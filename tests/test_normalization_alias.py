from __future__ import annotations

import hashlib
from pathlib import Path

from diabetes_mmkgqa_starter.normalization import alias_loader


def _md5_bytes(path: Path) -> str:
    hasher = hashlib.md5()
    hasher.update(path.read_bytes())
    return hasher.hexdigest()


def _alias_rows() -> list[dict]:
    return [
        {
            "canonical_name": "糖尿病",
            "alias": "Diabetes",
            "node_type": "Disease",
            "reviewer": "Team",
            "note": "A-layer synonym",
        },
        {
            "canonical_name": "糖尿病",
            "alias": "diabetes",
            "node_type": "Disease",
            "reviewer": "Team",
            "note": "normalized case",
        },
        {
            "canonical_name": "胸片",
            "alias": "X-ray",
            "node_type": "Image",
            "reviewer": "Team",
            "note": "C-layer synonym",
        },
        {
            "canonical_name": "发热",
            "alias": "Fever",
            "node_type": "Symptom",
            "reviewer": "Team",
            "note": "symptom alias",
        },
        {
            "canonical_name": "视网膜",
            "alias": "Fever",
            "node_type": "TestItem",
            "reviewer": "Team",
            "note": "same alias, different type",
        },
    ]


def test_parse_alias_rows_and_index_are_deterministic():
    alias_rows = _alias_rows()
    source_id = "manual_aliases"

    first_aliases = alias_loader.parse_alias_rows(alias_rows, source_id=source_id)
    second_aliases = alias_loader.parse_alias_rows(alias_rows, source_id=source_id)
    assert first_aliases == second_aliases
    assert len(first_aliases) == 5

    first_index = alias_loader.build_alias_index(first_aliases)
    second_index = alias_loader.build_alias_index(second_aliases)
    assert first_index == second_index
    assert first_index[("Disease", "diabetes")] == "糖尿病"

    normal = alias_loader.canonicalize_entity_name(first_index, "diabetes", "Disease")
    assert normal == "糖尿病"


def test_no_cross_type_merge_by_node_type():
    alias_rows = _alias_rows()
    alias_index = alias_loader.build_alias_index(alias_loader.parse_alias_rows(alias_rows, source_id="manual_aliases"))

    # same alias text but different node_type should not cross-map
    assert alias_loader.canonicalize_entity_name(alias_index, "Fever", "Symptom") == "发热"
    assert alias_loader.canonicalize_entity_name(alias_index, "Fever", "TestItem") == "视网膜"


def test_normalize_entity_records_and_export_repeatable(tmp_path: Path):
    alias_rows = alias_loader.parse_alias_rows(_alias_rows(), source_id="manual_aliases")
    alias_index = alias_loader.build_alias_index(alias_rows)
    entities = [
        {"canonical_name": "", "node_type": "Disease", "alias_name": "DIABETES", "source_id": "manual_aliases"},
        {"canonical_name": "X-ray", "node_type": "Image", "alias_name": "X-RAY", "source_id": "manual_aliases"},
        {"canonical_name": "未知实体", "node_type": "Disease", "alias_name": "", "source_id": "manual_aliases"},
    ]
    normalized = alias_loader.normalize_entity_records(entities, alias_index)

    disease_from_alias = next(item for item in normalized if item["alias_name"] == "DIABETES")
    image_from_alias = next(item for item in normalized if item["alias_name"] == "X-RAY")
    passthrough = next(item for item in normalized if item["canonical_name"] == "未知实体")
    assert disease_from_alias["canonical_name"] == "糖尿病"
    assert disease_from_alias["canonicalized_from_alias"] == "1"
    assert image_from_alias["canonical_name"] == "胸片"
    assert image_from_alias["canonicalized_from_alias"] == "0"
    assert passthrough["canonical_name"] == "未知实体"
    assert passthrough["canonicalized_from_alias"] == "0"

    parsed = alias_loader.AliasLoadOutputs(
        aliases=alias_rows,
        alias_index=alias_index,
        stats={
            "alias_count": len(alias_rows),
            "canonical_node_count": len(alias_rows),
            "alias_type_count": 3,
            "kg_version": "0.2.0",
        },
    )
    out1 = alias_loader.export_alias_outputs(parsed, tmp_path / "run1")
    out2 = alias_loader.export_alias_outputs(parsed, tmp_path / "run2")

    assert set(out1.keys()) == {"aliases", "alias_index"}
    assert set(out2.keys()) == {"aliases", "alias_index"}
    for key in ("aliases", "alias_index"):
        assert out1[key].exists()
        assert out2[key].exists()
        assert _md5_bytes(out1[key]) == _md5_bytes(out2[key]), f"{key} export must be repeatable"
