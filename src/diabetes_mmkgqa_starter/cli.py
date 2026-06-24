"""CLI entrypoint for the project bootstrap skeleton."""

from __future__ import annotations

from argparse import ArgumentParser
import sys
from typing import Sequence

from . import __version__


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
        print(f"[cli] {command} scaffold ready.")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
