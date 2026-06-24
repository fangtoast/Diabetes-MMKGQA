"""DiaKG parser for structured mentions and relations."""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import yaml

from .manual_ab_tables import stable_edge_id, stable_node_id


KG_VERSION = "0.2.0"


RELATION_LAYER_BY_NAME = {
    "HAS_SYMPTOM": "A",
    "HAS_CAUSE": "A",
    "HAS_PATHOGENESIS": "A",
    "RECOMMENDS_TEST": "A",
    "HAS_TEST_ITEM": "A",
    "TREATED_BY_DRUG": "A",
    "TREATED_BY_NONDRUG": "A",
    "TREATED_BY_OPERATION": "A",
    "AFFECTS_ANATOMY": "A",
    "HAS_ADVERSE_EFFECT": "A",
    "HAS_DOSE_AMOUNT": "A",
    "HAS_ADMIN_METHOD": "A",
    "HAS_DOSE_FREQUENCY": "A",
    "HAS_DURATION": "A",
    "IS_A": "A",
    "HAS_CLASS": "A",
    "HAS_ICD_CODE": "B",
    "GOVERNED_BY": "B",
    "HAS_STANDARD_RULE": "B",
    "HAS_REFERENCE_RANGE": "B",
    "HAS_UNIT": "B",
    "HAS_DIAGNOSTIC_THRESHOLD": "B",
    "APPLIES_TO": "B",
    "FROM_GUIDELINE": "B",
    "IMAGE_ASSOCIATED_WITH": "C",
    "HAS_IMAGE_GRADE": "C",
    "FROM_DATASET": "C",
    "IN_SPLIT": "C",
    "HAS_CASE": "C",
    "HAS_STAGE": "C",
    "MENTIONED_IN": "C",
    "PART_OF_DOCUMENT": "C",
}


def _sha1(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()


def _normalize_text(value: str) -> str:
    return " ".join((value or "").strip().split())


def _read_manifest(manifest_path: Path) -> dict:
    with manifest_path.open("r", encoding="utf-8-sig") as f:
        payload = yaml.safe_load(f)
    return {item["source_id"]: item for item in payload.get("sources", [])}


def _read_ontology_relation_map(ontology_path: Path | None = None) -> dict:
    ontology_path = ontology_path or (Path(__file__).resolve().parents[3] / "configs" / "ontology.yaml")
    with ontology_path.open("r", encoding="utf-8-sig") as f:
        data = yaml.safe_load(f)
    return data.get("raw_relation_mapping", {})


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


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
        for row in rows:
            writer.writerow(row)


def _relation_defaults(rel: str) -> str:
    return rel or ""


def _normalize_relation(raw_relation: str, mapping: dict[str, dict]) -> Tuple[str, bool]:
    mapping_record = mapping.get(raw_relation)
    if not mapping_record:
        return _relation_defaults(raw_relation), False
    return mapping_record.get("normalized", raw_relation), bool(mapping_record.get("reverse", False))


def _relation_layer(relation: str, relation_mapping: dict) -> str:
    if relation in relation_mapping:
        relation = relation_mapping[relation].get("normalized", relation)
    return RELATION_LAYER_BY_NAME.get(relation, "C")


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
    evidence_id: str,
    extraction_method: str = "diakg_parser",
    confidence: str = "1.0",
    raw_relation: str = "",
    normalized_relation: str = "",
    kg_version: str = KG_VERSION,
) -> str:
    normalized = normalized_relation or relation
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
        "evidence_id": evidence_id,
        "raw_relation": raw_relation or relation,
        "normalized_relation": normalized_relation or relation,
    }
    return edge_id


def _evidence_node_id(sentence_id: str) -> str:
    return stable_node_id("C", "EvidenceChunk", sentence_id)


def _document_node_id(document_id: str) -> str:
    return stable_node_id("C", "Document", document_id)


