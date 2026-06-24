from io import StringIO
import sys
from contextlib import redirect_stdout

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
from pathlib import Path

from diabetes_mmkgqa_starter.cli import main


def test_cli_load_portable_backend(tmp_path: Path):
    # prepare minimal backend files
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
