from __future__ import annotations

from pathlib import Path
import csv

import pytest
import yaml
pytest.importorskip("fastapi", reason="FastAPI is required for API endpoint tests.")
from fastapi.testclient import TestClient

from diabetes_mmkgqa_starter.api.app import create_app


def _write_csv(path: Path, rows: list[dict[str, str]], *, fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        if fieldnames is None:
            fieldnames = []
        with path.open("w", encoding="utf-8-sig", newline="") as f:
            if fieldnames:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
            return

    fieldnames = fieldnames or sorted({k for row in rows for k in row.keys()})
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _write_intents(path: Path) -> None:
    payload = {
        "intents": [
            {
                "name": "disease_symptoms",
                "description": "disease symptoms",
                "entity_types": ["Disease"],
                "relations": ["HAS_SYMPTOM"],
                "triggers": ["symptom", "symptoms", "what are the symptoms"],
            },
            {
                "name": "image_examples_by_disease",
                "description": "image examples",
                "entity_types": ["Disease"],
                "relations": ["IMAGE_ASSOCIATED_WITH"],
                "triggers": ["image", "images", "retina"],
            },
        ],
        "fallback": {
            "max_rows": 20,
            "max_hops": 2,
        },
    }
    path.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")


def _build_api_fixture(tmp_path: Path) -> tuple[Path, Path]:
    processed = tmp_path / "data" / "processed"
    _write_csv(
        processed / "nodes.csv",
        [
            {
                "node_id": "d1",
                "node_type": "Disease",
                "canonical_name": "diabetes",
                "knowledge_layer": "C",
                "source_ids": "manual",
                "kg_version": "0.2.0",
            },
            {
                "node_id": "s1",
                "node_type": "Symptom",
                "canonical_name": "thirst",
                "knowledge_layer": "A",
                "source_ids": "manual",
                "kg_version": "0.2.0",
            },
            {
                "node_id": "i1",
                "node_type": "Image",
                "canonical_name": "retina sample",
                "knowledge_layer": "C",
                "source_ids": "retina",
                "kg_version": "0.2.0",
            },
            {
                "node_id": "g1",
                "node_type": "ImageGrade",
                "canonical_name": "No_DR",
                "knowledge_layer": "C",
                "source_ids": "retina",
                "kg_version": "0.2.0",
            },
            {
                "node_id": "ds1",
                "node_type": "Dataset",
                "canonical_name": "RetinaMNIST+",
                "knowledge_layer": "C",
                "source_ids": "retina",
                "kg_version": "0.2.0",
            },
            {
                "node_id": "sp1",
                "node_type": "DataSplit",
                "canonical_name": "train",
                "knowledge_layer": "C",
                "source_ids": "retina",
                "kg_version": "0.2.0",
            },
        ],
        fieldnames=["node_id", "node_type", "canonical_name", "knowledge_layer", "source_ids", "kg_version"],
    )
    _write_csv(
        processed / "edges.csv",
        [
            {
                "head_id": "d1",
                "tail_id": "s1",
                "edge_id": "e1",
                "relation": "HAS_SYMPTOM",
                "source_id": "manual",
                "extraction_method": "manual",
                "confidence": "1.0",
                "knowledge_layer": "A",
                "kg_version": "0.2.0",
                "evidence_id": "ev1",
                "raw_relation": "HAS_SYMPTOM",
                "normalized_relation": "HAS_SYMPTOM",
            },
            {
                "head_id": "i1",
                "tail_id": "d1",
                "edge_id": "e2",
                "relation": "IMAGE_ASSOCIATED_WITH",
                "source_id": "retina",
                "extraction_method": "manual",
                "confidence": "1.0",
                "knowledge_layer": "C",
                "kg_version": "0.2.0",
                "evidence_id": "ev2",
                "raw_relation": "IMAGE_ASSOCIATED_WITH",
                "normalized_relation": "IMAGE_ASSOCIATED_WITH",
            },
            {
                "head_id": "i1",
                "tail_id": "g1",
                "edge_id": "e3",
                "relation": "HAS_IMAGE_GRADE",
                "source_id": "retina",
                "extraction_method": "manual",
                "confidence": "1.0",
                "knowledge_layer": "C",
                "kg_version": "0.2.0",
                "evidence_id": "ev2",
                "raw_relation": "HAS_IMAGE_GRADE",
                "normalized_relation": "HAS_IMAGE_GRADE",
            },
            {
                "head_id": "i1",
                "tail_id": "ds1",
                "edge_id": "e4",
                "relation": "FROM_DATASET",
                "source_id": "retina",
                "extraction_method": "manual",
                "confidence": "1.0",
                "knowledge_layer": "C",
                "kg_version": "0.2.0",
                "evidence_id": "ev2",
                "raw_relation": "FROM_DATASET",
                "normalized_relation": "FROM_DATASET",
            },
            {
                "head_id": "i1",
                "tail_id": "sp1",
                "edge_id": "e5",
                "relation": "IN_SPLIT",
                "source_id": "retina",
                "extraction_method": "manual",
                "confidence": "1.0",
                "knowledge_layer": "C",
                "kg_version": "0.2.0",
                "evidence_id": "ev2",
                "raw_relation": "IN_SPLIT",
                "normalized_relation": "IN_SPLIT",
            },
        ],
        fieldnames=[
            "head_id",
            "tail_id",
            "edge_id",
            "relation",
            "source_id",
            "extraction_method",
            "confidence",
            "knowledge_layer",
            "kg_version",
            "evidence_id",
            "raw_relation",
            "normalized_relation",
        ],
    )
    _write_csv(
        processed / "images.csv",
        [
            {
                "image_id": "i1",
                "relative_path": "data/interim/retina/retina_000001.bin",
                "dataset": "RetinaMNIST+",
                "split": "train",
                "grade": "No_DR",
                "kg_version": "0.2.0",
            }
        ],
        fieldnames=["image_id", "relative_path", "dataset", "split", "grade", "kg_version"],
    )

    _write_csv(processed / "documents.csv", [], fieldnames=[])
    _write_csv(processed / "evidence.csv", [], fieldnames=[])
    _write_csv(processed / "triples.tsv", [])

    intents_file = tmp_path / "intents.yaml"
    _write_intents(intents_file)
    return processed, intents_file


def test_api_health_ready_with_portable_backend(tmp_path: Path):
    processed, intents_path = _build_api_fixture(tmp_path)
    app = create_app(repo_root=tmp_path, processed_dir=processed, intents_path=intents_path)
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["backend_ready"] is True
    assert payload["status"] == "ready"
    assert payload["summary"]["node_count"] == 6


def test_api_health_blocked_without_backend(tmp_path: Path):
    app = create_app(repo_root=tmp_path, processed_dir="data/processed")
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["backend_ready"] is False
    assert payload["status"] == "blocked"
    assert "课程演示、非临床诊断" in payload["safety_notice"]


def test_api_qa_and_search_endpoints(tmp_path: Path):
    processed, intents_path = _build_api_fixture(tmp_path)
    app = create_app(repo_root=tmp_path, processed_dir=processed, intents_path=intents_path)
    client = TestClient(app)

    qa = client.post("/qa", json={"question": "what are symptoms of diabetes"})
    assert qa.status_code == 200
    qa_body = qa.json()
    assert qa_body["status"] == "ok"
    assert qa_body["evidence_ids"] == ["ev1"]
    assert "课程演示、非临床诊断" in qa_body["safety_notice"]

    search = client.get("/entities/search", params={"query": "diabetes", "node_types": "Disease", "limit": 10})
    assert search.status_code == 200
    search_body = search.json()
    assert search_body["count"] == 1
    assert search_body["items"][0]["canonical_name"] == "diabetes"
    assert "课程演示、非临床诊断" in search_body["safety_notice"]

    graph = client.get("/graph/subgraph", params={"center_node_id": "d1", "max_hops": 2})
    assert graph.status_code == 200
    graph_body = graph.json()
    assert graph_body["center_node_id"] == "d1"
    assert graph_body["node_count"] >= 2

    images = client.get("/images/search", params={"disease_id": "d1", "limit": 5})
    assert images.status_code == 200
    images_body = images.json()
    assert images_body["count"] == 1
    assert images_body["items"][0]["image_id"] == "i1"


def test_api_images_search_and_stats_require_backend(tmp_path: Path):
    processed, intents_path = _build_api_fixture(tmp_path)
    app = create_app(repo_root=tmp_path, processed_dir=processed, intents_path=intents_path)
    client = TestClient(app)

    stats = client.get("/stats")
    assert stats.status_code == 200
    stats_body = stats.json()
    assert stats_body["node_count"] == 6
    assert stats_body["edge_count"] == 5
    assert "课程演示、非临床诊断" in stats_body["safety_notice"]

    missing = client.get("/graph/subgraph", params={"center_node_id": "missing", "max_hops": 1})
    assert missing.status_code == 404
    missing_body = missing.json()
    assert "not found" in missing_body["detail"]
    assert "课程演示、非临床诊断" in missing_body["safety_notice"]
