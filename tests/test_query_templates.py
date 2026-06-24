from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from diabetes_mmkgqa_starter.qa import IntentRouter
from diabetes_mmkgqa_starter.qa.query_templates import (
    QAQueryTemplateError,
    build_subgraph_query,
    validate_query_payload,
)


def _write_intent_contract(path: Path, payload: dict[str, object]) -> None:
    path.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")


def _match(tmp_path: Path) -> tuple[object, str]:
    intents_path = tmp_path / "intents.yaml"
    _write_intent_contract(
        intents_path,
        {
            "intents": [
                {
                    "name": "disease_symptoms",
                    "description": "symptoms",
                    "entity_types": ["Disease"],
                    "relations": ["HAS_SYMPTOM", "RECOMMENDS_TEST"],
                    "triggers": ["symptom", "symptoms"],
                }
            ],
            "fallback": {"max_rows": 20, "max_hops": 2},
        },
    )

    router = IntentRouter.from_file(intents_path)
    match = router.route("what are symptoms of diabetes?")
    assert match is not None
    return match, "0a7b4e4d"


def test_build_subgraph_query_is_parameterized_and_read_only(tmp_path: Path) -> None:
    match, node_id = _match(tmp_path)
    query_template = build_subgraph_query(intent_match=match, node_id=node_id, max_hops=3)

    validate_query_payload(query_template)

    assert query_template.read_only is True
    assert query_template.name == "subgraph_by_node"
    assert "MATCH" in query_template.query
    assert "$node_id" in query_template.query
    assert "$relations" in query_template.query
    assert "$max_hops" in query_template.query
    assert query_template.parameters["max_hops"] == 3
    assert query_template.parameters["relations"] == ["HAS_SYMPTOM", "RECOMMENDS_TEST"]
    assert query_template.max_hops == 3
    assert query_template.to_payload()["read_only"] is True


def test_build_subgraph_query_rejects_bad_node_id(tmp_path: Path) -> None:
    match, _ = _match(tmp_path)

    with pytest.raises(QAQueryTemplateError):
        build_subgraph_query(intent_match=match, node_id="bad' OR 1=1", max_hops=2)

    with pytest.raises(QAQueryTemplateError):
        build_subgraph_query(intent_match=match, node_id="", max_hops=2)


def test_query_template_is_not_raw_user_query(tmp_path: Path) -> None:
    match, node_id = _match(tmp_path)
    raw_question = "show symptoms of diabetes'; DELETE (n)-[r]->() //"
    template = build_subgraph_query(intent_match=match, node_id=node_id, max_hops=2)

    assert raw_question not in template.query
    assert "$node_id" in template.query
    assert "$relations" in template.query
    assert "DELETE" not in template.query


def test_validate_query_payload_blocks_user_query_template_abuse() -> None:
    bad_payload = type(
        "Q",
        (),
        {
            "query": "MATCH (n) RETURN n {node_id}",
            "parameters": {"node_id": "abc"},
            "read_only": True,
            "allowed_relations": (),
        },
    )()

    with pytest.raises(QAQueryTemplateError):
        validate_query_payload(bad_payload)  # type: ignore[arg-type]

