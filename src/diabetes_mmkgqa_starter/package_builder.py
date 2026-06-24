"""Build deterministic deliverable package artifacts for project handoff."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import zipfile

REQUIRED_FILES = [
    "AGENTS.md",
    "README.md",
    "TASKS.md",
    "docs/project_plan.md",
    "docs/architecture.md",
    "configs/ontology.yaml",
    "configs/intents.yaml",
    "data/source_manifest.yaml",
    "requirements-lock.txt",
    "pyproject.toml",
    "docs/report_inputs.md",
]

OPTIONAL_REQUIRED_PACK_FILES = [
    "docs/cases/demo_cases.json",
]

REQUIRED_PROCESSED_FILES = [
    "stats.json",
    "nodes.csv",
    "nodes.parquet",
    "edges.csv",
    "edges.parquet",
    "triples.tsv",
    "documents.csv",
    "documents.parquet",
    "evidence.csv",
    "evidence.parquet",
    "images.csv",
    "images.parquet",
    "schema.json",
    "graph.graphml",
]

SAFE_DIRECTORIES = [
    ("src", "platform/src"),
    ("configs", "platform/configs"),
    ("scripts", "platform/scripts"),
    ("docs", "platform/docs"),
    ("tests", "platform/tests"),
]

BLOCKED_EXCLUDED_PATTERNS = [
    "data/raw/**",
    "data/interim/**",
    "deliverables/**",
    "**/__pycache__/**",
    "**/.pytest_cache/**",
]


def _sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1 << 20), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _is_excluded(relative_path: Path) -> bool:
    parts = relative_path.parts
    if not parts:
        return False
    if parts[0] == "data" and len(parts) > 1 and parts[1] in {"raw", "interim"}:
        return True
    if parts[0] == "deliverables":
        return True
    if "__pycache__" in parts or ".pytest_cache" in parts:
        return True
    return False


def _safe_copy_file(source: Path, destination_root: Path, archive_path: Path, *, copied: list[dict], missing: list[str]) -> None:
    if not source.exists():
        missing.append(str(archive_path))
        return
    destination = destination_root / archive_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    copied.append(
        {
            "source": str(source),
            "archive_path": str(archive_path.as_posix()),
            "size": source.stat().st_size,
            "sha256": _sha256(source),
        }
    )


def _copy_directory_tree(
    source_root: Path,
    destination_root: Path,
    archive_prefix: Path,
    copied: list[dict],
) -> None:
    if not source_root.exists():
        return

    for source_file in source_root.rglob("*"):
        if not source_file.is_file():
            continue
        rel = source_file.relative_to(source_root)
        if _is_excluded(rel):
            continue
        destination = destination_root / archive_prefix / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, destination)
        copied.append(
            {
                "source": str(source_file),
                "archive_path": str((archive_prefix / rel).as_posix()),
                "size": source_file.stat().st_size,
                "sha256": _sha256(source_file),
            }
        )


def _collect_file_records(staging_root: Path) -> list[dict]:
    records: list[dict] = []
    for source in sorted(staging_root.rglob("*")):
        if not source.is_file():
            continue
        relative = source.relative_to(staging_root)
        records.append(
            {
                "archive_path": relative.as_posix(),
                "size": source.stat().st_size,
                "sha256": _sha256(source),
            }
        )
    return sorted(records, key=lambda row: row["archive_path"])


def build_package(
    repo_root: Path,
    *,
    processed_dir: Path | None = None,
    output_dir: Path,
    archive_name: str = "diabetes_mmkgqa_deliverables.zip",
) -> dict:
    repo_root = repo_root.resolve()
    processed_dir = (processed_dir or (repo_root / "data" / "processed")).resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if output_dir in {repo_root, repo_root / "data" / "processed"}:
        raise ValueError("package output directory must be outside source data root or explicitly isolated.")

    staging = output_dir / "_package_staging"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    copied: list[dict] = []
    missing: list[str] = []
    blocked_reasons: list[str] = []

    for rel in REQUIRED_FILES:
        src = repo_root / rel
        _safe_copy_file(src, staging, Path(rel), copied=copied, missing=missing)
        if not src.exists():
            blocked_reasons.append(f"Missing required file: {rel}")

    for rel in OPTIONAL_REQUIRED_PACK_FILES:
        _safe_copy_file(repo_root / rel, staging, Path("report") / rel, copied=copied, missing=missing)

    for source_dir, archive_dir in SAFE_DIRECTORIES:
        _copy_directory_tree(repo_root / source_dir, staging, Path(archive_dir), copied=copied)

    package_data_dir = staging / "kg"
    package_data_dir.mkdir(parents=True, exist_ok=True)
    for processed_file in REQUIRED_PROCESSED_FILES:
        source_path = processed_dir / processed_file
        destination = Path("kg") / processed_file
        _safe_copy_file(source_path, staging, destination, copied=copied, missing=missing)
        if processed_file in {"nodes.csv", "edges.csv", "stats.json"} and not source_path.exists():
            blocked_reasons.append(f"Missing critical KG file: data/processed/{processed_file}")

    package_dir = staging / "package"
    package_dir.mkdir(parents=True, exist_ok=True)

    reproducibility_text = (
        "# Reproducible package record\n"
        f"- Generated at: {datetime.now(timezone.utc).isoformat()}\n"
        f"- Repository root: {repo_root}\n"
        "- Rule: data/raw and other immutable roots are excluded from package.\n"
        "- Packaging commands:\n"
        "  - python -m diabetes_mmkgqa_starter.cli kg\n"
        "  - python -m diabetes_mmkgqa_starter.cli demo\n"
        "  - make report\n"
        f"- Output archive: {archive_name}\n"
    )
    (package_dir / "reproducibility.txt").write_text(reproducibility_text, encoding="utf-8")

    (package_dir / "excluded_paths.txt").write_text(
        "\n".join(BLOCKED_EXCLUDED_PATTERNS) + "\n",
        encoding="utf-8",
    )

    manifest_records = _collect_file_records(staging)
    checksums = "\n".join(f"{item['sha256']}  {item['archive_path']}" for item in manifest_records)
    checksums_path = staging / "package" / "checksums.sha256"
    checksums_path.write_text(checksums, encoding="utf-8")

    manifest_records = _collect_file_records(staging)
    source_manifest = repo_root / "data" / "source_manifest.yaml"
    kg_version = "unknown"
    stats_path = processed_dir / "stats.json"
    if stats_path.exists():
        try:
            stats_payload = json.loads(stats_path.read_text(encoding="utf-8"))
            if isinstance(stats_payload, dict):
                kg_version = str(stats_payload.get("kg_version", "unknown"))
        except Exception:
            pass

    status = "BLOCKED" if blocked_reasons else "READY"

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "package_name": archive_name,
        "status": status,
        "blocked_reasons": blocked_reasons,
        "kg_version": kg_version,
        "manifest_source_id_count": 0,
        "source_manifest": str(source_manifest),
        "included_file_count": len(manifest_records),
        "missing_paths": missing,
        "excluded_path_patterns": BLOCKED_EXCLUDED_PATTERNS,
        "output_dir": str(output_dir),
    }

    # Try read source manifest for quick checks in manifest file itself.
    if source_manifest.exists():
        summary["manifest_source_id_count"] = len([line for line in source_manifest.read_text(encoding="utf-8").splitlines() if "source_id" in line])

    manifest_path = staging / "package" / "package-manifest.json"
    manifest_payload = {
        "summary": summary,
        "files": manifest_records,
    }
    manifest_path.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest_records = _collect_file_records(staging)

    # Rewrite checksums to include the manifest record.
    checksums = "\n".join(f"{item['sha256']}  {item['archive_path']}" for item in manifest_records)
    checksums_path.write_text(checksums, encoding="utf-8")

    manifest_records = _collect_file_records(staging)
    archive_path = output_dir / archive_name
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for item in sorted(staging.rglob("*"), key=lambda p: str(p).lower()):
            if not item.is_file():
                continue
            rel = item.relative_to(staging).as_posix()
            zinfo = zipfile.ZipInfo(rel)
            zinfo.date_time = (1980, 1, 1, 0, 0, 0)
            zinfo.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(zinfo, item.read_bytes())

    summary["archive"] = {
        "path": str(archive_path),
        "size": archive_path.stat().st_size,
        "sha256": _sha256(archive_path),
    }

    manifest_path.write_text(
        json.dumps({"summary": summary, "files": manifest_records}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    summary_path = output_dir / "package-manifest.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "archive_path": archive_path,
        "staging_dir": staging,
        "summary": summary,
        "manifest_path": manifest_path,
        "summary_path": summary_path,
        "copied_files": copied,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create reproducible deliverable package artifacts.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--processed-dir", default=str(Path("data") / "processed"))
    parser.add_argument("--package-output-dir", default="deliverables")
    parser.add_argument("--package-name", default="diabetes_mmkgqa_deliverables.zip")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = build_package(
        Path(args.repo_root),
        processed_dir=Path(args.processed_dir),
        output_dir=Path(args.package_output_dir),
        archive_name=args.package_name,
    )
    summary = result["summary"]
    print(f"[package] status={summary['status']} archive={result['archive_path']}")
    print(f"[package] files={summary['included_file_count']}")
    for reason in summary["blocked_reasons"]:
        print(f"[package] BLOCKED: {reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
