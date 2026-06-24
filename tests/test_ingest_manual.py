from __future__ import annotations

import hashlib
from pathlib import Path

from diabetes_mmkgqa_starter.ingestion.manual_ab_tables import (
    ManualParseOutputs,
    export_manual_interim_outputs,
    parse_manual_sources,
)


def _md5_bytes(path: Path) -> str:
    hasher = hashlib.md5()
    hasher.update(path.read_bytes())
    return hasher.hexdigest()


def test_ingest_manual_parsing_is_deterministic(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]
    first: ManualParseOutputs = parse_manual_sources(repo_root=repo_root)
    second: ManualParseOutputs = parse_manual_sources(repo_root=repo_root)

    assert first.nodes == second.nodes
    assert first.edges == second.edges
    assert first.aliases == second.aliases
    assert first.stats["node_count"] == len(first.nodes)
    assert first.stats["edge_count"] == len(first.edges)

    assert any(node["node_type"] == "Disease" for node in first.nodes)
    assert any(node["node_type"] == "ICD_Code" for node in first.nodes)
    assert any(node["node_type"] == "StandardRule" for node in first.nodes)
    assert any(edge["relation"] == "HAS_ICD_CODE" for edge in first.edges)
    assert any(edge["relation"] == "APPLIES_TO" for edge in first.edges)
    assert all(node["node_id"] for node in first.nodes)
    assert all(edge["source_id"].startswith("manual_") for edge in first.edges)
    assert all(node["knowledge_layer"] in {"A", "B", "C"} for node in first.nodes)
    assert all(edge["extraction_method"] == "manual" for edge in first.edges)
    assert all(edge["knowledge_layer"] in {"A", "B", "C"} for edge in first.edges)


def test_ingest_manual_export_repeatable(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]
    parsed = parse_manual_sources(repo_root=repo_root)

    out_dir1 = tmp_path / "run1"
    out_dir2 = tmp_path / "run2"
    files1 = export_manual_interim_outputs(parsed, out_dir1)
    files2 = export_manual_interim_outputs(parsed, out_dir2)

    expected = {"nodes", "edges", "aliases"}
    assert set(files1.keys()) == expected
    assert set(files2.keys()) == expected

    for key in expected:
        assert files1[key].exists()
        assert files2[key].exists()
        assert _md5_bytes(files1[key]) == _md5_bytes(files2[key]), f"{key} export must be repeatable"