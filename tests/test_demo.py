from __future__ import annotations

from pathlib import Path
import csv
import json
import os
import subprocess
import sys

from diabetes_mmkgqa_starter import demo


def _write_csv(path: Path, rows: list[dict], *, fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        with path.open("w", encoding="utf-8-sig", newline="") as f:
            if fieldnames:
                f.write(",".join(fieldnames) + "\n")
            return

    fieldnames = fieldnames or sorted({k for row in rows for k in row.keys()})
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _build_demo_fixture(processed: Path) -> None:
    _write_csv(
        processed / "nodes.csv",
        [
            {
                "node_id": "n_disease",
                "node_type": "Disease",
                "canonical_name": "糖尿病",
                "knowledge_layer": "C",
                "source_ids": "manual",
                "kg_version": "0.2.0",
            },
            {
                "node_id": "n_symptom",
                "node_type": "Symptom",
                "canonical_name": "多饮",
                "knowledge_layer": "A",
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
                "head_id": "n_disease",
                "tail_id": "n_symptom",
                "edge_id": "e_symptom",
                "relation": "HAS_SYMPTOM",
                "source_id": "manual",
                "extraction_method": "manual",
                "confidence": "1.0",
                "knowledge_layer": "A",
                "kg_version": "0.2.0",
                "evidence_id": "ev1",
                "raw_relation": "HAS_SYMPTOM",
                "normalized_relation": "HAS_SYMPTOM",
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
            "evidence_id",
            "raw_relation",
            "normalized_relation",
        ],
    )
    _write_csv(processed / "images.csv", [])
    _write_csv(processed / "documents.csv", [])
    _write_csv(processed / "evidence.csv", [])


def test_run_demo_cases_generates_json_and_case_count(tmp_path: Path):
    processed = tmp_path / "data" / "processed"
    _build_demo_fixture(processed)
    out_dir = tmp_path / "docs" / "cases"
    screenshot_dir = tmp_path / "docs" / "screenshots"

    result = demo.run_demo_cases(
        repo_root=tmp_path,
        output_dir=out_dir,
        processed_dir=processed,
        intents_path=Path("configs") / "intents.yaml",
        screenshot_dir=screenshot_dir,
        output_json="demo_test.json",
        cases=[
            {
                "case_id": "DEMO-101",
                "title": "qa",
                "kind": "qa",
                "question": "症状 糖尿病",
                "note": "qa case",
            },
            {
                "case_id": "DEMO-102",
                "title": "graph",
                "kind": "graph",
                "question": "",
                "note": "graph case",
            },
            {
                "case_id": "DEMO-103",
                "title": "stats",
                "kind": "stats",
                "question": "",
                "note": "stats case",
            },
        ],
        capture_screenshots=False,
    )
    assert result["case_count"] == 3
    payload = json.loads((out_dir / "demo_test.json").read_text(encoding="utf-8"))
    assert payload["case_count"] == 3
    assert len(payload["cases"]) == 3
    assert payload["cases"][0]["status"] in {"ok", "clarification", "not_found"}
    assert payload["cases"][1]["case_id"] == "DEMO-102"
    assert payload["cases"][1]["status"] == "ok"


def test_cli_demo_command_writes_case_file(tmp_path: Path):
    processed = tmp_path / "data" / "processed"
    _build_demo_fixture(processed)

    repo_root = Path(__file__).resolve().parent.parent
    out_dir = tmp_path / "docs" / "cases"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "diabetes_mmkgqa_starter.cli",
            "--repo-root",
            str(tmp_path),
            "--processed-dir",
            str(processed),
            "--demo-output-dir",
            str(out_dir),
            "--demo-output-json",
            "cli_demo.json",
            "--intent-path",
            str(repo_root / "configs" / "intents.yaml"),
            "--no-demo-screenshots",
            "demo",
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=tmp_path,
        env={**os.environ, **{"PYTHONPATH": str(repo_root / "src")}},
    )
    assert result.returncode == 0
    assert "Generated" in result.stdout
    assert (out_dir / "cli_demo.json").exists()
