from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import json

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
