"""Alias loader and deterministic entity normalization utilities."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import yaml

from diabetes_mmkgqa_starter.ingestion.manual_ab_tables import KG_VERSION, stable_node_id


def _normalize_text(value: str) -> str:
    return " ".join((value or "").strip().split())


def _read_manifest(manifest_path: Path) -> dict:
    with manifest_path.open("r", encoding="utf-8-sig") as f:
        payload = yaml.safe_load(f)
    return {item["source_id"]: item for item in payload.get("sources", [])}


def _read_csv_rows(source_file: Path, required_fields: Iterable[str]) -> list[dict]:
    with source_file.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"Missing header in {source_file}")
        fieldset = set(reader.fieldnames)
        missing = [x for x in required_fields if x not in fieldset]
        if missing:
            raise ValueError(f"{source_file} missing required fields: {', '.join(missing)}")
        return [dict((k, _normalize_text(v)) for k, v in row.items()) for row in reader]


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8-sig")
        return

    all_fields = sorted({k for row in rows for k in row.keys()})
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=all_fields)
        writer.writeheader()
        writer.writerows(rows)


def _alias_key(node_type: str, alias: str) -> str:
    return f"{node_type}|{_normalize_text(alias).lower()}"


@dataclass(frozen=True)
class AliasLoadOutputs:
    aliases: List[dict]
    alias_index: dict[tuple[str, str], str]
    stats: dict


def _canon_key(item: dict) -> tuple[str, str]:
    return (_normalize_text(item.get("node_type", "")), _normalize_text(item.get("canonical_name", "")))


def parse_alias_rows(rows: list[dict], source_id: str) -> list[dict]:
    alias_rows: list[dict] = []
    seen: set[tuple[str, str]] = set()

    for row in rows:
        canonical_name = _normalize_text(row.get("canonical_name", ""))
        alias = _normalize_text(row.get("alias", ""))
        node_type = _normalize_text(row.get("node_type", ""))

        if not canonical_name or not alias or not node_type:
            continue

        record = {
            "canonical_name": canonical_name,
            "alias": alias,
            "node_type": node_type,
            "reviewer": row.get("reviewer", "Team"),
            "note": row.get("note", ""),
            "source_id": source_id,
            "kg_version": KG_VERSION,
        }

        signature = (record["canonical_name"], record["alias"], record["node_type"])
        if signature in seen:
            continue
        seen.add(signature)
        alias_rows.append(record)

    alias_rows.sort(key=lambda x: (x["node_type"], x["canonical_name"], x["alias"]))
    return alias_rows


def build_alias_index(alias_rows: list[dict]) -> dict[tuple[str, str], str]:
    index: dict[tuple[str, str], str] = {}
    for row in alias_rows:
        node_type = _normalize_text(row["node_type"])
        alias = _normalize_text(row["alias"]).lower()
        canonical = _normalize_text(row["canonical_name"])
        index[(node_type, alias)] = canonical
    return index


def canonicalize_entity_name(
    alias_index: dict[tuple[str, str], str],
    entity_name: str,
    node_type: str,
) -> str:
    normalized_name = _normalize_text(entity_name)
    normalized_type = _normalize_text(node_type)
    if not normalized_name or not normalized_type:
        return normalized_name
    return alias_index.get((normalized_type, normalized_name.lower()), normalized_name)


def normalize_entity_records(
    rows: list[dict],
    alias_index: dict[tuple[str, str], str],
) -> list[dict]:
    output: list[dict] = []
    for row in rows:
        node_type = _normalize_text(row.get("node_type", ""))
        canonical_input = _normalize_text(row.get("canonical_name", ""))
        alias_input = _normalize_text(row.get("alias_name", ""))

        canonical_name = canonical_input
        canonicalized_from_alias = "0"
        if alias_input and node_type:
            alias_canonical = canonicalize_entity_name(alias_index, alias_input, node_type)
            if alias_canonical and alias_canonical != canonical_name:
                canonical_name = alias_canonical
                canonicalized_from_alias = "0" if canonical_name and canonical_input else "1"

        if not canonical_name:
            canonical_name = canonical_input

        normalized = dict(row)
        normalized["canonical_name"] = _normalize_text(canonical_name)
        normalized["canonicalized_from_alias"] = canonicalized_from_alias
        normalized["node_type"] = node_type
        if not normalized["canonical_name"]:
            continue

        stable_type = row.get("node_type", node_type) or row.get("node_type_hint", node_type)
        output.append(normalized)

    return sorted(output, key=lambda x: (_canon_key(x)[0], _canon_key(x)[1]))


def parse_aliases(
    repo_root: Path,
    *,
    source_id: str | None = None,
    manifest_path: Path | None = None,
) -> AliasLoadOutputs:
    manifest = _read_manifest(manifest_path or (repo_root / "data" / "source_manifest.yaml"))
    selected_source = source_id or "manual_aliases"
    if selected_source not in manifest:
        raise KeyError(f"{selected_source} is missing in source manifest.")
    source = manifest[selected_source]
    source_path = repo_root / source["root_file"]
    if not source_path.exists():
        raise FileNotFoundError(f"Alias source file missing: {source_path}")

    rows = _read_csv_rows(source_path, ["canonical_name", "alias", "node_type", "reviewer", "note"])
    alias_rows = parse_alias_rows(rows, selected_source)
    alias_index = build_alias_index(alias_rows)

    node_records = normalize_entity_records(alias_rows, alias_index)
    stats = {
        "alias_count": len(alias_rows),
        "canonical_node_count": len(node_records),
        "alias_type_count": len(set(row["node_type"] for row in alias_rows)),
        "kg_version": KG_VERSION,
    }

    return AliasLoadOutputs(
        aliases=alias_rows,
        alias_index={k: v for k, v in alias_index.items()},
        stats=stats,
    )


def export_alias_outputs(parsed: AliasLoadOutputs, output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    out_aliases = output_dir / "aliases.csv"
    out_index = output_dir / "alias_index.csv"

    _write_csv(out_aliases, parsed.aliases)

    index_rows = [
        {
            "node_type": k[0],
            "alias": k[1],
            "canonical_name": v,
            "kg_version": KG_VERSION,
            "target_node_id": stable_node_id("A", k[0], v),
        }
        for k, v in sorted(parsed.alias_index.items())
    ]
    _write_csv(out_index, index_rows)

    return {
        "aliases": out_aliases,
        "alias_index": out_index,
    }
