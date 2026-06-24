from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import sys
import zipfile

from diabetes_mmkgqa_starter.cli import build_parser, main


def test_cli_help_shows_available_commands():
    parser = build_parser()
    with redirect_stdout(StringIO()) as fp:
        parser.print_help()
    output = fp.getvalue()
    assert "bootstrap" in output
    assert "diabetes-mmkgqa" in output


def test_cli_no_args_shows_help_and_returns_zero():
    code = main([])
    assert code == 0


def test_cli_version_flag_works():
    old_argv = sys.argv
    try:
        sys.argv = ["diabetes-mmkgqa", "--version"]
        try:
            main()
        except SystemExit as exc:  # argparse exits after printing version
            assert exc.code == 0
    finally:
        sys.argv = old_argv


def test_cli_load_portable_backend(tmp_path: Path):
    processed = tmp_path / "data" / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    (processed / "nodes.csv").write_text(
        "node_id,node_type,canonical_name,knowledge_layer,source_ids,kg_version\n"
        "n1,Disease,diabetes,C,manual,0.2.0\n",
        encoding="utf-8",
    )
    (processed / "edges.csv").write_text(
        "head_id,tail_id,edge_id,relation,source_id,extraction_method,confidence,knowledge_layer,kg_version\n",
        encoding="utf-8",
    )
    (processed / "images.csv").write_text(
        "image_id,relative_path,kg_version\n",
        encoding="utf-8",
    )

    code = main(["--repo-root", str(tmp_path), "--output-dir", str(processed), "load", "--backend", "portable"])
    assert code == 0


def test_cli_package_command_generates_archive_and_excludes_raw(tmp_path: Path):
    repo_root = tmp_path
    (repo_root / "README.md").write_text("# test\n", encoding="utf-8")
    (repo_root / "AGENTS.md").write_text("test agents\n", encoding="utf-8")
    (repo_root / "TASKS.md").write_text("dummy\n", encoding="utf-8")
    (repo_root / "docs").mkdir()
    (repo_root / "docs" / "project_plan.md").write_text("plan\n", encoding="utf-8")
    (repo_root / "docs" / "architecture.md").write_text("architecture\n", encoding="utf-8")
    (repo_root / "configs").mkdir()
    (repo_root / "configs" / "ontology.yaml").write_text("version: 0.2.0\n", encoding="utf-8")
    (repo_root / "configs" / "intents.yaml").write_text("version: 0.2.0\n", encoding="utf-8")
    (repo_root / "data").mkdir()
    (repo_root / "data" / "source_manifest.yaml").write_text("version: 0.2.0\nsources: []\n", encoding="utf-8")

    docs = repo_root / "docs"
    (docs / "report_inputs.md").write_text("report\n", encoding="utf-8")
    (docs / "cases").mkdir()
    (docs / "cases" / "demo_cases.json").write_text("{}", encoding="utf-8")
    (docs / "screenshots").mkdir()
    (docs / "screenshots" / "placeholder.txt").write_text("ui\n", encoding="utf-8")

    (repo_root / "requirements-lock.txt").write_text("pytest\n", encoding="utf-8")
    (repo_root / "pyproject.toml").write_text("[project]\nname=\"demo\"\n", encoding="utf-8")
    (repo_root / "Makefile").write_text("all:\n\t@echo test\n", encoding="utf-8")

    (repo_root / "src").mkdir()
    (repo_root / "src" / "diabetes_mmkgqa_starter").mkdir(parents=True)
    (repo_root / "src" / "diabetes_mmkgqa_starter" / "__init__.py").write_text("__version__ = '0.1.0'\n", encoding="utf-8")

    processed = repo_root / "data" / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    (processed / "stats.json").write_text('{"kg_version":"0.2.0"}', encoding="utf-8")
    (processed / "nodes.csv").write_text("node_id,node_type,canonical_name,knowledge_layer,source_ids,kg_version\n", encoding="utf-8")
    (processed / "nodes.parquet").write_text("", encoding="utf-8")
    (processed / "edges.csv").write_text("head_id,tail_id,edge_id,relation,source_id,extraction_method,confidence,knowledge_layer,kg_version\n", encoding="utf-8")
    (processed / "edges.parquet").write_text("", encoding="utf-8")
    (processed / "triples.tsv").write_text("", encoding="utf-8")
    (processed / "documents.csv").write_text("document_id,source_id\n", encoding="utf-8")
    (processed / "documents.parquet").write_text("", encoding="utf-8")
    (processed / "evidence.csv").write_text("evidence_id,document_id\n", encoding="utf-8")
    (processed / "evidence.parquet").write_text("", encoding="utf-8")
    (processed / "images.csv").write_text("image_id,relative_path\n", encoding="utf-8")
    (processed / "images.parquet").write_text("", encoding="utf-8")
    (processed / "schema.json").write_text("{}", encoding="utf-8")
    (processed / "graph.graphml").write_text("<graph></graph>", encoding="utf-8")

    raw_root = repo_root / "data" / "raw" / "manual"
    raw_root.mkdir(parents=True, exist_ok=True)
    (raw_root / "sample.csv").write_text("raw,data\n", encoding="utf-8")

    output_dir = repo_root / "deliverables"
    code = main(
        [
            "--repo-root",
            str(repo_root),
            "--package-output-dir",
            str(output_dir),
            "--package-name",
            "package.zip",
            "package",
        ]
    )
    assert code == 0

    archive = output_dir / "package.zip"
    assert archive.exists()
    with zipfile.ZipFile(archive, "r") as zf:
        names = zf.namelist()
    assert "data/raw/manual/sample.csv" not in names
    assert "package-manifest.json" in names or "package/package-manifest.json" in names

