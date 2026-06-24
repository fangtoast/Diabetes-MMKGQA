from __future__ import annotations

import hashlib
from pathlib import Path

from diabetes_mmkgqa_starter import graph_builder


def _md5(path: Path) -> str:
    hasher = hashlib.md5()
    hasher.update(path.read_bytes())
    return hasher.hexdigest()


def _run_build(repo_root: Path, out_dir: Path, **kwargs):
    return graph_builder.build_graph_outputs(
        repo_root=repo_root,
        output_dir=out_dir,
        **kwargs,
    )


def test_graph_build_outputs_reproducible_without_raw_multimodal(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]

    out1 = _run_build(repo_root, tmp_path / "run1", include_retina=False, include_pneumonia=False)
    out2 = _run_build(repo_root, tmp_path / "run2", include_retina=False, include_pneumonia=False)

    expected = {
        "nodes_csv",
        "nodes_parquet",
        "edges_csv",
        "edges_parquet",
        "triples_tsv",
        "documents_csv",
        "documents_parquet",
        "evidence_csv",
        "evidence_parquet",
        "images_csv",
        "images_parquet",
        "schema_json",
        "stats_json",
        "graphml",
    }
    assert set(out1.output_files.keys()) == expected
    assert set(out2.output_files.keys()) == expected

    for key in expected:
        assert out1.output_files[key].exists()
        assert out2.output_files[key].exists()

    # deterministic export check
    for key in expected:
        assert _md5(out1.output_files[key]) == _md5(out2.output_files[key]), f"{key} must be repeatable"

    assert out1.stats["node_count"] == len(out1.nodes)
    assert out1.stats["edge_count"] == len(out1.edges)
    assert out1.stats["canonical_entity_count"] > 0
    assert out1.stats["unique_semantic_triples_count"] > 0
    assert out1.stats["image_node_count"] == len([n for n in out1.nodes if n.get("node_type") == "Image"])
    assert out1.stats["node_layer_counts"].get("C", 0) >= 1
    assert "A" in out1.stats["edge_layer_counts"]


def test_graph_stats_include_layer_counts_and_provenance(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]

    result = graph_builder.build_graph_outputs(
        repo_root=repo_root,
        output_dir=tmp_path / "run",
        include_retina=False,
        include_pneumonia=False,
    )

    stats = result.stats
    assert "edge_layer_counts" in stats
    assert "node_layer_counts" in stats
    assert "layered_statistics" in stats
    assert "schema_validation" in stats
    assert "provenance_edge_count" in stats
    assert stats["provenance_edge_count"] >= 0
    assert stats["schema_validation"]["relation_violations"] is not None
    assert stats["layered_statistics"]["layer_counts"]["node"] == stats["node_layer_counts"]
    assert stats["layered_statistics"]["layer_counts"]["edge"] == stats["edge_layer_counts"]
    assert "A" in stats["layered_statistics"]["layer_breakdown"]
    assert "B" in stats["layered_statistics"]["layer_breakdown"]
    assert "C" in stats["layered_statistics"]["layer_breakdown"]
    b_layer = stats["layered_statistics"]["layer_breakdown"]["B"]
    c_layer = stats["layered_statistics"]["layer_breakdown"]["C"]

    assert b_layer["icd_code_count"] == len([node for node in result.nodes if node.get("node_type") == "ICD_Code"])
    assert b_layer["guideline_count"] == len([node for node in result.nodes if node.get("node_type") == "Guideline"])
    assert b_layer["standard_rule_count"] == len([node for node in result.nodes if node.get("node_type") == "StandardRule"])
    assert b_layer["reference_range_count"] == len([node for node in result.nodes if node.get("node_type") == "ReferenceRange"])
    assert c_layer["disease_count"] == len([node for node in result.nodes if node.get("node_type") == "Disease"])
    assert c_layer["image_node_count"] == len([node for node in result.nodes if node.get("node_type") == "Image"])
    assert c_layer["multimodal_edge_count"] == len(
        [
            edge
            for edge in result.edges
            if edge.get("relation") in {"IMAGE_ASSOCIATED_WITH", "HAS_IMAGE_GRADE", "FROM_DATASET", "IN_SPLIT"}
        ]
    )


def test_graph_quality_gate_has_expected_fields(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]

    result = graph_builder.build_graph_outputs(
        repo_root=repo_root,
        output_dir=tmp_path / "run",
        include_retina=False,
        include_pneumonia=False,
    )

    schema = result.schema
    stats = result.stats

    assert "quality_gate" in schema
    assert "quality_gate" in stats
    assert "duplicate_node_ids" in schema["quality_gate"]
    assert "duplicate_edge_ids" in schema["quality_gate"]
    assert "self_loops" in schema["quality_gate"]
    assert "missing_endpoints" in schema["quality_gate"]
    assert "relation_violations" in schema["quality_gate"]
    assert "image_path_violations" in schema["quality_gate"]
    assert isinstance(schema["quality_gate"]["duplicate_node_ids"], list)
    assert isinstance(schema["quality_gate"]["duplicate_edge_ids"], list)
    assert isinstance(schema["quality_gate"]["self_loops"], list)
    assert isinstance(schema["quality_gate"]["missing_endpoints"], list)
    assert isinstance(schema["quality_gate"]["relation_violations"], list)
    assert isinstance(schema["quality_gate"]["image_path_violations"], list)

    # deterministic quality checks for current built graph
    assert stats["quality_gate"]["missing_endpoints"] == []
    assert stats["quality_gate"]["self_loops"] == []
    assert stats["quality_gate"]["image_path_violations"] == []
    assert len(stats["quality_gate"]["duplicate_node_ids"]) == 0
    assert len(stats["quality_gate"]["duplicate_edge_ids"]) == 0
    assert stats["quality_gate"]["passed"] is True
    assert len(stats["quality_gate"]["relation_violations"]) == 0
