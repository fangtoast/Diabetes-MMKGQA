"""Parsers for A/B/C manual table sources.

This module converts seeded CSV sources into normalized graph-ready node and edge
records with deterministic IDs.
"""

from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import yaml


KG_VERSION = "0.2.0"


def _sha1(value: str) -> str:
    """Compute deterministic sha1 for stable identifiers."""
    return hashlib.sha1(value.encode("utf-8")).hexdigest()


def stable_node_id(knowledge_layer: str, node_type: str, canonical_name: str) -> str:
    return _sha1("|".join([knowledge_layer, node_type, canonical_name.strip().lower()]))


def stable_edge_id(head_id: str, relation: str, tail_id: str, source_id: str, evidence_id: str = "") -> str:
    return _sha1("|".join([head_id, relation, tail_id, source_id, evidence_id or ""]))


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
        path.write_text("", encoding="utf-8")
        return

    all_fields = sorted({k for row in rows for k in row.keys()})
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=all_fields)
        writer.writeheader()
        writer.writerows(rows)


@dataclass(frozen=True)
class ManualParseOutputs:
    nodes: List[dict]
    edges: List[dict]
    aliases: List[dict]
    stats: dict


def _add_node(
    nodes: dict,
    *,
    source_id: str,
    node_type: str,
    canonical_name: str,
    knowledge_layer: str,
    kg_version: str = KG_VERSION,
    extras: dict | None = None,
) -> str:
    canonical = _normalize_text(canonical_name)
    if not canonical:
        raise ValueError(f"{node_type} missing canonical_name")

    node_id = stable_node_id(knowledge_layer, node_type, canonical)
    if node_id in nodes:
        return node_id

    record = {
        "node_id": node_id,
        "node_type": node_type,
        "canonical_name": canonical,
        "knowledge_layer": knowledge_layer,
        "source_ids": source_id,
        "kg_version": kg_version,
    }
    if extras:
        for key, value in extras.items():
            if value != "":
                record[key] = value
    nodes[node_id] = record
    return node_id


def _add_edge(
    edges: dict,
    *,
    head_id: str,
    relation: str,
    tail_id: str,
    source_id: str,
    knowledge_layer: str,
    extraction_method: str = "manual",
    confidence: str = "1.0",
    evidence_id: str = "",
    raw_relation: str = "",
    normalized_relation: str = "",
    kg_version: str = KG_VERSION,
) -> str:
    edge_id = stable_edge_id(head_id, relation, tail_id, source_id, evidence_id)
    if edge_id in edges:
        return edge_id

    edges[edge_id] = {
        "edge_id": edge_id,
        "head_id": head_id,
        "relation": relation,
        "tail_id": tail_id,
        "source_id": source_id,
        "extraction_method": extraction_method,
        "confidence": confidence,
        "knowledge_layer": knowledge_layer,
        "kg_version": kg_version,
        "evidence_id": evidence_id or "",
        "raw_relation": raw_relation or relation,
        "normalized_relation": normalized_relation or relation,
    }
    return edge_id


def parse_manual_a_terms(rows: list[dict], source_id: str) -> list[dict]:
    nodes_by_id: dict[str, dict] = {}
    for row in rows:
        _add_node(
            nodes_by_id,
            source_id=source_id,
            node_type=row["node_type"],
            canonical_name=row["canonical_name"],
            knowledge_layer="A",
            extras={
                "description": row.get("description", ""),
                "aliases": row.get("synonyms", ""),
            },
        )

    return sorted(nodes_by_id.values(), key=lambda x: x["node_id"])


def parse_manual_b_icd(rows: list[dict], source_id: str) -> tuple[list[dict], list[dict]]:
    nodes_by_id: dict[str, dict] = {}
    edges_by_id: dict[str, dict] = {}

    for row in rows:
        disease_name = row["disease_name"]
        disease_id = _add_node(
            nodes_by_id,
            source_id=source_id,
            node_type="Disease",
            canonical_name=disease_name,
            knowledge_layer="C",
            extras={"description": row.get("note", "")},
        )
        icd_id = _add_node(
            nodes_by_id,
            source_id=source_id,
            node_type="ICD_Code",
            canonical_name=row["icd_code"],
            knowledge_layer="B",
            extras={"description": row.get("note", ""), "code": row["icd_code"]},
        )
        _add_edge(
            edges_by_id,
            head_id=disease_id,
            relation="HAS_ICD_CODE",
            tail_id=icd_id,
            source_id=source_id,
            knowledge_layer="B",
            raw_relation="ICD_Disease",
            normalized_relation="HAS_ICD_CODE",
        )

    return (
        sorted(nodes_by_id.values(), key=lambda x: x["node_id"]),
        sorted(edges_by_id.values(), key=lambda x: x["edge_id"]),
    )


