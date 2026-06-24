"""RetinaMNIST parser for image metadata and labels."""

from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import List

import yaml

from .manual_ab_tables import stable_edge_id, stable_node_id


KG_VERSION = "0.2.0"

GRADE_LABELS = {
    0: "No_DR",
    1: "Mild_non_proliferative_DR",
    2: "Moderate_non_proliferative_DR",
    3: "Severe_non_proliferative_DR",
    4: "Proliferative_DR",
}

RELATION_LAYER_BY_NAME = {
    "IMAGE_ASSOCIATED_WITH": "C",
    "HAS_IMAGE_GRADE": "C",
    "FROM_DATASET": "C",
    "IN_SPLIT": "C",
}

DISEASE_CANONICAL_NAME = "diabetic retinopathy"
DATASET_CANONICAL_NAME = "RetinaMNIST+"


def _sha1(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()


def _normalize_text(value: str) -> str:
    return " ".join((value or "").strip().split())


def _to_int_or_none(value) -> int | None:
    if isinstance(value, bool):
        return int(value)
    if hasattr(value, "item"):
        try:
            value = value.item()
        except Exception:
            pass
    if isinstance(value, (tuple, list)):
        if not value:
            return None
        return _to_int_or_none(value[0])
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _read_manifest(manifest_path: Path) -> dict:
    with manifest_path.open("r", encoding="utf-8-sig") as f:
        payload = yaml.safe_load(f)
    return {item["source_id"]: item for item in payload.get("sources", [])}


def _read_npz_like_payload(path: Path) -> dict:
    try:
        import numpy as np
    except Exception as exc:
        raise RuntimeError("numpy is required to parse RetinaMNIST npz files.") from exc

    with np.load(path, allow_pickle=False) as payload:
        return {key: payload[key] for key in payload.files}


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


def _iter_key_candidates(split_name: str, kind: str) -> list[str]:
    key = split_name.strip().lower()
    variants = []
    if split_name == "val":
        variants.extend([f"{key}_images", f"{key}_label", f"val_{kind}", f"valid_{kind}", f"validation_{kind}"])
    if split_name == "test":
        variants.extend([f"{key}_images", f"{key}_label", f"test_{kind}"])
    if split_name == "train":
        variants.extend([f"{key}_{kind}", f"train_{kind}", f"training_{kind}"])
    variants.extend([f"{key}{kind}", f"{kind}_{key}", f"{kind}"])
    return variants


def _find_split_payload(payload: dict, split_name: str, kind: str) -> list | None:
    keys = set(payload.keys())
    exact_candidates = _iter_key_candidates(split_name, kind)
    for candidate in exact_candidates:
        if candidate in keys:
            return list(payload[candidate])
    for key in sorted(keys):
        lower = key.lower()
        if split_name in lower and kind in lower:
            return list(payload[key])
    return None


def _find_split_key(payload: dict, split_name: str, kind: str) -> str | None:
    keys = payload.keys()
    exact_candidates = _iter_key_candidates(split_name, kind)
    for candidate in exact_candidates:
        if candidate in keys:
            return candidate
    for key in sorted(keys):
        lower = key.lower()
        if split_name in lower and kind in lower:
            return key
    return None


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
    extraction_method: str = "retinamnist_parser",
    confidence: str = "1.0",
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
        "evidence_id": evidence_id,
        "raw_relation": raw_relation or relation,
        "normalized_relation": normalized_relation or relation,
    }
    return edge_id


@dataclass(frozen=True)
class RetinaMNISTParseOutputs:
    nodes: List[dict]
    edges: List[dict]
    images: List[dict]
    stats: dict


