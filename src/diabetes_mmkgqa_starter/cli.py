"""CLI entrypoint for the project bootstrap skeleton."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
import sys
from typing import Sequence

from . import __version__
from . import graph_builder


AVAILABLE_COMMANDS = (
    "help",
    "bootstrap",
    "data",
    "kg",
    "up",
    "load",
    "test",
    "verify",
    "demo",
    "report",
    "package",
)


def build_parser() -> ArgumentParser:
    """Build the CLI parser used by both the entrypoint and tests."""
    parser = ArgumentParser(
        prog="diabetes-mmkgqa",
        description=(
            "Educational non-diagnostic diabetic multimodal KGQA starter. "
            "This is a course demo tool, not a clinical diagnostic system."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=list(AVAILABLE_COMMANDS),
        help="bootstrap data kg up load test verify demo report package",
    )
    parser.add_argument("--repo-root", default=".", help="Repository root for KG build.")
    parser.add_argument("--output-dir", default=str(Path("data") / "processed"), help="Output directory for KG artifacts.")
    parser.add_argument("--skip-diakg", action="store_true", help="Skip DiaKG parser in kg command.")
    parser.add_argument("--skip-retina", action="store_true", help="Skip RetinaMNIST parser in kg command.")
    parser.add_argument("--skip-pneumonia", action="store_true", help="Skip PneumoniaMNIST parser in kg command.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI.

    Returns:
        int: exit code.
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    command = getattr(args, "command", None)

    if command is None or command == "help":
        parser.print_help()
        return 0

    if command in set(AVAILABLE_COMMANDS):
        if command == "kg":
            graph_builder.build_graph_outputs(
                repo_root=Path(args.repo_root),
                output_dir=Path(args.output_dir),
                include_diakg=not args.skip_diakg,
                include_retina=not args.skip_retina,
                include_pneumonia=not args.skip_pneumonia,
            )
            print(f"[cli] kg outputs generated in {Path(args.output_dir).resolve()}")
            return 0
        print(f"[cli] {command} scaffold ready.")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
