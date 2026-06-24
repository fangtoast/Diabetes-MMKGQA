"""CLI entrypoint for the project bootstrap skeleton."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
import os
import subprocess
import sys
from typing import Sequence

from . import __version__
from . import graph_builder
from . import demo
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
    parser.add_argument("--neo4j-uri", default=None, help="Neo4j Bolt URI for load command.")
    parser.add_argument("--neo4j-user", default="neo4j", help="Neo4j username for load command.")
    parser.add_argument(
        "--neo4j-password",
        default=None,
        help="Neo4j password for load command. If omitted, load will require this argument.",
    )
    parser.add_argument("--neo4j-database", default="neo4j", help="Neo4j database name for load command.")
    parser.add_argument(
        "--backend",
        default="neo4j",
        choices=["neo4j", "portable"],
        help="Backend selection for load command.",
    )
    parser.add_argument("--load-dry-run", action="store_true", help="Build and validate Neo4j import plan without execution.")
    parser.add_argument(
        "--ontology-path",
        default=str(Path("configs") / "ontology.yaml"),
        help="Ontology path for load relation validation.",
    )
    parser.add_argument(
        "--intent-path",
        default=str(Path("configs") / "intents.yaml"),
        help="Intent contract path for QA and demo case execution.",
    )
    parser.add_argument(
        "--processed-dir",
        default=str(Path("data") / "processed"),
        help="Directory that stores portable KG exports for demo execution.",
    )
    parser.add_argument(
        "--demo-output-dir",
        default=str(Path("docs") / "cases"),
        help="Directory for generated demo case JSON.",
    )
    parser.add_argument(
        "--demo-output-json",
        default="demo_cases.json",
        help="Filename for generated demo results JSON.",
    )
    parser.add_argument(
        "--demo-screenshot-dir",
        default=str(Path("docs") / "screenshots"),
        help="Directory for demo case screenshots.",
    )
    parser.add_argument("--no-demo-screenshots", action="store_true", help="Skip screenshot generation for demo cases.")
    parser.add_argument(
        "--package-output-dir",
        default=str(Path("deliverables")),
        help="Directory for final deliverable packaging output.",
    )
    parser.add_argument(
        "--package-name",
        default="diabetes_mmkgqa_deliverables.zip",
        help="Archive filename for package output.",
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
        if command == "load":
            if args.backend == "portable":
                from .db import PortableGraphBackend

                backend = PortableGraphBackend.from_dir(Path(args.output_dir), ontology_path=Path(args.ontology_path))
                summary = backend.summary
                print(
                    "[cli] Portable backend loaded: "
                    f"nodes={summary.node_count}, edges={summary.edge_count}, images={summary.image_count}, "
                    f"stat_source={summary.stat_source}"
                )
                print(f"[cli] Portable health: {backend.health()}")
                return 0

            from .db import neo4j_loader

            summary = neo4j_loader.execute_load(
                processed_dir=Path(args.output_dir),
                uri=args.neo4j_uri,
                user=args.neo4j_user,
                password=args.neo4j_password,
                database=args.neo4j_database,
                ontology_path=Path(args.ontology_path),
                dry_run=args.load_dry_run,
            )
            print(
                "[cli] Neo4j import plan prepared/executed: "
                f"nodes={summary.node_count}, edges={summary.edge_count}, statements={summary.statement_count}, dry_run={args.load_dry_run}"
            )
            return 0
        if command == "demo":
            result = demo.run_demo_cases(
                repo_root=Path(args.repo_root),
                output_dir=Path(args.demo_output_dir),
                processed_dir=Path(args.processed_dir),
                intents_path=Path(args.intent_path),
                screenshot_dir=Path(args.demo_screenshot_dir),
                output_json=args.demo_output_json,
                capture_screenshots=not args.no_demo_screenshots,
            )
            print(f"[cli] Generated {result['case_count']} demo cases -> {result['output_path']}")
            print(f"[cli] Demo screenshots: {result['screenshot_count']}")
            return 0
        if command == "verify":
            env = os.environ.copy()
            repo_root = Path(args.repo_root)
            env["PYTHONPATH"] = str((repo_root / "src").resolve())

            test_result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests", "-q"],
                cwd=str(repo_root),
                env=env,
                check=False,
            )
            if test_result.returncode != 0:
                print("[cli] verify test suite failed")
                return test_result.returncode

            load_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "diabetes_mmkgqa_starter.cli",
                    "load",
                    "--backend",
                    "portable",
                    "--repo-root",
                    str(repo_root),
                    "--output-dir",
                    str((repo_root / "data" / "processed").resolve()),
                    "--ontology-path",
                    str((repo_root / "configs" / "ontology.yaml").resolve()),
                ],
                env=env,
                check=False,
            )
            if load_result.returncode != 0:
                print("[cli] verify portable load check failed")
                return load_result.returncode

            print("[cli] verify passed")
            return 0

        if command == "package":
            from . import package_builder

            result = package_builder.build_package(
                repo_root=Path(args.repo_root),
                processed_dir=Path(args.processed_dir),
                output_dir=Path(args.package_output_dir),
                archive_name=args.package_name,
            )
            summary = result["summary"]
            print(
                "[cli] Package status: "
                f"{summary['status']}, archive={result['archive_path']}, files={summary['included_file_count']}"
            )
            if summary["blocked_reasons"]:
                for reason in summary["blocked_reasons"]:
                    print(f"[cli] BLOCKED: {reason}")
            print(f"[cli] Package manifest: {result['summary_path']}")
            print(f"[cli] Package files checksum: {summary['archive']['sha256']}")
            return 0
        print(f"[cli] {command} scaffold ready.")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

