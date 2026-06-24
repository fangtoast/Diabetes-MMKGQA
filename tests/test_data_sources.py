from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import json
import csv
import hashlib

import yaml



def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_medmnist_manifest_checksums_present():
    manifest_path = _repo_root() / "data" / "source_manifest.yaml"
    with manifest_path.open("r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)

    sources = {item["source_id"]: item for item in manifest["sources"]}

    assert sources["retinamnist"]["checksum"].startswith("md5:")
    assert sources["retinamnist"]["checksum"] == "md5:eae7e3b6f3fcbda4ae613ebdcbe35348"
    assert sources["pneumoniamnist"]["checksum"].startswith("md5:")
    assert sources["pneumoniamnist"]["checksum"] == "md5:d6a3c71de1b945ea11211b03746c1fe1"
    assert sources["retinamnist"]["acquisition"].startswith("Download from official")
    assert sources["pneumoniamnist"]["acquisition"].startswith("Download from official")


def test_fetch_medmnist_dry_run_script():
    script = _repo_root() / "scripts" / "fetch_medmnist.py"
    result = subprocess.run(
        [sys.executable, str(script), "--dataset", "all", "--dry-run"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 0
    out = result.stdout
    assert "retinamnist" in out
    assert "pneumoniamnist" in out
    assert "DRY-RUN" in out


def test_diakg_fallback_fixture_schema():
    manifest_path = _repo_root() / "data" / "source_manifest.yaml"
    fixture_path = _repo_root() / "data" / "raw" / "diakg" / "diakg_fixture.json"

    with manifest_path.open("r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)
    sources = {item["source_id"]: item for item in manifest["sources"]}
    assert sources["manual_diakg_fallback"]["checksum"] == "md5:6fa2487c214e7a2c288f901440c5014d"
    assert fixture_path.exists()

    with fixture_path.open("r", encoding="utf-8-sig") as f:
        payload = json.load(f)
    assert "documents" in payload
    assert isinstance(payload["documents"], list)
    assert payload["documents"], "fixture must contain at least one document"

    doc = payload["documents"][0]
    assert "paragraphs" in doc
    assert doc["paragraphs"]


def test_fetch_diakg_dry_run_script():
    script = _repo_root() / "scripts" / "fetch_diakg.py"
    result = subprocess.run(
        [sys.executable, str(script), "--dry-run"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 0
    out = result.stdout
    assert "diakg" in out
    assert "fallback_fixture" in out


def _md5_hex(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return f"md5:{h.hexdigest()}"


def test_manual_csvs_exist_and_schema_and_checksums():
    root = _repo_root() / "data" / "source_manifest.yaml"
    with root.open("r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)
    source_map = {item["source_id"]: item for item in manifest["sources"]}

    rows = [
        ("manual_a_general_terms", "a_general_terms.csv", ["canonical_name", "node_type", "synonyms", "description"]),
        ("manual_b_icd10_subset", "b_icd10_subset.csv", ["disease_name", "icd_code", "disease_layer", "note"]),
        ("manual_b_guideline_rules", "b_guideline_rules.csv", ["disease_name", "rule_type", "code", "value", "unit", "source_ref", "comments"]),
        ("manual_c_hypertension_rules", "c_hypertension_rules.csv", ["rule_name", "disease_name", "finding", "severity", "recommendation", "source"]),
        ("manual_aliases", "aliases.csv", ["canonical_name", "alias", "node_type", "reviewer", "note"]),
    ]

    for source_id, filename, required in rows:
        src = source_map[source_id]
        path = _repo_root() / src["root_file"]
        assert path.exists(), f"{filename} must exist"
        assert _md5_hex(path) == src["checksum"], f"{filename} checksum mismatch"

        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            assert reader.fieldnames is not None
            assert set(required).issubset(set(reader.fieldnames))
            data_rows = list(reader)
            assert data_rows, f"{filename} must contain at least one row"