def parse_retinamnist_records(payload: dict, source_id: str) -> RetinaMNISTParseOutputs:
    nodes: dict[str, dict] = {}
    edges: dict[str, dict] = {}
    image_rows: list[dict] = []

    dataset_id = _add_node(
        nodes,
        source_id=source_id,
        node_type="Dataset",
        canonical_name=DATASET_CANONICAL_NAME,
        knowledge_layer="C",
        extras={"description": "MedMNIST RetinaMNIST+"},
    )

    disease_id = _add_node(
        nodes,
        source_id=source_id,
        node_type="Disease",
        canonical_name=DISEASE_CANONICAL_NAME,
        knowledge_layer="C",
        extras={"description": "Diabetes-related vision complication"},
    )

    split_nodes: dict[str, str] = {}
    grade_nodes: dict[str, str] = {}

    for split_name in ("train", "val", "test"):
        images = _find_split_payload(payload, split_name, "images")
        labels = _find_split_payload(payload, split_name, "labels")
        if images is None or labels is None:
            continue

        image_key = _find_split_key(payload, split_name, "images")
        label_key = _find_split_key(payload, split_name, "labels")
        split_node_name = "validation" if split_name == "val" else split_name
        split_node_id = split_nodes.get(split_node_name)
        if split_node_id is None:
            split_node_id = _add_node(
                nodes,
                source_id=source_id,
                node_type="DataSplit",
                canonical_name=split_node_name,
                knowledge_layer="C",
                extras={"description": f"{split_node_name} split"},
            )
            split_nodes[split_node_name] = split_node_id

        limit = min(len(images), len(labels))
        for index in range(limit):
            image_id = stable_node_id("C", "Image", f"{split_name}_{index}")
            grade = _to_int_or_none(labels[index])
            grade_label = GRADE_LABELS.get(grade, f"Unknown_{grade}")
            grade_node_name = f"{DATASET_CANONICAL_NAME}:{grade_label}"
            grade_node_id = grade_nodes.get(grade_node_name)
            if grade_node_id is None:
                grade_node_id = _add_node(
                    nodes,
                    source_id=source_id,
                    node_type="ImageGrade",
                    canonical_name=grade_node_name,
                    knowledge_layer="C",
                    extras={"grade_code": str(grade), "source_id_hint": source_id},
                )
                grade_nodes[grade_node_name] = grade_node_id

            image_node_id = stable_node_id(
                "C",
                "Image",
                f"{DATASET_CANONICAL_NAME}_{split_name}_{index:06d}",
            )
            if image_node_id not in nodes:
                nodes[image_node_id] = {
                    "node_id": image_node_id,
                    "node_type": "Image",
                    "canonical_name": f"{DATASET_CANONICAL_NAME} image {split_name} {index:06d}",
                    "knowledge_layer": "C",
                    "source_ids": source_id,
                    "kg_version": KG_VERSION,
                    "split": split_name,
                    "grade_code": str(grade),
                    "image_index": str(index),
                    "image_key": image_key or "",
                    "label_key": label_key or "",
                }

            evidence_id = _sha1("|".join([source_id, split_name, str(index)]))
            _add_edge(
                edges,
                head_id=image_node_id,
                relation="IMAGE_ASSOCIATED_WITH",
                tail_id=disease_id,
                source_id=source_id,
                knowledge_layer=RELATION_LAYER_BY_NAME["IMAGE_ASSOCIATED_WITH"],
                evidence_id=evidence_id,
                raw_relation="IMAGE_ASSOCIATED_WITH",
                normalized_relation="IMAGE_ASSOCIATED_WITH",
            )
            _add_edge(
                edges,
                head_id=image_node_id,
                relation="HAS_IMAGE_GRADE",
                tail_id=grade_node_id,
                source_id=source_id,
                knowledge_layer=RELATION_LAYER_BY_NAME["HAS_IMAGE_GRADE"],
                evidence_id=evidence_id,
                raw_relation="HAS_IMAGE_GRADE",
                normalized_relation="HAS_IMAGE_GRADE",
            )
            _add_edge(
                edges,
                head_id=image_node_id,
                relation="FROM_DATASET",
                tail_id=dataset_id,
                source_id=source_id,
                knowledge_layer=RELATION_LAYER_BY_NAME["FROM_DATASET"],
                evidence_id=evidence_id,
                raw_relation="FROM_DATASET",
                normalized_relation="FROM_DATASET",
            )
            _add_edge(
                edges,
                head_id=image_node_id,
                relation="IN_SPLIT",
                tail_id=split_node_id,
                source_id=source_id,
                knowledge_layer=RELATION_LAYER_BY_NAME["IN_SPLIT"],
                evidence_id=evidence_id,
                raw_relation="IN_SPLIT",
                normalized_relation="IN_SPLIT",
            )

            image_rows.append(
                {
                    "image_id": image_node_id,
                    "source_id": source_id,
                    "split": split_name,
                    "grade": grade_label,
                    "grade_code": str(grade),
                    "dataset": DATASET_CANONICAL_NAME,
                    "source_file": f"{split_name}_images",
                    "image_index": str(index),
                    "kg_version": KG_VERSION,
                    "evidence_id": evidence_id,
                }
            )

    return RetinaMNISTParseOutputs(
        nodes=sorted(nodes.values(), key=lambda x: x["node_id"]),
        edges=sorted(edges.values(), key=lambda x: x["edge_id"]),
        images=sorted(image_rows, key=lambda x: x["image_id"]),
        stats={
            "node_count": len(nodes),
            "edge_count": len(edges),
            "image_count": len(image_rows),
            "kg_version": KG_VERSION,
        },
    )


def parse_retinamnist(
    repo_root: Path,
    *,
    source_id: str | None = None,
    manifest_path: Path | None = None,
) -> RetinaMNISTParseOutputs:
    manifest = _read_manifest(manifest_path or (repo_root / "data" / "source_manifest.yaml"))
    selected_source = source_id or "retinamnist"
    if selected_source not in manifest:
        raise KeyError(f"{selected_source} is missing in source manifest.")

    source = manifest[selected_source]
    source_path = repo_root / source["root_file"]
    if not source_path.exists():
        raise FileNotFoundError(f"RetinaMNIST source file missing: {source_path}")

    payload = _read_npz_like_payload(source_path)
    return parse_retinamnist_records(payload, selected_source)


def export_retinamnist_interim_outputs(parsed: RetinaMNISTParseOutputs, output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    out_nodes = output_dir / "retinamnist_nodes.csv"
    out_edges = output_dir / "retinamnist_edges.csv"
    out_images = output_dir / "retinamnist_images.csv"

    _write_csv(out_nodes, parsed.nodes)
    _write_csv(out_edges, parsed.edges)
    _write_csv(out_images, parsed.images)

    return {
        "nodes": out_nodes,
        "edges": out_edges,
        "images": out_images,
    }
