#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, Iterable, Mapping

import yaml


ZENODO_RECORD_ID = "10519652"
RECORD_BASE_URL = f"https://zenodo.org/api/records/{ZENODO_RECORD_ID}"

# Static fallback metadata in case Zenodo API is temporarily unavailable.
MEDMNIST_FALLBACK = {
    "retinamnist": {
        "file": "retinamnist_224.npz",
        "checksum": "md5:eae7e3b6f3fcbda4ae613ebdcbe35348",
        "size": 127_992_567,
        "source_url": "https://zenodo.org/api/records/10519652/files/retinamnist_224.npz/content",
    },
    "pneumoniamnist": {
        "file": "pneumoniamnist_224.npz",
        "checksum": "md5:d6a3c71de1b945ea11211b03746c1fe1",
        "size": 214_384_716,
        "source_url": "https://zenodo.org/api/records/10519652/files/pneumoniamnist_224.npz/content",
    },
}


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def get_manifest(path: Path) -> Mapping[str, Mapping[str, object]]:
    with open(path, "r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)
    entries = {item["source_id"]: item for item in manifest.get("sources", [])}
    return entries


def build_download_catalog() -> Dict[str, Dict[str, str]]:
    ctx = ssl.create_default_context()
    catalog: Dict[str, Dict[str, str]] = {}
    try:
        req = urllib.request.Request(
            RECORD_BASE_URL,
            headers={"User-Agent": "diabetes-mmkgqa-acquisition/0.1"},
        )
        with urllib.request.urlopen(req, timeout=30, context=ctx) as response:
            payload = json.load(response)
            for file_info in payload.get("files", []):
                key = file_info.get("key", "")
                if key not in {"retinamnist_224.npz", "pneumoniamnist_224.npz"}:
                    continue
                dataset = "retinamnist" if key.startswith("retinamnist") else "pneumoniamnist"
                catalog[dataset] = {
                    "file": key,
                    "checksum": file_info.get("checksum", ""),
                    "size": file_info.get("size", 0),
                    "source_url": file_info.get("links", {}).get("self", ""),
                }
        if catalog:
            return catalog
    except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        print(f"[warn] Failed to query Zenodo metadata: {exc}", file=sys.stderr)

    print("[info] Using fallback MedMNIST catalog metadata")
    return MEDMNIST_FALLBACK.copy()


def md5sum(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return f"md5:{h.hexdigest()}"


def validate_checksum(path: Path, expected: str) -> bool:
    if not expected:
        return False
    if not path.exists():
        return False
    observed = md5sum(path)
    return observed == expected.lower()


def download_one(url: str, target: Path, timeout: int = 30) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": "diabetes-mmkgqa-acquisition/0.1"})
    with urllib.request.urlopen(req, timeout=timeout, context=ssl.create_default_context()) as response, open(tmp, "wb") as out:
        while True:
            buf = response.read(1024 * 1024)
            if not buf:
                break
            out.write(buf)
    tmp.replace(target)


def select_sources(manifest: Mapping[str, Mapping[str, object]], include: Iterable[str]) -> Dict[str, Mapping[str, object]]:
    selected = set(include)
    out: Dict[str, Mapping[str, object]] = {}
    for source_id in selected:
        if source_id not in manifest:
            continue
        if source_id not in ("retinamnist", "pneumoniamnist"):
            continue
        out[source_id] = manifest[source_id]
    return out


def run_fetch(dataset: str, manifest_path: Path, do_download: bool, force: bool, dry_run: bool) -> int:
    repo_root = get_repo_root()
    manifest = get_manifest(manifest_path)
    catalog = build_download_catalog()

    requested = ["retinamnist", "pneumoniamnist"] if dataset == "all" else [dataset]
    selected = select_sources(manifest, requested)

    report = []
    exit_code = 0

    for source_id, source in selected.items():
        filename = catalog.get(source_id, {}).get("file", MEDMNIST_FALLBACK[source_id]["file"])
        expected_checksum = catalog.get(source_id, {}).get("checksum", "")
        download_url = catalog.get(source_id, {}).get("source_url", "")
        target = repo_root / str(source.get("root_file", source_id))
        root_note = f"root_file={source.get('root_file')}"

        if not target.exists():
            status = "missing"
        elif not expected_checksum:
            status = "present(no expected checksum)"
        elif validate_checksum(target, expected_checksum):
            status = "verified"
        else:
            status = "present(checksum-mismatch)"

        row = {
            "source_id": source_id,
            "target": str(target),
            "download_url": download_url,
            "expected_checksum": expected_checksum,
            "status": status,
            "manifest_root": source.get("root_file"),
        }
        report.append(row)

        print(
            f"[{source_id}] {root_note}"
            f"\n  acquisition={source.get('acquisition')}"
            f"\n  target={target}"
            f"\n  status={status}"
            f"\n  checksum={expected_checksum or 'UNKNOWN'}"
        )

        if do_download:
            if target.exists() and status == "verified" and not force:
                print(f"[skip] {source_id}: target already verified")
                continue
            try:
                if not download_url:
                    print(f"[warn] {source_id}: missing download URL", file=sys.stderr)
                    exit_code = 1
                    continue
                print(f"[download] {source_id} -> {target}")
                download_one(download_url, target)
                if expected_checksum and not validate_checksum(target, expected_checksum):
                    print(f"[error] checksum mismatch after download: {source_id}", file=sys.stderr)
                    exit_code = 1
                else:
                    print(f"[ok] downloaded and verified: {source_id}")
            except Exception as exc:
                print(f"[error] {source_id} download failed: {exc}", file=sys.stderr)
                exit_code = 1

    if dry_run:
        print("DRY-RUN: no files were downloaded")

    if not report:
        print(f"[error] no valid MedMNIST targets for dataset='{dataset}'", file=sys.stderr)
        return 1

    return exit_code


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Acquire MedMNIST official ROOT npz files for reproducible KG pipeline.")
    p.add_argument(
        "--dataset",
        choices=["all", "retinamnist", "pneumoniamnist"],
        default="all",
        help="dataset to process",
    )
    p.add_argument(
        "--manifest",
        default="data/source_manifest.yaml",
        help="path to source manifest (default: data/source_manifest.yaml)",
    )
    p.add_argument("--download", action="store_true", help="download files if missing or mismatched")
    p.add_argument("--force", action="store_true", help="re-download even if already verified")
    p.add_argument("--dry-run", action="store_true", help="print plan and status only")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = get_repo_root() / manifest_path

    if not manifest_path.exists():
        print(f"[error] manifest not found: {manifest_path}", file=sys.stderr)
        return 1

    do_download = bool(args.download and not args.dry_run)
    return run_fetch(args.dataset, manifest_path, do_download=do_download, force=args.force, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