def parse_manual_b_rules(rows: list[dict], source_id: str) -> tuple[list[dict], list[dict]]:
    nodes_by_id: dict[str, dict] = {}
    edges_by_id: dict[str, dict] = {}

    for row in rows:
        guideline_name = f"{row['source_ref'] or 'Manual'} guideline"
        guideline_id = _add_node(
            nodes_by_id,
            source_id=source_id,
            node_type="Guideline",
            canonical_name=guideline_name,
            knowledge_layer="B",
        )

        rule_name = f"{row['disease_name']}:{row['rule_type']}"
        rule_id = _add_node(
            nodes_by_id,
            source_id=source_id,
            node_type="StandardRule",
            canonical_name=rule_name,
            knowledge_layer="B",
            extras={
                "code": row.get("code", ""),
                "unit": row.get("unit", ""),
                "description": row.get("comments", ""),
                "finding": row.get("rule_type", ""),
            },
        )
        _add_edge(
            edges_by_id,
            head_id=guideline_id,
            relation="HAS_STANDARD_RULE",
            tail_id=rule_id,
            source_id=source_id,
            knowledge_layer="B",
            raw_relation="Guideline_Rule",
            normalized_relation="HAS_STANDARD_RULE",
        )

        disease_id = _add_node(
            nodes_by_id,
            source_id=source_id,
            node_type="Disease",
            canonical_name=row["disease_name"],
            knowledge_layer="C",
            extras={"description": row.get("comments", "")},
        )
        test_item_id = None
        if row.get("rule_type"):
            test_item_id = _add_node(
                nodes_by_id,
                source_id=source_id,
                node_type="TestItem",
                canonical_name=row["rule_type"],
                knowledge_layer="A",
                extras={
                    "unit": row.get("unit", ""),
                    "description": row.get("comments", ""),
                },
            )
            _add_edge(
                edges_by_id,
                head_id=disease_id,
                relation="HAS_TEST_ITEM",
                tail_id=test_item_id,
                source_id=source_id,
                knowledge_layer="A",
                raw_relation="TestItem_Disease",
                normalized_relation="HAS_TEST_ITEM",
            )
        _add_edge(
            edges_by_id,
            head_id=rule_id,
            relation="APPLIES_TO",
            tail_id=disease_id,
            source_id=source_id,
            knowledge_layer="B",
            raw_relation="Guideline_Disease",
            normalized_relation="APPLIES_TO",
        )

        if row.get("rule_type") and row.get("code"):
            threshold_id = _add_node(
                nodes_by_id,
                source_id=source_id,
                node_type="DiagnosticThreshold",
                canonical_name=f"{row['disease_name']}:{row['rule_type']}:{row['code']}",
                knowledge_layer="B",
                extras={"code": row["code"], "unit": row.get("unit", ""), "description": row.get("value", "")},
            )
            _add_edge(
                edges_by_id,
                head_id=test_item_id or rule_id,
                relation="HAS_DIAGNOSTIC_THRESHOLD",
                tail_id=threshold_id,
                source_id=source_id,
                knowledge_layer="B",
                raw_relation="Threshold_TestItem",
                normalized_relation="HAS_DIAGNOSTIC_THRESHOLD",
            )

    return (
        sorted(nodes_by_id.values(), key=lambda x: x["node_id"]),
        sorted(edges_by_id.values(), key=lambda x: x["edge_id"]),
    )


def parse_manual_c_hypertension(rows: list[dict], source_id: str) -> tuple[list[dict], list[dict], list[dict]]:
    nodes_by_id: dict[str, dict] = {}
    edges_by_id: dict[str, dict] = {}
    aliases: list[dict] = []

    for row in rows:
        disease_id = _add_node(
            nodes_by_id,
            source_id=source_id,
            node_type="Disease",
            canonical_name=row["disease_name"],
            knowledge_layer="C",
            extras={"description": row.get("recommendation", "")},
        )
        rule_id = _add_node(
            nodes_by_id,
            source_id=source_id,
            node_type="StandardRule",
            canonical_name=row["rule_name"],
            knowledge_layer="B",
            extras={
                "severity": row.get("severity", ""),
                "description": row.get("recommendation", ""),
            },
        )
        _add_edge(
            edges_by_id,
            head_id=rule_id,
            relation="APPLIES_TO",
            tail_id=disease_id,
            source_id=source_id,
            knowledge_layer="B",
            raw_relation="Guideline_Disease",
            normalized_relation="APPLIES_TO",
        )

        finding_id = _add_node(
            nodes_by_id,
            source_id=source_id,
            node_type="SeverityLevel",
            canonical_name=f"{row['finding']}",
            knowledge_layer="C",
            extras={"description": row.get("finding", "")},
        )
        aliases.append(
            {
                "canonical_name": row["finding"],
                "alias": row["rule_name"],
                "target_node_id": finding_id,
                "source_id": source_id,
                "node_type": "SeverityLevel",
                "kind": "hypertension_rule_finding",
                "kg_version": KG_VERSION,
            }
        )

    return (
        sorted(nodes_by_id.values(), key=lambda x: x["node_id"]),
        sorted(edges_by_id.values(), key=lambda x: x["edge_id"]),
        sorted(aliases, key=lambda x: (x["canonical_name"], x["alias"])),
    )


