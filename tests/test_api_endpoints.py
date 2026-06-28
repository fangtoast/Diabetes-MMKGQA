from __future__ import annotations

from pathlib import Path
import csv

import pytest
import yaml
import numpy as np
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
                "aliases": "",
                "knowledge_layer": "C",
                "source_ids": "manual",
                "kg_version": "0.2.0",
            },
            {
                "node_id": "d_retina",
                "node_type": "Disease",
                "canonical_name": "糖尿病视网膜病变",
                "aliases": "糖网;DR",
                "knowledge_layer": "C",
                "source_ids": "retinamnist",
                "kg_version": "0.2.0",
            },
            {
                "node_id": "s1",
                "node_type": "Symptom",
                "canonical_name": "thirst",
                "aliases": "",
                "knowledge_layer": "A",
                "source_ids": "manual",
                "kg_version": "0.2.0",
            },
            {
                "node_id": "i1",
                "node_type": "Image",
                "canonical_name": "retina sample",
                "aliases": "",
                "knowledge_layer": "C",
                "source_ids": "retina",
                "kg_version": "0.2.0",
            },
            {
                "node_id": "g1",
                "node_type": "ImageGrade",
                "canonical_name": "No_DR",
                "aliases": "",
                "knowledge_layer": "C",
                "source_ids": "retina",
                "kg_version": "0.2.0",
            },
            {
                "node_id": "ds1",
                "node_type": "Dataset",
                "canonical_name": "RetinaMNIST+",
                "aliases": "RetinaMNIST",
                "knowledge_layer": "C",
                "source_ids": "retina",
                "kg_version": "0.2.0",
            },
            {
                "node_id": "sp1",
                "node_type": "DataSplit",
                "canonical_name": "train",
                "aliases": "",
                "knowledge_layer": "C",
                "source_ids": "retina",
                "kg_version": "0.2.0",
            },
        ],
        fieldnames=["node_id", "node_type", "canonical_name", "aliases", "knowledge_layer", "source_ids", "kg_version"],
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
                "tail_id": "d_retina",
                "edge_id": "e2b",
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
                "source_id": "retinamnist",
                "source_file": "train_images",
                "image_index": "0",
                "dataset": "RetinaMNIST+",
                "split": "train",
                "grade": "No_DR",
                "grade_code": "0",
                "kg_version": "0.2.0",
            }
        ],
        fieldnames=[
            "image_id",
            "source_id",
            "source_file",
            "image_index",
            "dataset",
            "split",
            "grade",
            "grade_code",
            "kg_version",
        ],
    )

    _write_csv(processed / "documents.csv", [], fieldnames=[])
    _write_csv(processed / "evidence.csv", [], fieldnames=[])
    _write_csv(processed / "triples.tsv", [])

    raw_retina = tmp_path / "data" / "raw" / "retinamnist"
    raw_retina.mkdir(parents=True, exist_ok=True)
    np.savez(
        raw_retina / "retinamnist_224.npz",
        train_images=np.zeros((1, 4, 4, 3), dtype=np.uint8),
        train_labels=np.array([[0]], dtype=np.uint8),
    )

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
    assert payload["summary"]["node_count"] == 7


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

    legacy_search = client.get("/entities/search", params={"q": "diabetes", "node_types": "Disease", "limit": 10})
    assert legacy_search.status_code == 200
    legacy_search_body = legacy_search.json()
    assert legacy_search_body["count"] == 1
    assert legacy_search_body["items"][0]["canonical_name"] == "diabetes"
    assert "课程演示、非临床诊断" in legacy_search_body["safety_notice"]

    retina_search = client.get("/entities/search", params={"query": "糖网", "node_types": "Disease", "limit": 10})
    assert retina_search.status_code == 200
    retina_body = retina_search.json()
    assert retina_body["items"][0]["node_id"] == "d_retina"

    dataset_search = client.get("/entities/search", params={"query": "RetinaMNIST", "node_types": "Dataset", "limit": 10})
    assert dataset_search.status_code == 200
    assert dataset_search.json()["items"][0]["node_id"] == "ds1"

    grade_search = client.get("/entities/search", params={"query": "No_DR", "node_types": "ImageGrade", "limit": 10})
    assert grade_search.status_code == 200
    assert grade_search.json()["items"][0]["node_id"] == "g1"

    graph = client.get("/graph/subgraph", params={"center_node_id": "d1", "max_hops": 2})
    assert graph.status_code == 200
    graph_body = graph.json()
    assert graph_body["center_node_id"] == "d1"
    assert graph_body["node_count"] >= 2

    overview = client.get("/graph/overview", params={"limit": 4, "node_types": "Disease,Symptom"})
    assert overview.status_code == 200
    overview_body = overview.json()
    assert overview_body["mode"] == "overview"
    assert overview_body["node_count"] >= 2
    assert overview_body["edge_count"] >= 1

    legacy_graph = client.get("/graph/subgraph", params={"node": "d1", "max_hops": 2})
    assert legacy_graph.status_code == 200
    legacy_graph_body = legacy_graph.json()
    assert legacy_graph_body["center_node_id"] == "d1"
    assert legacy_graph_body["node_count"] >= 2

    images = client.get("/images/search", params={"disease_id": "d1", "limit": 5})
    assert images.status_code == 200
    images_body = images.json()
    assert images_body["count"] == 1
    assert images_body["items"][0]["image_id"] == "i1"
    assert images_body["items"][0]["preview_url"] == "/images/i1/preview.png"
    assert images_body["images"] == images_body["items"]

    default_images = client.get("/images/search", params={"disease_id": "", "limit": 5})
    assert default_images.status_code == 200
    default_images_body = default_images.json()
    assert default_images_body["count"] == 1
    assert default_images_body["images"][0]["image_id"] == "i1"

    source_images = client.get("/images/search", params={"source_id": "retinamnist", "limit": 5})
    assert source_images.status_code == 200
    source_images_body = source_images.json()
    assert source_images_body["count"] == 1
    assert source_images_body["images"][0]["source_id"] == "retinamnist"

    retina_images = client.get("/images/search", params={"disease_id": retina_body["items"][0]["node_id"], "limit": 5})
    assert retina_images.status_code == 200
    assert retina_images.json()["count"] == 1

    preview = client.get("/images/i1/preview.png")
    assert preview.status_code == 200
    assert preview.headers["content-type"] == "image/png"
    assert preview.content.startswith(b"\x89PNG")