@dataclass(frozen=True)
class DiakgParseOutputs:
    nodes: List[dict]
    edges: List[dict]
    documents: List[dict]
    evidence: List[dict]
    stats: dict


def _select_diakg_source(repo_root: Path, source_map: dict, source_id: str | None = None) -> str:
    candidates = ["diakg", "manual_diakg_fallback"] if source_id is None else [source_id]
    for sid in candidates:
        source = source_map.get(sid)
        if not source:
            continue
        source_path = repo_root / source["root_file"]
        if source_path.exists():
            return sid
    raise FileNotFoundError("No DiaKG source file available for parser.")


def parse_diakg_records(
    payload: dict,
    source_id: str,
    relation_mapping: dict[str, dict],
) -> DiakgParseOutputs:
    nodes: dict[str, dict] = {}
    edges: dict[str, dict] = {}
    documents: list[dict] = []
    evidence_rows: list[dict] = []

    docs = payload.get("documents", [])
    if not isinstance(docs, list):
        raise ValueError("Payload must include documents list.")

    for document in docs:
        document_id = _normalize_text(document.get("document_id", ""))
        if not document_id:
            continue
        document_title = _normalize_text(document.get("title", ""))
        if not document_title:
            document_title = document_id
        document_node_id = _add_node(
            nodes,
            source_id=source_id,
            node_type="Document",
            canonical_name=document_title,
            knowledge_layer="C",
            extras={
                "source_document_id": document_id,
                "title": document_title,
            },
        )

        documents.append(
            {
                "document_id": document_id,
                "document_node_id": document_node_id,
                "title": document_title,
                "source_id": source_id,
                "kg_version": KG_VERSION,
            }
        )

        paragraphs = document.get("paragraphs", [])
        if not isinstance(paragraphs, list):
            continue

        for paragraph in paragraphs:
            for sentence in paragraph.get("sentences", []) or []:
                sentence_id = _normalize_text(sentence.get("sentence_id", ""))
                if not sentence_id:
                    continue
                text = _normalize_text(sentence.get("text", ""))
                evidence_id = _evidence_node_id(sentence_id)
                evidence_node_id = _add_node(
                    nodes,
                    source_id=source_id,
                    node_type="EvidenceChunk",
                    canonical_name=sentence_id,
                    knowledge_layer="C",
                    extras={
                        "source_sentence_id": sentence_id,
                        "document_id": document_id,
                        "text": text,
                    },
                )

                evidence_rows.append(
                    {
                        "evidence_id": evidence_node_id,
                        "sentence_id": sentence_id,
                        "document_id": document_id,
                        "text": text,
                        "source_id": source_id,
                        "kg_version": KG_VERSION,
                    }
                )

                _add_edge(
                    edges,
                    head_id=evidence_node_id,
                    relation="PART_OF_DOCUMENT",
                    tail_id=document_node_id,
                    source_id=source_id,
                    knowledge_layer=_relation_layer("PART_OF_DOCUMENT", relation_mapping),
                    evidence_id=evidence_node_id,
                    raw_relation="PART_OF_DOCUMENT",
                    normalized_relation="PART_OF_DOCUMENT",
                )

                entity_index: dict[Tuple[str, str], str] = {}
                for entity in sentence.get("entities", []) or []:
                    entity_type = _normalize_text(entity.get("entity_type", ""))
                    canonical = _normalize_text(entity.get("canonical_name", entity.get("text", "")))
                    if not entity_type or not canonical:
                        continue
                    entity_node_id = _add_node(
                        nodes,
                        source_id=source_id,
                        node_type=entity_type,
                        canonical_name=canonical,
                        knowledge_layer="C",
                        extras={
                            "evidence_id": evidence_node_id,
                            "document_id": document_id,
                        },
                    )
                    entity_index[(canonical, entity_type)] = entity_node_id

                for relation in sentence.get("relations", []) or []:
                    raw_relation = _normalize_text(relation.get("relation", ""))
                    if not raw_relation:
                        continue
                    head_text = _normalize_text(relation.get("head", ""))
                    tail_text = _normalize_text(relation.get("tail", ""))
                    if not head_text or not tail_text:
                        continue

                    normalized_relation, reverse = _normalize_relation(raw_relation, relation_mapping)
                    head_candidates = [
                        key for key in entity_index.keys() if key[0] == head_text
                    ]
                    tail_candidates = [
                        key for key in entity_index.keys() if key[0] == tail_text
                    ]
                    # mention relations may point to sentence id
                    if not head_candidates and tail_text == sentence_id:
                        head_id = evidence_node_id
                    else:
                        head_id = entity_index[head_candidates[0]] if head_candidates else None

                    if not tail_candidates and tail_text == sentence_id:
                        tail_id = evidence_node_id
                    else:
                        tail_id = entity_index[tail_candidates[0]] if tail_candidates else None

                    if head_id is None or tail_id is None:
                        continue

                    if reverse:
                        head_id, tail_id = tail_id, head_id

                    if normalized_relation == "HAS_CAUSE":
                        head_node = nodes.get(head_id, {})
                        tail_node = nodes.get(tail_id, {})
                        if head_node.get("node_type") == "Disease" and tail_node.get("node_type") == "Disease":
                            tail_id = _add_node(
                                nodes,
                                source_id=source_id,
                                node_type="Etiology",
                                canonical_name=tail_node.get("canonical_name", tail_text),
                                knowledge_layer="C",
                                extras={"source_sentence_id": sentence_id, "document_id": document_id},
                            )

                    _add_edge(
                        edges,
                        head_id=head_id,
                        relation=normalized_relation,
                        tail_id=tail_id,
                        source_id=source_id,
                        knowledge_layer=_relation_layer(normalized_relation, relation_mapping),
                        extraction_method="diakg_parser",
                        confidence="1.0",
                        evidence_id=evidence_node_id,
                        raw_relation=raw_relation,
                        normalized_relation=normalized_relation,
                    )

    return DiakgParseOutputs(
        nodes=sorted(nodes.values(), key=lambda x: x["node_id"]),
        edges=sorted(edges.values(), key=lambda x: x["edge_id"]),
        documents=sorted(documents, key=lambda x: x["document_id"]),
        evidence=sorted(evidence_rows, key=lambda x: x["evidence_id"]),
        stats={
            "node_count": len(nodes),
            "edge_count": len(edges),
            "document_count": len(documents),
            "evidence_count": len(evidence_rows),
            "kg_version": KG_VERSION,
        },
    )


