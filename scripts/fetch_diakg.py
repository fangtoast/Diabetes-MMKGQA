#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import ssl
import urllib.error
import urllib.request
from pathlib import Path
from typing import Mapping

import yaml


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_manifest(path: Path) -> Mapping[str, Mapping[str, object]]:
    with path.open('r', encoding='utf-8') as f:
        manifest = yaml.safe_load(f)
    return {item['source_id']: item for item in manifest['sources']}


def md5sum(path: Path) -> str:
    h = hashlib.md5()
    with path.open('rb') as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return f'md5:{h.hexdigest()}'


def download(url: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={'User-Agent': 'diabetes-mmkgqa-acquisition/0.1'})
    with urllib.request.urlopen(req, timeout=60, context=ssl.create_default_context()) as resp, target.open('wb') as out:
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)


def run(download: bool, use_fixture: bool, dry_run: bool, manifest_path: Path, force: bool) -> int:
    manifest = load_manifest(manifest_path)
    src = manifest['diakg']
    fixture_root = src['root_file'].replace('diakg.json', 'diakg_fixture.json')

    repo_root = get_repo_root()
    root_target = repo_root / src['root_file']
    fixture_target = repo_root / fixture_root

    expected_checksum = str(src.get('checksum', '')).strip()
    acquisition = str(src.get('acquisition', 'not available'))
    url = os.getenv('DIAKG_SOURCE_URL', '').strip()

    print('[diakg] source:', src['source_id'])
    print('  title:', src.get('title'))
    print('  acquisition:', acquisition)
    print('  license_or_terms:', src.get('license_or_terms'))
    print('  expected_checksum:', expected_checksum or 'TO_BE_FILLED_AFTER_DOWNLOAD')
    print('  root_file:', root_target)
    print('  fixture_file:', fixture_target)

    if dry_run:
        if root_target.exists():
            if expected_checksum and expected_checksum != 'VERIFY_AGAINST_OFFICIAL_METADATA':
                actual = md5sum(root_target)
                match = 'verified' if actual == expected_checksum else 'checksum_mismatch'
            else:
                match = 'present(no_checksum)'
            print('  status:', match)
        else:
            print('  status: missing')
        if fixture_target.exists():
            print('  fallback_fixture: present')
        else:
            print('  fallback_fixture: missing')
        print('  dry-run requested: no files were downloaded')
        return 0

    if use_fixture:
        if fixture_target.exists():
            print('Using fixture for offline development:', fixture_target)
            return 0
        print('ERROR: fixture not found:', fixture_target)
        return 1

    if not download:
        print('No download action requested; run with --download or --use-fixture. Exiting.')
        return 0

    if not url:
        print('BLOCKED: missing explicit DIAKG_SOURCE_URL environment variable for automated download.')
        print('  Please set DIAKG_SOURCE_URL then rerun, or use --use-fixture for offline skeleton.')
        return 2

    if root_target.exists() and not force:
        if expected_checksum and expected_checksum != 'VERIFY_AGAINST_OFFICIAL_METADATA':
            if md5sum(root_target) == expected_checksum:
                print('Root file exists and checksum matched; use --force to re-download.')
                return 0

    print('Downloading diakg from', url)
    try:
        download(url, root_target)
    except (urllib.error.URLError, OSError) as exc:
        print('ERROR: download failed:', exc)
        return 1

    if expected_checksum and expected_checksum != 'VERIFY_AGAINST_OFFICIAL_METADATA':
        actual = md5sum(root_target)
        if actual != expected_checksum:
            print('ERROR: checksum mismatch after download. expected=', expected_checksum, 'actual=', actual)
            return 1
        print('Downloaded and verified:', actual)
    else:
        print('Downloaded to:', root_target)
    return 0


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Fetch or validate DiaKG source and fallback fixture.')
    p.add_argument('--dry-run', action='store_true', help='Print plan and current status only.')
    p.add_argument('--download', action='store_true', help='Attempt download of diakg.json from DIAKG_SOURCE_URL.')
    p.add_argument('--use-fixture', action='store_true', help='Use the local fallback fixture explicitly.')
    p.add_argument('--force', action='store_true', help='Re-download even if existing root file is present.')
    p.add_argument('--manifest', default='data/source_manifest.yaml', help='Manifest path')
    return p.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = get_repo_root() / manifest_path
    if not manifest_path.exists():
        print('ERROR: manifest not found', manifest_path)
        return 1
    return run(download=args.download, use_fixture=args.use_fixture, dry_run=args.dry_run,
               manifest_path=manifest_path, force=args.force)


if __name__ == '__main__':
    raise SystemExit(main())
