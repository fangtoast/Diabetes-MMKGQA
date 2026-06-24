from __future__ import annotations

from pathlib import Path
from typing import Any

from diabetes_mmkgqa_starter.db import PortableGraphBackend
from diabetes_mmkgqa_starter.qa import IntentRouter, QAService
import yaml


def _write_csv(path: Path, rows: list[dict[str, Any]], *, fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        if fieldnames is None:
            fieldnames = []
        with path.open("w", encoding="utf-8-sig", newline="") as f:
            if fieldnames:
                f.write(",".join(fieldnames) + "\n")
            return

    fieldnames = fieldnames or sorted({k for row in rows for k in row.keys()})
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        f.write(",".join(fieldnames) + "\n")
        for row in rows:
            values = [str(row.get(col, "")) for col in fieldnames]
            f.write(",".join(values) + "\n")


def _build_portable_fixture(processed_dir: Path) -> None:
    _write_csv(
        processed_dir / "nodes.csv",
        [
            {
                "node_id": "n1",
                "node_type": "Disease",
                "canonical_name": "diabetes",
                "knowledge_layer": "C",
                "source_ids": "manual",
                "kg_version": "0.2.0",
            },
            {
                "node_id": "n2",
                "node_type": "Symptom",
                "canonical_name": "thirst",
                "knowledge_layer": "A",
                "source_ids": "manual",
                "kg_version": "0.2.0",
            },
            {
                "node_id": "n3",
                "node_type": "Symptom",
                "canonical_name": "blurred vision",
                "knowledge_layer": "A",
                "source_ids": "manual",
                "kg_version": "0.2.0",
            },
            {
                "node_id": "n4",
                "node_type": "Image",
                "canonical_name": "retina image 1",
                "knowledge_layer": "C",
                "source_ids": "retina",
                "kg_version": "0.2.0",
            },
            {
                "node_id": "n5",
                "node_type": "ImageGrade",
                "canonical_name": "No_DR",
                "knowledge_layer": "C",
                "source_ids": "retina",
                "kg_version": "0.2.0",
            },
            {
                "node_id": "n6",
                "node_type": "Dataset",
                "canonical_name": "RetinaMNIST+",
                "knowledge_layer": "C",
                "source_ids": "retina",
                "kg_version": "0.2.0",
            },
            {
                "node_id": "n7",
                "node_type": "DataSplit",
                "canonical_name": "train",
                "knowledge_layer": "C",
                "source_ids": "retina",
                "kg_version": "0.2.0",
            },
        ],
        fieldnames=["node_id", "node_type", "canonical_name", "knowledge_layer", "source_ids", "kg_version"],
    )

    _write_csv(
        processed_dir / "edges.csv",
        [
            {
                "head_id": "n1",
                "tail_id": "n2",
                "edge_id": "e1",
                "relation": "HAS_SYMPTOM",
                "source_id": "manual",
                "extraction_method": "manual",
                "confidence": "1.0",
                "knowledge_layer": "A",
                "kg_version": "0.2.0",
            },
            {
                "head_id": "n1",
                "tail_id": "n3",
                "edge_id": "e2",
                "relation": "HAS_SYMPTOM",
                "source_id": "manual",
                "extraction_method": "manual",
                "confidence": "1.0",
                "knowledge_layer": "A",
                "kg_version": "0.2.0",
                "evidence_id": "ev2",
                "raw_relation": "HAS_SYMPTOM",
                "normalized_relation": "HAS_SYMPTOM",
            },
            {
                "head_id": "n4",
                "tail_id": "n1",
                "edge_id": "e3",
                "relation": "IMAGE_ASSOCIATED_WITH",
                "source_id": "retina",
                "extraction_method": "manual",
                "confidence": "1.0",
                "knowledge_layer": "C",
                "kg_version": "0.2.0",
                "evidence_id": "ev3",
                "raw_relation": "IMAGE_ASSOCIATED_WITH",
                "normalized_relation": "IMAGE_ASSOCIATED_WITH",
            },
            {
                "head_id": "n4",
                "tail_id": "n5",
                "edge_id": "e4",
                "relation": "HAS_IMAGE_GRADE",
                "source_id": "retina",
                "extraction_method": "manual",
                "confidence": "1.0",
                "knowledge_layer": "C",
                "kg_version": "0.2.0",
                "evidence_id": "ev3",
                "raw_relation": "HAS_IMAGE_GRADE",
                "normalized_relation": "HAS_IMAGE_GRADE",
            },
            {
                "head_id": "n4",
                "tail_id": "n6",
                "edge_id": "e5",
                "relation": "FROM_DATASET",
                "source_id": "retina",
                "extraction_method": "manual",
                "confidence": "1.0",
                "knowledge_layer": "C",
                "kg_version": "0.2.0",
                "evidence_id": "ev3",
                "raw_relation": "FROM_DATASET",
                "normalized_relation": "FROM_DATASET",
            },
            {
                "head_id": "n4",
                "tail_id": "n7",
                "edge_id": "e6",
                "relation": "IN_SPLIT",
                "source_id": "retina",
                "extraction_method": "manual",
                "confidence": "1.0",
                "knowledge_layer": "C",
                "kg_version": "0.2.0",
                "evidence_id": "ev3",
                "raw_relation": "IN_SPLIT",
                "normalized_relation": "IN_SPLIT",
            },
        ],
        fieldnames=[
            "head_id",
            "tail_id",
            "edge_id",
            "relation",
            "source_id",
            "extraction_method",
            "confidence",
            "knowledge_layer",
            "kg_version",
            "evidence_id",
            "raw_relation",
            "normalized_relation",
        ],
    )

    _write_csv(
        processed_dir / "images.csv",
        [
            {
                "image_id": "n4",
                "relative_path": "data/interim/retina/retina_000001.bin",
                "dataset": "RetinaMNIST+",
                "split": "train",
                "grade": "No_DR",
                "kg_version": "0.2.0",
            }
        ],
        fieldnames=["image_id", "relative_path", "dataset", "split", "grade", "kg_version"],
    )


def _write_intent_contract(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")


def _build_backend_with_contract(tmp_path: Path) -> tuple[PortableGraphBackend, Path]:
    processed = tmp_path / "data" / "processed"
    _build_portable_fixture(processed)

    intents_file = tmp_path / "intents.yaml"
    return PortableGraphBackend.from_dir(processed), intents_file


def test_intent_router_prefers_longer_trigger(tmp_path: Path):
    intents_path = tmp_path / "intents.yaml"
    _write_intent_contract(
        intents_path,
        {
            "intents": [
                {
                    "name": "short_match",
                    "description": "short",
                    "entity_types": ["Disease"],
                    "relations": ["HAS_SYMPTOM"],
                    "triggers": ["symptom"],
                },
                {
                    "name": "long_match",
                    "description": "long",
                    "entity_types": ["Disease"],
                    "relations": ["HAS_SYMPTOM"],
                    "triggers": ["common symptoms"],
                },
            ],
            "fallback": {"max_rows": 20, "max_hops": 2},
        },
    )
    router = IntentRouter.from_file(intents_path)
    match = router.route("list common symptoms")
    assert match is not None
    assert match.intent.name == "long_match"


def test_qa_service_a_layer_symptom_question_has_evidence_and_metadata(tmp_path: Path):
    backend, intents_path = _build_backend_with_contract(tmp_path)
    _write_intent_contract(
        intents_path,
        {
            "intents": [
                {
                    "name": "disease_symptoms",
                    "description": "symptoms",
                    "entity_types": ["Disease"],
                    "relations": ["HAS_SYMPTOM"],
                    "triggers": ["symptom", "symptoms"],
                }
            ],
            "fallback": {"max_rows": 20, "max_hops": 2},
        },
    )

    service = QAService(backend=backend, intents_path=intents_path)
    result = service.ask("What are symptoms of diabetes?")

    assert result["status"] == "ok"
    assert result["entity"]["canonical_name"] == "diabetes"
    assert result["evidence_ids"] == ["ev2"]
    assert result["source_ids"] == ["manual"]
    assert result["kg_version"] == "0.2.0"
    assert "课程演示、非临床诊断" in result["safety_notice"]
    assert len(result["rows"]) == 2
    assert result["metadata"]["relation_count"] == 2
    assert result["metadata"]["image_count"] == 0


def test_qa_service_ambiguous_entity_returns_clarification(tmp_path: Path):
    processed = tmp_path / "data" / "processed"
    _write_csv(
        processed / "nodes.csv",
        [
            {
                "node_id": "d1",
                "node_type": "Disease",
                "canonical_name": "diabetes",
                "knowledge_layer": "C",
                "source_ids": "manual",
                "kg_version": "0.2.0",
            },
            {
                "node_id": "d2",
                "node_type": "Disease",
                "canonical_name": "diabetes type 2",
                "knowledge_layer": "C",
                "source_ids": "manual",
                "kg_version": "0.2.0",
            },
        ],
        fieldnames=["node_id", "node_type", "canonical_name", "knowledge_layer", "source_ids", "kg_version"],
    )
    _write_csv(
        processed / "edges.csv",
        [
            {
                "head_id": "d1",
                "tail_id": "d2",
                "edge_id": "e1",
                "relation": "HAS_CLASS",
                "source_id": "manual",
                "extraction_method": "manual",
                "confidence": "1.0",
                "knowledge_layer": "A",
                "kg_version": "0.2.0",
            }
        ],
        fieldnames=[
            "head_id",
            "tail_id",
            "edge_id",
            "relation",
            "source_id",
            "extraction_method",
            "confidence",
            "knowledge_layer",
            "kg_version",
        ],
    )
    _write_csv(processed / "images.csv", [], fieldnames=["image_id", "relative_path", "kg_version"])

    intents_file = tmp_path / "intents.yaml"
    _write_intent_contract(
        intents_file,
        {
            "intents": [
                {
                    "name": "disease_symptoms",
                    "description": "symptoms",
                    "entity_types": ["Disease"],
                    "relations": ["HAS_SYMPTOM"],
                    "triggers": ["symptom", "symptoms"],
                }
            ],
            "fallback": {"max_rows": 20, "max_hops": 2},
        },
    )
    service = QAService(backend=PortableGraphBackend.from_dir(processed), intents_path=intents_file)
    result = service.ask("symptoms of diabetes?")

    assert result["status"] == "clarification"
    assert len(result["metadata"]["candidates"]) == 2
    assert result["metadata"]["candidates"][0]["canonical_name"] in {"diabetes", "diabetes type 2"}
    assert "课程演示、非临床诊断" in result["safety_notice"]
    assert result["source_ids"] == ["manual"]
    assert result["metadata"]["candidate_count"] == 2


def test_qa_service_image_intent_returns_image_candidates(tmp_path: Path):
    backend, intents_path = _build_backend_with_contract(tmp_path)
    _write_intent_contract(
        intents_path,
        {
            "intents": [
                {
                    "name": "image_examples_by_disease",
                    "description": "image examples",
                    "entity_types": ["Disease"],
                    "relations": ["IMAGE_ASSOCIATED_WITH"],
                    "triggers": ["image", "images", "retina"],
                }
            ],
            "fallback": {"max_rows": 20, "max_hops": 2},
        },
    )

    service = QAService(backend=backend, intents_path=intents_path)
    result = service.ask("show disease images for diabetes")

    assert result["status"] == "ok"
    assert len(result["images"]) == 1
    assert result["images"][0]["image_id"] == "n4"
    assert result["rows"][0]["relation"] == "IMAGE_ASSOCIATED_WITH"
    assert result["source_ids"] == ["manual", "retina"]
    assert result["evidence_ids"] == ["ev3"]
    assert result["metadata"]["image_count"] == 1


def test_qa_service_not_found_returns_contract_fields(tmp_path: Path):
    processed = tmp_path / "data" / "processed"
    _write_csv(
        processed / "nodes.csv",
        [
            {
                "node_id": "d1",
                "node_type": "Disease",
                "canonical_name": "diabetes",
                "knowledge_layer": "C",
                "source_ids": "manual",
                "kg_version": "0.2.0",
            }
        ],
        fieldnames=["node_id", "node_type", "canonical_name", "knowledge_layer", "source_ids", "kg_version"],
    )
    _write_csv(processed / "edges.csv", [], fieldnames=[
        "head_id",
        "tail_id",
        "edge_id",
        "relation",
        "source_id",
        "extraction_method",
        "confidence",
        "knowledge_layer",
        "kg_version",
        "evidence_id",
        "raw_relation",
        "normalized_relation",
    ])
    _write_csv(processed / "images.csv", [], fieldnames=["image_id", "relative_path", "kg_version"])

    intents_file = tmp_path / "intents.yaml"
    _write_intent_contract(
        intents_file,
        {
            "intents": [
                {
                    "name": "disease_symptoms",
                    "description": "symptoms",
                    "entity_types": ["Disease"],
                    "relations": ["HAS_SYMPTOM"],
                    "triggers": ["symptom", "symptoms"],
                }
            ],
            "fallback": {"max_rows": 20, "max_hops": 2},
        },
    )
    service = QAService(backend=PortableGraphBackend.from_dir(processed), intents_path=intents_file)
    result = service.ask("What are symptoms of diabetes?")

    assert result["status"] == "not_found"
    assert result["evidence_ids"] == []
    assert result["source_ids"] == ["manual"]
    assert result["kg_version"] == "0.2.0"
    assert "课程演示、非临床诊断" in result["safety_notice"]
    assert "未能在当前知识库中找到关于 diabetes 的 disease_symptoms 信息" in result["answer"]
