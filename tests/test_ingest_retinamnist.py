from __future__ import annotations

import hashlib
from pathlib import Path

from diabetes_mmkgqa_starter.ingestion import retinamnist_parser


def _md5_bytes(path: Path) -> str:
    hasher = hashlib.md5()
    hasher.update(path.read_bytes())
    return hasher.hexdigest()


def _fixture_payload() -> dict:
    return {
        "train_images": [
            [[0], [0], [0]],
            [[1], [1], [1]],
        ],
        "train_labels": [0, 1],
        "val_images": [
            [[2], [2], [2]],
            [[3], [3], [3]],
        ],
        "val_labels": [2, 3],
        "test_images": [
            [[4], [4], [4]],
            [[5], [5], [5]],
        ],
        "test_labels": [4, 0],
    }


def test_parse_retinamnist_records_is_deterministic():
    payload = _fixture_payload()
    first = retinamnist_parser.parse_retinamnist_records(payload, source_id="retinamnist")
    second = retinamnist_parser.parse_retinamnist_records(payload, source_id="retinamnist")

    assert first.nodes == second.nodes
    assert first.edges == second.edges
    assert first.images == second.images
    assert first.stats["node_count"] == len(first.nodes)
    assert first.stats["edge_count"] == len(first.edges)
    assert first.stats["image_count"] == len(first.images)

    expected_image_count = 2 + 2 + 2
    assert first.stats["image_count"] == expected_image_count
    assert any(node["node_type"] == "Image" for node in first.nodes)
    assert any(node["node_type"] == "ImageGrade" for node in first.nodes)
    assert any(node["node_type"] == "DataSplit" for node in first.nodes)
    assert any(edge["relation"] == "IMAGE_ASSOCIATED_WITH" for edge in first.edges)
    assert any(edge["relation"] == "HAS_IMAGE_GRADE" for edge in first.edges)
    assert any(edge["relation"] == "FROM_DATASET" for edge in first.edges)
    assert any(edge["relation"] == "IN_SPLIT" for edge in first.edges)
    assert all(edge["source_id"] == "retinamnist" for edge in first.edges)
    assert all(edge["knowledge_layer"] == "C" for edge in first.edges)
    assert all(edge["extraction_method"] == "retinamnist_parser" for edge in first.edges)
    assert all(edge["evidence_id"] for edge in first.edges)
    assert all("grade" in row for row in first.images)

    assert any(row["grade_code"] == "4" for row in first.images)
    assert any(row["split"] == "train" for row in first.images)
    assert any(row["split"] == "val" for row in first.images)
    assert any(row["split"] == "test" for row in first.images)


def test_parse_retinamnist_export_repeatable(tmp_path: Path):
    parsed = retinamnist_parser.parse_retinamnist_records(_fixture_payload(), source_id="retinamnist")
    out1 = retinamnist_parser.export_retinamnist_interim_outputs(parsed, tmp_path / "run1")
    out2 = retinamnist_parser.export_retinamnist_interim_outputs(parsed, tmp_path / "run2")

    expected = {"nodes", "edges", "images"}
    assert set(out1.keys()) == expected
    assert set(out2.keys()) == expected

    for key in expected:
        assert out1[key].exists()
        assert out2[key].exists()
        assert _md5_bytes(out1[key]) == _md5_bytes(out2[key]), f"{key} export must be repeatable"