def test_api_images_search_and_stats_require_backend(tmp_path: Path):
    processed, intents_path = _build_api_fixture(tmp_path)
    app = create_app(repo_root=tmp_path, processed_dir=processed, intents_path=intents_path)
    client = TestClient(app)

    stats = client.get("/stats")
    assert stats.status_code == 200
    stats_body = stats.json()
    assert stats_body["node_count"] == 7
    assert stats_body["edge_count"] == 6
    assert "课程演示、非临床诊断" in stats_body["safety_notice"]

    details = client.get("/stats/details", params={"kind": "images", "limit": 5})
    assert details.status_code == 200
    details_body = details.json()
    assert details_body["kind"] == "images"
    assert details_body["count"] == 1
    assert details_body["items"][0]["image_id"] == "i1"
    assert "relative_path" not in details_body["items"][0]
    assert "D:\\" not in str(details_body["items"])
    assert "课程演示、非临床诊断" in details_body["safety_notice"]

    evidence_details = client.get("/stats/details", params={"kind": "evidence_claims", "limit": 5})
    assert evidence_details.status_code == 200
    evidence_body = evidence_details.json()
    assert evidence_body["count"] == 6
    assert evidence_body["items"][0]["evidence_id"]
    assert "head_name" in evidence_body["items"][0]

    invalid_details = client.get("/stats/details", params={"kind": "raw_paths"})
    assert invalid_details.status_code == 422
    assert "课程演示、非临床诊断" in invalid_details.json()["safety_notice"]

    missing = client.get("/graph/subgraph", params={"center_node_id": "missing", "max_hops": 1})
    assert missing.status_code == 404
    missing_body = missing.json()
    assert "not found" in missing_body["detail"]
    assert "课程演示、非临床诊断" in missing_body["safety_notice"]


def test_api_frontend_routes_when_frontend_exists(tmp_path: Path):
    processed, intents_path = _build_api_fixture(tmp_path)
    frontend = tmp_path / "frontend"
    frontend.mkdir()
    (frontend / "index.html").write_text("<!doctype html><html><body>kgqa ui</body></html>", encoding="utf-8")
    (frontend / "styles.css").write_text("body { }", encoding="utf-8")
    (frontend / "app.js").write_text("console.log('ui boot');", encoding="utf-8")

    app = create_app(repo_root=tmp_path, processed_dir=processed, intents_path=intents_path)
    client = TestClient(app)

    root = client.get("/", allow_redirects=False)
    ui = client.get("/ui")
    static = client.get("/static/app.js")

    assert root.status_code == 307
    assert root.headers["location"] == "/ui"
    assert ui.status_code == 200
    assert "kgqa ui" in ui.text
    assert static.status_code == 200
