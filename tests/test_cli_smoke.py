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