def parse_diakg(
    repo_root: Path,
    *,
    source_id: str | None = None,
    manifest_path: Path | None = None,
    ontology_path: Path | None = None,
) -> DiakgParseOutputs:
    manifest = _read_manifest(manifest_path or (repo_root / "data" / "source_manifest.yaml"))
    selected_source_id = _select_diakg_source(repo_root, manifest, source_id)
    source = manifest[selected_source_id]
    payload = _load_json(repo_root / source["root_file"])
    if source.get("source_id") != selected_source_id:
        payload["source_id"] = selected_source_id
    relation_mapping = _read_ontology_relation_map(ontology_path)
    return parse_diakg_records(payload, selected_source_id, relation_mapping)


def export_diakg_interim_outputs(parsed: DiakgParseOutputs, output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    out_nodes = output_dir / "diakg_nodes.csv"
    out_edges = output_dir / "diakg_edges.csv"
    out_documents = output_dir / "diakg_documents.csv"
    out_evidence = output_dir / "diakg_evidence.csv"

    _write_csv(out_nodes, parsed.nodes)
    _write_csv(out_edges, parsed.edges)
    _write_csv(out_documents, parsed.documents)
    _write_csv(out_evidence, parsed.evidence)
    return {
        "nodes": out_nodes,
        "edges": out_edges,
        "documents": out_documents,
        "evidence": out_evidence,
    }
