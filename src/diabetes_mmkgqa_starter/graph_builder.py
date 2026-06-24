"""Portable graph build and export pipeline."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import dataclass
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List

import pandas as pd
import yaml

from diabetes_mmkgqa_starter.ingestion import (
    diakg_parser,
    manual_ab_tables,
    pneumoniamnist_parser,
    retinamnist_parser,
)
from diabetes_mmkgqa_starter.normalization import alias_loader

KG_VERSION = "0.2.0"


@dataclass(frozen=True)
class GraphBuildOutputs:
    nodes: List[dict]
    edges: List[dict]
    documents: List[dict]
    evidence: List[dict]
    images: List[dict]
    stats: dict
    schema: dict
    output_files: dict[str, Path]


def _read_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as f:
        return yaml.safe_load(f)


def _write_csv(path: Path, rows: list[dict], *, fieldnames: list[str] | None = None) -> None:
    if not rows:
        path.parent.mkdir(parents=True, exist_ok=True)
        if fieldnames is None:
            fieldnames = []
        with path.open("w", encoding="utf-8-sig", newline="") as f:
            if fieldnames:
                csv.DictWriter(f, fieldnames=fieldnames).writeheader()
            return

    all_fields = sorted({k for row in rows for k in row.keys()}) if fieldnames is None else fieldnames
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=all_fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(
            _to_jsonable(payload),
            f,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )


def _to_jsonable(value: object):
    if isinstance(value, set):
        return sorted(value)
    if isinstance(value, tuple):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {k: _to_jsonable(v) for k, v in value.items()}
    return value


def _write_parquet(path: Path, rows: list[dict], *, columns: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        df = pd.DataFrame(columns=columns or [])
        df.to_parquet(path, index=False)
        return
    df = pd.DataFrame(rows)
    if columns is not None:
        for col in columns:
            if col not in df:
                df[col] = ""
        df = df[columns]
    df.to_parquet(path, index=False)


def _write_graphml(path: Path, nodes: list[dict], edges: list[dict]) -> None:
    try:
        import networkx as nx
    except Exception as exc:
        raise RuntimeError("networkx required for graphml export.") from exc

    graph = nx.DiGraph()
    for node in nodes:
        node_id = node.get("node_id", "")
        if not node_id:
            continue
        attributes = {k: str(v) for k, v in node.items() if k != "node_id"}
        graph.add_node(node_id, **attributes)

    for edge in edges:
        head = edge.get("head_id", "")
        tail = edge.get("tail_id", "")
        if not head or not tail:
            continue
        attributes = {k: str(v) for k, v in edge.items() if k not in {"head_id", "tail_id", "edge_id"}}
        graph.add_edge(head, tail, edge_id=edge.get("edge_id", ""), **attributes)

    path.parent.mkdir(parents=True, exist_ok=True)
    nx.write_graphml(graph, path)


def _stable_merge_row_lists(*rows_groups: Iterable[dict], key: str) -> list[dict]:
    merged: dict[str, dict] = {}
    for rows in rows_groups:
        for row in rows:
            record_id = row.get(key, "")
            if not record_id:
                continue
            merged.setdefault(record_id, dict(row))

            existing = merged[record_id]
            if key == "node_id":
                existing_sources = _split_source_ids(existing.get("source_ids", ""))
                incoming_sources = _split_source_ids(row.get("source_ids", ""))
                merged_sources = sorted(existing_sources | incoming_sources)
                existing["source_ids"] = "|".join(merged_sources)

                for field, value in row.items():
                    if field == key:
                        continue
                    if field == "source_ids":
                        continue
                    if existing.get(field, "") == "":
                        existing[field] = value
            else:
                for field, value in row.items():
                    if existing.get(field, "") == "" and value != "":
                        existing[field] = value

    if key == "node_id":
        return sorted(merged.values(), key=lambda x: x["node_id"])
    if key == "edge_id":
        return sorted(merged.values(), key=lambda x: x["edge_id"])
    if key == "document_id":
        return sorted(merged.values(), key=lambda x: x["document_id"])
    if key == "evidence_id":
        return sorted(merged.values(), key=lambda x: x["evidence_id"])
    return sorted(merged.values(), key=lambda x: next(iter(x.values()), ""))


def _split_source_ids(value: str | list[str] | None) -> set[str]:
    if not value:
        return set()
    if isinstance(value, list):
        return {v for v in value if v}
    return {item.strip() for item in str(value).split("|") if item.strip()}


def _normalize_records(
    nodes: list[dict],
    edges: list[dict],
    documents: list[dict],
    evidence: list[dict],
    images: list[dict],
    alias_index: dict[tuple[str, str], str] | None = None,
) -> tuple[list[dict], list[dict], list[dict], list[dict], list[dict]]:
    alias_index = alias_index or {}
    canonical_map: dict[str, tuple[str, str]] = {}
    for (node_type, alias), canonical in alias_index.items():
        canonical_map[(str(node_type).lower(), alias)] = canonical

    normalized_nodes: list[dict] = []
    node_id_remap: dict[str, str] = {}
    for row in nodes:
        node = dict(row)
        node_type = str(node.get("node_type", "")).strip()
        canonical_name = str(node.get("canonical_name", "")).strip()
        node_id = str(node.get("node_id", "")).strip()
        if node_type and canonical_name:
            mapped = canonical_map.get((node_type.lower(), canonical_name.lower()))
            if mapped:
                new_canonical = mapped
                node["canonical_name"] = new_canonical
                # stable node id may be precomputed with old name; rewrite if possible
                if node.get("knowledge_layer"):
                    node["node_id"] = manual_ab_tables.stable_node_id(node["knowledge_layer"], node_type, new_canonical)
                else:
                    node["node_id"] = node.get("node_id", "")
                if node_id and node_id != node["node_id"]:
                    node_id_remap[node_id] = node["node_id"]
        normalized_nodes.append(node)

    # remap edges that may reference old node ids after alias normalization
    node_id_lookup = {row.get("node_id", ""): row.get("node_id", "") for row in normalized_nodes}
    node_id_lookup.update(node_id_remap)
    for row in edges:
        row["head_id"] = row.get("head_id", "")
        row["tail_id"] = row.get("tail_id", "")
        row["head_id"] = node_id_lookup.get(row["head_id"], row["head_id"])
        row["tail_id"] = node_id_lookup.get(row["tail_id"], row["tail_id"])

    return (
        sorted(normalized_nodes, key=lambda x: x["node_id"]),
        sorted(edges, key=lambda x: x["edge_id"]),
        sorted(documents, key=lambda x: x["document_id"]),
        sorted(evidence, key=lambda x: x["evidence_id"]),
        sorted(images, key=lambda x: x["image_id"]),
    )


def _node_counts_by_layer(rows: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        layer = row.get("knowledge_layer", "UNKNOWN")
        counts[layer] = counts.get(layer, 0) + 1
    return counts


def _edge_counts_by_layer(rows: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        layer = row.get("knowledge_layer", "UNKNOWN")
        counts[layer] = counts.get(layer, 0) + 1
    return counts


def _relation_counts(rows: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        relation = row.get("relation", "")
        counts[relation] = counts.get(relation, 0) + 1
    return counts


def _validate_graph_schema(
    ontology: dict,
    nodes: list[dict],
    edges: list[dict],
    images: list[dict],
    repo_root: Path,
) -> dict:
    node_type_by_id: dict[str, str] = {row.get("node_id", ""): row.get("node_type", "") for row in nodes}
    relations_def = ontology.get("relations", {})
    required_node_properties = ontology.get("required_node_properties", [])
    required_edge_properties = ontology.get("required_edge_properties", [])
    required_evidence_properties = ontology.get("required_evidence_relation_properties", [])
    unknown_relation_count = Counter()

    missing_node_properties: list[dict] = []
    for row in nodes:
        missing = [field for field in required_node_properties if field and not row.get(field)]
        if missing:
            missing_node_properties.append({"node_id": row["node_id"], "missing": missing})

    missing_edge_properties: list[dict] = []
    for row in edges:
        missing = [field for field in required_edge_properties if field and not row.get(field)]
        if missing:
            missing_edge_properties.append({"edge_id": row["edge_id"], "missing": missing})

    missing_evidence_properties = 0
    for row in edges:
        raw_relation = row.get("raw_relation", "")
        if raw_relation == "mention" or raw_relation in {"MENTIONED_IN", "PART_OF_DOCUMENT"}:
            missing = [field for field in required_evidence_properties if not row.get(field)]
            if missing:
                missing_evidence_properties += 1

    relation_violations: list[dict] = []
    missing_endpoint_edges: list[dict] = []
    for row in edges:
        relation = row.get("relation", "")
        relation_def = relations_def.get(relation)
        if not relation_def:
            unknown_relation_count[relation] += 1
            relation_violations.append(
                {
                    "edge_id": row.get("edge_id"),
                    "relation": relation,
                    "reason": "relation_not_in_ontology",
                }
            )
            continue
        head_type = node_type_by_id.get(row.get("head_id"), "")
        tail_type = node_type_by_id.get(row.get("tail_id"), "")
        head_id = row.get("head_id", "")
        tail_id = row.get("tail_id", "")
        if not head_id or not tail_id:
            missing_endpoint_edges.append(
                {
                    "edge_id": row.get("edge_id"),
                    "relation": relation,
                    "head_id": head_id,
                    "tail_id": tail_id,
                    "reason": "missing_head_or_tail_id",
                }
            )
            continue
        if head_id not in node_type_by_id:
            missing_endpoint_edges.append(
                {
                    "edge_id": row.get("edge_id"),
                    "relation": relation,
                    "head_id": head_id,
                    "reason": "missing_head_node",
                }
            )
        if tail_id not in node_type_by_id:
            missing_endpoint_edges.append(
                {
                    "edge_id": row.get("edge_id"),
                    "relation": relation,
                    "tail_id": tail_id,
                    "reason": "missing_tail_node",
                }
            )
        domain = set(relation_def.get("domain", []))
        range_ = set(relation_def.get("range", []))
        if domain and "*" not in domain and head_type not in domain:
            relation_violations.append(
                {
                    "edge_id": row.get("edge_id", ""),
                    "relation": relation,
                    "reason": "head_type_mismatch",
                    "head_type": head_type,
                    "allowed_domain": sorted(domain),
                }
            )
        if range_ and "*" not in range_ and tail_type not in range_:
            relation_violations.append(
                {
                    "edge_id": row.get("edge_id", ""),
                    "relation": relation,
                    "reason": "tail_type_mismatch",
                    "tail_type": tail_type,
                    "allowed_range": sorted(range_),
                }
            )

    duplicate_node_ids = [
        {"node_id": node_id, "count": count}
        for node_id, count in Counter((row.get("node_id", "") for row in nodes if row.get("node_id", ""))).items()
        if count > 1
    ]
    duplicate_edge_ids = [
        {"edge_id": edge_id, "count": count}
        for edge_id, count in Counter((row.get("edge_id", "") for row in edges if row.get("edge_id", ""))).items()
        if count > 1
    ]
    self_loops = [
        {
            "edge_id": row.get("edge_id", ""),
            "head_tail": row.get("head_id", ""),
            "relation": row.get("relation", ""),
        }
        for row in edges
        if row.get("head_id", "") and row.get("head_id", "") == row.get("tail_id", "")
    ]

    image_path_violations: list[dict] = []
    for row in images:
        rel_path = str(row.get("relative_path", "")).strip()
        if not rel_path:
            continue
        rel_path_obj = Path(rel_path)
        if rel_path_obj.is_absolute():
            image_path_violations.append(
                {
                    "image_id": row.get("image_id", ""),
                    "relative_path": rel_path,
                    "reason": "absolute_path",
                }
            )
            continue
        candidate = (repo_root / rel_path_obj).resolve()
        if not candidate.exists():
            image_path_violations.append(
                {
                    "image_id": row.get("image_id", ""),
                    "relative_path": rel_path,
                    "reason": "file_not_found",
                }
            )

    unknown_relation_counts = [{"relation": rel, "count": count} for rel, count in unknown_relation_count.items()]

    return {
        "required_node_properties": required_node_properties,
        "required_edge_properties": required_edge_properties,
        "required_evidence_relation_properties": required_evidence_properties,
        "nodes_missing_required_properties": missing_node_properties[:100],
        "edges_missing_required_properties": missing_edge_properties[:100],
        "evidence_relation_missing_required_properties": missing_evidence_properties,
        "duplicate_node_ids": duplicate_node_ids,
        "duplicate_edge_ids": duplicate_edge_ids,
        "missing_endpoint_edges": missing_endpoint_edges[:100],
        "self_loops": self_loops[:100],
        "image_path_violations": image_path_violations[:100],
        "unknown_relation_counts": unknown_relation_counts,
        "relation_violations": relation_violations[:100],
        "relation_domain_range_violations": relation_violations[:100],
        "domain_range_violation_count": len(relation_violations),
        "self_loop_count": len(self_loops),
        "missing_endpoint_count": len(missing_endpoint_edges),
        "image_path_violation_count": len(image_path_violations),
        "counts": {
            "nodes_by_type": {k: len([n for n in nodes if n.get("node_type") == k]) for k in sorted({n.get("node_type", "") for n in nodes})},
            "relations": _relation_counts(edges),
            "sources": {
                "node_source_ids": _to_jsonable(
                    _split_source_ids("|".join([row.get("source_ids", "") for row in nodes]))
                ),
                "edge_source_ids": _to_jsonable(
                    _split_source_ids("|".join([row.get("source_id", "") for row in edges]))
                ),
            },
        },
    }


def _build_stats(
    nodes: list[dict],
    edges: list[dict],
    documents: list[dict],
    evidence: list[dict],
    images: list[dict],
    ontology: dict,
    warnings: list[str],
    repo_root: Path,
) -> dict:
    unique_entities = {(row.get("node_type"), row.get("canonical_name")) for row in nodes}
    unique_triples = {(row.get("head_id"), row.get("relation"), row.get("tail_id")) for row in edges}
    provenance_relations = {"MENTIONED_IN", "PART_OF_DOCUMENT"}
    evidence_backed = [row for row in edges if str(row.get("evidence_id", "")).strip()]
    provenance = [row for row in edges if row.get("relation") in provenance_relations]
    triple_layers = {
        "A": len([edge for edge in edges if edge.get("knowledge_layer") == "A"]),
        "B": len([edge for edge in edges if edge.get("knowledge_layer") == "B"]),
        "C": len([edge for edge in edges if edge.get("knowledge_layer") == "C"]),
    }

    schema_issues = _validate_graph_schema(ontology, nodes, edges, images, repo_root)
    return {
        "kg_version": KG_VERSION,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "document_count": len(documents),
        "evidence_count": len(evidence),
        "image_node_count": len([row for row in nodes if row.get("node_type") == "Image"]),
        "image_metadata_count": len(images),
        "canonical_entity_count": len(unique_entities),
        "unique_semantic_triples_count": len(unique_triples),
        "evidence_backed_relation_claim_count": len(evidence_backed),
        "provenance_edge_count": len(provenance),
        "node_layer_counts": _node_counts_by_layer(nodes),
        "edge_layer_counts": _edge_counts_by_layer(edges),
        "triple_layer_counts": triple_layers,
        "warnings": warnings,
        "schema_validation": schema_issues,
        "quality_gate": {
            "duplicate_node_ids": schema_issues.get("duplicate_node_ids", []),
            "duplicate_edge_ids": schema_issues.get("duplicate_edge_ids", []),
            "self_loops": schema_issues.get("self_loops", []),
            "missing_endpoints": schema_issues.get("missing_endpoint_edges", []),
            "domain_range_violations": schema_issues.get("relation_violations", []),
            "image_path_violations": schema_issues.get("image_path_violations", []),
            "passed": all(
                [
                    not schema_issues.get("duplicate_node_ids"),
                    not schema_issues.get("duplicate_edge_ids"),
                    schema_issues.get("self_loop_count", 0) == 0,
                    schema_issues.get("missing_endpoint_count", 0) == 0,
                    schema_issues.get("image_path_violation_count", 0) == 0,
                ]
            ),
        },
    }


def _build_graph_records(
    repo_root: Path,
    include_manual: bool = True,
    include_diakg: bool = True,
    include_retina: bool = True,
    include_pneumonia: bool = True,
    manifest_path: Path | None = None,
    ontology_path: Path | None = None,
) -> tuple[list[dict], list[dict], list[dict], list[dict], list[dict], list[str], dict]:
    manifest_path = manifest_path or (repo_root / "data" / "source_manifest.yaml")
    ontology_path = ontology_path or (repo_root / "configs" / "ontology.yaml")
    manifest = _read_yaml(manifest_path)
    ontology = _read_yaml(ontology_path)
    source_map = {item["source_id"]: item for item in manifest.get("sources", [])}

    all_nodes: list[dict] = []
    all_edges: list[dict] = []
    all_documents: list[dict] = []
    all_evidence: list[dict] = []
    all_images: list[dict] = []
    warnings: list[str] = []

    aliases = alias_loader.parse_aliases(repo_root, source_id="manual_aliases", manifest_path=manifest_path)
    alias_index = aliases.alias_index

    if include_manual:
        manual = manual_ab_tables.parse_manual_sources(repo_root, manifest_path=manifest_path)
        all_nodes.extend(manual.nodes)
        all_edges.extend(manual.edges)

    if include_diakg:
        try:
            selected = source_map.get("diakg")
            if selected is not None and (repo_root / selected["root_file"]).exists():
                diakg = diakg_parser.parse_diakg(repo_root, source_id="diakg", manifest_path=manifest_path)
            else:
                diakg = diakg_parser.parse_diakg(repo_root, source_id="manual_diakg_fallback", manifest_path=manifest_path)
            all_nodes.extend(diakg.nodes)
            all_edges.extend(diakg.edges)
            all_documents.extend(diakg.documents)
            all_evidence.extend(diakg.evidence)
        except Exception as exc:
            warnings.append(f"DiKG parser skipped: {exc}")

    if include_retina:
        selected = source_map.get("retinamnist")
        if selected is not None:
            retina_root = repo_root / selected["root_file"]
            if retina_root.exists():
                retina = retinamnist_parser.parse_retinamnist(repo_root, source_id="retinamnist", manifest_path=manifest_path)
                all_nodes.extend(retina.nodes)
                all_edges.extend(retina.edges)
                all_images.extend(retina.images)
            else:
                warnings.append("RetinaMNIST root file missing; image parser skipped.")
        else:
            warnings.append("retinamnist source config missing; image parser skipped.")

    if include_pneumonia:
        selected = source_map.get("pneumoniamnist")
        if selected is not None:
            pneumonia_root = repo_root / selected["root_file"]
            if pneumonia_root.exists():
                pneum = pneumoniamnist_parser.parse_pneumoniamnist(
                    repo_root,
                    source_id="pneumoniamnist",
                    manifest_path=manifest_path,
                )
                all_nodes.extend(pneum.nodes)
                all_edges.extend(pneum.edges)
                all_images.extend(pneum.images)
            else:
                warnings.append("PneumoniaMNIST root file missing; image parser skipped.")
        else:
            warnings.append("pneumoniamnist source config missing; image parser skipped.")

    all_nodes, all_edges, all_documents, all_evidence, all_images = _normalize_records(
        all_nodes, all_edges, all_documents, all_evidence, all_images, alias_index=alias_index
    )

    merged_nodes = _stable_merge_row_lists(all_nodes, key="node_id")
    merged_edges = _stable_merge_row_lists(all_edges, key="edge_id")
    merged_documents = _stable_merge_row_lists(all_documents, key="document_id")
    merged_evidence = _stable_merge_row_lists(all_evidence, key="evidence_id")
    merged_images = _stable_merge_row_lists(all_images, key="image_id")

    stats = _build_stats(
        merged_nodes,
        merged_edges,
        merged_documents,
        merged_evidence,
        merged_images,
        ontology,
        warnings,
        repo_root,
    )
    return merged_nodes, merged_edges, merged_documents, merged_evidence, merged_images, warnings, ontology


def _triples_rows(edges: list[dict]) -> list[dict]:
    triples: list[dict] = []
    for edge in edges:
        triples.append(
            {
                "head_id": edge.get("head_id", ""),
                "relation": edge.get("relation", ""),
                "tail_id": edge.get("tail_id", ""),
                "evidence_id": edge.get("evidence_id", ""),
                "source_id": edge.get("source_id", ""),
                "kg_version": edge.get("kg_version", KG_VERSION),
                "knowledge_layer": edge.get("knowledge_layer", ""),
            }
        )
    return sorted(triples, key=lambda x: (x["head_id"], x["relation"], x["tail_id"], x["source_id"]))


def build_graph_outputs(
    repo_root: Path,
    *,
    output_dir: Path | None = None,
    manifest_path: Path | None = None,
    ontology_path: Path | None = None,
    include_manual: bool = True,
    include_diakg: bool = True,
    include_retina: bool = True,
    include_pneumonia: bool = True,
) -> GraphBuildOutputs:
    repo_root = repo_root.resolve()
    output_dir = (output_dir or (repo_root / "data" / "processed")).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    nodes, edges, documents, evidence, images, warnings, ontology = _build_graph_records(
        repo_root,
        include_manual=include_manual,
        include_diakg=include_diakg,
        include_retina=include_retina,
        include_pneumonia=include_pneumonia,
        manifest_path=manifest_path,
        ontology_path=ontology_path,
    )

    triples = _triples_rows(edges)
    schema = _validate_graph_schema(ontology, nodes, edges, images, repo_root)
    stats = _build_stats(nodes, edges, documents, evidence, images, ontology, warnings, repo_root)

    output_files: dict[str, Path] = {}
    output_files["nodes_csv"] = output_dir / "nodes.csv"
    output_files["nodes_parquet"] = output_dir / "nodes.parquet"
    output_files["edges_csv"] = output_dir / "edges.csv"
    output_files["edges_parquet"] = output_dir / "edges.parquet"
    output_files["triples_tsv"] = output_dir / "triples.tsv"
    output_files["documents_csv"] = output_dir / "documents.csv"
    output_files["documents_parquet"] = output_dir / "documents.parquet"
    output_files["evidence_csv"] = output_dir / "evidence.csv"
    output_files["evidence_parquet"] = output_dir / "evidence.parquet"
    output_files["images_csv"] = output_dir / "images.csv"
    output_files["images_parquet"] = output_dir / "images.parquet"
    output_files["schema_json"] = output_dir / "schema.json"
    output_files["stats_json"] = output_dir / "stats.json"
    output_files["graphml"] = output_dir / "graph.graphml"

    _write_csv(output_files["nodes_csv"], nodes)
    _write_csv(output_files["edges_csv"], edges)
    _write_csv(
        output_files["triples_tsv"],
        triples,
        fieldnames=["head_id", "relation", "tail_id", "evidence_id", "source_id", "kg_version", "knowledge_layer"],
    )
    _write_csv(output_files["documents_csv"], documents)
    _write_csv(output_files["evidence_csv"], evidence)
    _write_csv(output_files["images_csv"], images)

    _write_parquet(output_files["nodes_parquet"], nodes, columns=sorted({k for row in nodes for k in row.keys()}))
    _write_parquet(output_files["edges_parquet"], edges, columns=sorted({k for row in edges for k in row.keys()}))
    _write_parquet(output_files["documents_parquet"], documents, columns=sorted({k for row in documents for k in row.keys()}))
    _write_parquet(output_files["evidence_parquet"], evidence, columns=sorted({k for row in evidence for k in row.keys()}))
    _write_parquet(output_files["images_parquet"], images, columns=sorted({k for row in images for k in row.keys()}))

    schema_payload = {
        "kg_version": KG_VERSION,
        "ontology": ontology.get("version"),
        "project_domain": ontology.get("project_domain"),
        "node_counts": schema.get("counts", {}).get("nodes_by_type", {}),
        "edge_counts": schema.get("counts", {}).get("relations", {}),
        "relation_violations": schema.get("relation_domain_range_violations", []),
        "missing_node_property_records": schema.get("nodes_missing_required_properties", []),
        "missing_edge_property_records": schema.get("edges_missing_required_properties", []),
        "quality_gate": {
            "passed": not schema.get("duplicate_node_ids")
            and not schema.get("duplicate_edge_ids")
            and schema.get("self_loop_count", 0) == 0
            and schema.get("missing_endpoint_count", 0) == 0
            and schema.get("image_path_violation_count", 0) == 0,
            "duplicate_node_ids": schema.get("duplicate_node_ids", []),
            "duplicate_edge_ids": schema.get("duplicate_edge_ids", []),
            "self_loops": schema.get("self_loops", []),
            "missing_endpoints": schema.get("missing_endpoint_edges", []),
            "relation_violations": schema.get("relation_violations", []),
            "image_path_violations": schema.get("image_path_violations", []),
            "unknown_relation_counts": schema.get("unknown_relation_counts", []),
        },
    }
    _write_json(output_files["schema_json"], schema_payload)
    _write_json(output_files["stats_json"], stats)
    _write_graphml(output_files["graphml"], nodes, edges)

    return GraphBuildOutputs(
        nodes=nodes,
        edges=edges,
        documents=documents,
        evidence=evidence,
        images=images,
        stats=stats,
        schema=schema_payload,
        output_files=output_files,
    )


def _file_md5(path: Path) -> str:
    hasher = hashlib.md5()
    hasher.update(path.read_bytes())
    return hasher.hexdigest()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build portable knowledge-graph exports.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-dir", default=str(Path("data") / "processed"))
    parser.add_argument("--skip-diakg", action="store_true")
    parser.add_argument("--skip-retina", action="store_true")
    parser.add_argument("--skip-pneumonia", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    output_dir = Path(args.output_dir)

    build_graph_outputs(
        repo_root,
        output_dir=output_dir,
        include_diakg=not args.skip_diakg,
        include_retina=not args.skip_retina,
        include_pneumonia=not args.skip_pneumonia,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