def parse_manual_aliases(rows: list[dict], source_id: str) -> list[dict]:
    alias_rows: list[dict] = []
    for row in rows:
        alias_rows.append(
            {
                "canonical_name": _normalize_text(row["canonical_name"]),
                "alias": _normalize_text(row["alias"]),
                "node_type": row["node_type"],
                "reviewer": row.get("reviewer", "Team"),
                "note": row.get("note", ""),
                "source_id": source_id,
                "kg_version": KG_VERSION,
            }
        )
    return sorted(alias_rows, key=lambda x: (x["canonical_name"], x["alias"]))


def parse_manual_sources(
    repo_root: Path,
    manifest_path: Path | None = None,
) -> ManualParseOutputs:
    manifest_path = manifest_path or (repo_root / "data" / "source_manifest.yaml")
    source_map = _read_manifest(manifest_path)

    def source_path(source_id: str) -> Path:
        return repo_root / source_map[source_id]["root_file"]

    a_rows = _read_csv_rows(
        source_path("manual_a_general_terms"),
        ["canonical_name", "node_type", "synonyms", "description"],
    )
    icd_rows = _read_csv_rows(
        source_path("manual_b_icd10_subset"),
        ["disease_name", "icd_code", "disease_layer", "note"],
    )
    rule_rows = _read_csv_rows(
        source_path("manual_b_guideline_rules"),
        ["disease_name", "rule_type", "code", "value", "unit", "source_ref", "comments"],
    )
    htn_rows = _read_csv_rows(
        source_path("manual_c_hypertension_rules"),
        ["rule_name", "disease_name", "finding", "severity", "recommendation", "source"],
    )
    alias_rows = _read_csv_rows(
        source_path("manual_aliases"),
        ["canonical_name", "alias", "node_type", "reviewer", "note"],
    )

    nodes: dict[str, dict] = {}
    edges: dict[str, dict] = {}
    alias_links: list[dict] = []

    for node in parse_manual_a_terms(a_rows, source_map["manual_a_general_terms"]["source_id"]):
        nodes[node["node_id"]] = node

    icd_nodes, icd_edges = parse_manual_b_icd(
        icd_rows, source_map["manual_b_icd10_subset"]["source_id"]
    )
    for node in icd_nodes:
        nodes[node["node_id"]] = node
    for edge in icd_edges:
        edges[edge["edge_id"]] = edge

    rule_nodes, rule_edges = parse_manual_b_rules(
        rule_rows, source_map["manual_b_guideline_rules"]["source_id"]
    )
    for node in rule_nodes:
        nodes[node["node_id"]] = node
    for edge in rule_edges:
        edges[edge["edge_id"]] = edge

    c_nodes, c_edges, c_aliases = parse_manual_c_hypertension(
        htn_rows, source_map["manual_c_hypertension_rules"]["source_id"]
    )
    for node in c_nodes:
        nodes[node["node_id"]] = node
    for edge in c_edges:
        edges[edge["edge_id"]] = edge

    alias_links.extend(c_aliases)
    alias_links.extend(parse_manual_aliases(alias_rows, source_map["manual_aliases"]["source_id"]))

    return ManualParseOutputs(
        nodes=sorted(nodes.values(), key=lambda x: x["node_id"]),
        edges=sorted(edges.values(), key=lambda x: x["edge_id"]),
        aliases=sorted(alias_links, key=lambda x: (x["canonical_name"], x.get("alias", ""))),
        stats={
            "node_count": len(nodes),
            "edge_count": len(edges),
            "alias_count": len(alias_links),
            "kg_version": KG_VERSION,
        },
    )


def export_manual_interim_outputs(parsed: ManualParseOutputs, output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_nodes = output_dir / "manual_nodes.csv"
    output_edges = output_dir / "manual_edges.csv"
    output_aliases = output_dir / "manual_aliases.csv"

    _write_csv(output_nodes, parsed.nodes)
    _write_csv(output_edges, parsed.edges)
    _write_csv(output_aliases, parsed.aliases)

    return {
        "nodes": output_nodes,
        "edges": output_edges,
        "aliases": output_aliases,
    }
