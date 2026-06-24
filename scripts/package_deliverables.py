"""CLI wrapper for deliverable package generation."""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from diabetes_mmkgqa_starter.package_builder import main as _main


if __name__ == "__main__":
    raise SystemExit(_main())

