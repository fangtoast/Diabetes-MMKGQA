from __future__ import annotations

import hashlib
from pathlib import Path

from diabetes_mmkgqa_starter.ingestion.diakg_parser import (
    DiakgParseOutputs,
    export_diakg_interim_outputs,
    parse_diakg,
    parse_diakg_records,
)


def _md5_hex(path: Path) -> str:
    hasher = hashlib.md5()
    hasher.update(path.read_bytes())
    return hasher.hexdigest()


def test_parse_diakg_deterministic_and_relations():
    repo_root = Path(__file__).resolve().parents[1]
    first: DiakgParseOutputs = parse_diakg(repo_root, source_id="manual_diakg_fallback")
    second: DiakgParseOutputs = parse_diakg(repo_root, source_id="manual_diakg_fallback")

    assert first.nodes == second.nodes
    assert first.edges == second.edges
    assert first.documents == second.documents
    assert first.evidence == second.evidence
    assert first.stats["node_count"] == len(first.nodes)
    assert first.stats["edge_count"] == len(first.edges)
    assert first.stats["evidence_count"] == len(first.evidence)
    assert first.stats["document_count"] == len(first.documents)

    assert any(edge["relation"] == "HAS_SYMPTOM" for edge in first.edges)
    assert any(edge["raw_relation"] in {"HAS_SYMPTOM", "HAS_CAUSE", "MENTIONED_IN"} for edge in first.edges)
    assert all(edge["knowledge_layer"] in {"A", "B", "C"} for edge in first.edges)
    assert all(node["node_id"] for node in first.nodes)
    assert all(edge["source_id"] in {"diakg", "manual_diakg_fallback"} for edge in first.edges)
    assert all(edge["evidence_id"] for edge in first.edges)


def test_parse_diakg_records_and_export_repeatable(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]
    source_path = repo_root / "data" / "raw" / "diakg" / "diakg_fixture.json"
    source_id = "manual_diakg_fallback"
    payload = __import__("json").loads(source_path.read_text(encoding="utf-8-sig"))
    with open(repo_root / "configs" / "ontology.yaml", "r", encoding="utf-8-sig") as f:
        import yaml

        relation_mapping = yaml.safe_load(f).get("raw_relation_mapping", {})
    parsed = parse_diakg_records(payload, source_id, relation_mapping)

    assert parsed.nodes
    assert parsed.edges
    assert parsed.documents
    assert parsed.evidence

    node_types = {node["node_type"] for node in parsed.nodes}
    assert "Document" in node_types
    assert "EvidenceChunk" in node_types
    assert any(node["canonical_name"] == "diakg_doc_001" for node in parsed.nodes) or any(
        node["source_ids"] in {"manual_diakg_fallback"} for node in parsed.nodes
    )

    out1 = export_diakg_interim_outputs(parsed, tmp_path / "run1")
    out2 = export_diakg_interim_outputs(parsed, tmp_path / "run2")
    for key in ("nodes", "edges", "documents", "evidence"):
        assert out1[key].exists()
        assert out2[key].exists()
        assert _md5_hex(out1[key]) == _md5_hex(out2[key]), f"{key} export must be repeatable"
