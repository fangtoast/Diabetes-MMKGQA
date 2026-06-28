"""Tests for portable file-backed KG backend."""

from __future__ import annotations

from pathlib import Path

from diabetes_mmkgqa_starter.db.portable_backend import PortableGraphBackend


def _write_csv(path: Path, rows: list[dict[str, str]], *, fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        if fieldnames is None:
            fieldnames = []
        with path.open("w", encoding="utf-8", newline="") as f:
            if fieldnames:
                f.write(",".join(fieldnames) + "\n")
            return

    fieldnames = fieldnames or sorted({k for row in rows for k in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as f:
        f.write(",".join(fieldnames) + "\n")
        for row in rows:
            values = [str(row.get(col, "")) for col in fieldnames]
            f.write(",".join([v.replace(",", "\\,") for v in values]) + "\n")


def _build_portable_fixture(processed_dir: Path) -> None:
    _write_csv(
        processed_dir / "nodes.csv",
        [
            {
                "node_id": "n1",
                "node_type": "Disease",
                "canonical_name": "diabetes",
                "knowledge_layer": "C",
                "source_ids": "manual",
                "kg_version": "0.2.0",
            },
            {
                "node_id": "n2",
                "node_type": "Image",
                "canonical_name": "retina_01",
                "knowledge_layer": "C",
                "source_ids": "manual",
                "kg_version": "0.2.0",
            },
            {
                "node_id": "n3",
                "node_type": "ImageGrade",
                "canonical_name": "grade_3",
                "knowledge_layer": "C",
                "source_ids": "manual",
                "kg_version": "0.2.0",
            },
            {
                "node_id": "n4",
                "node_type": "Dataset",
                "canonical_name": "retina_dataset",
                "knowledge_layer": "C",
                "source_ids": "manual",
                "kg_version": "0.2.0",
            },
            {
                "node_id": "n5",
                "node_type": "DataSplit",
                "canonical_name": "train",
                "knowledge_layer": "C",
                "source_ids": "manual",
                "kg_version": "0.2.0",
            },
        ],
        fieldnames=["node_id", "node_type", "canonical_name", "knowledge_layer", "source_ids", "kg_version"],
    )

    _write_csv(
        processed_dir / "edges.csv",
        [
            {
                "head_id": "n2",
                "tail_id": "n1",
                "edge_id": "e1",
                "relation": "IMAGE_ASSOCIATED_WITH",
                "source_id": "manual",
                "extraction_method": "manual",
                "confidence": "1.0",
                "knowledge_layer": "C",
                "kg_version": "0.2.0",
                "evidence_id": "ev1",
            },
            {
                "head_id": "n2",
                "tail_id": "n3",
                "edge_id": "e2",
                "relation": "HAS_IMAGE_GRADE",
                "source_id": "manual",
                "extraction_method": "manual",
                "confidence": "1.0",
                "knowledge_layer": "C",
                "kg_version": "0.2.0",
            },
            {
                "head_id": "n2",
                "tail_id": "n4",
                "edge_id": "e3",
                "relation": "FROM_DATASET",
                "source_id": "manual",
                "extraction_method": "manual",
                "confidence": "1.0",
                "knowledge_layer": "C",
                "kg_version": "0.2.0",
            },
            {
                "head_id": "n2",
                "tail_id": "n5",
                "edge_id": "e4",
                "relation": "IN_SPLIT",
                "source_id": "manual",
                "extraction_method": "manual",
                "confidence": "1.0",
                "knowledge_layer": "C",
                "kg_version": "0.2.0",
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
        ],
    )

    _write_csv(
        processed_dir / "images.csv",
        [
            {
                "image_id": "n2",
                "relative_path": "data/interim/retinamnist/retina_sample.bin",
                "dataset": "retina_dataset",
                "split": "train",
                "grade": "grade_3",
                "source_id": "retinamnist",
                "kg_version": "0.2.0",
            }
        ],
        fieldnames=["image_id", "relative_path", "dataset", "split", "grade", "source_id", "kg_version"],
    )


def test_portable_backend_load_and_health(tmp_path: Path):
    processed = tmp_path / "data" / "processed"
    _build_portable_fixture(processed)

    backend = PortableGraphBackend.from_dir(processed)
    health = backend.health()

    assert health["ok"] is True
    assert health["backend"] == "portable"
    assert health["node_count"] == 5
    assert health["edge_count"] == 4
    assert health["image_count"] == 1
    assert backend.summary.node_count == 5
    assert backend.summary.edge_count == 4
    assert backend.summary.image_count == 1


def test_portable_backend_search_and_subgraph(tmp_path: Path):
    processed = tmp_path / "data" / "processed"
    _build_portable_fixture(processed)
    backend = PortableGraphBackend.from_dir(processed)

    disease = backend.search_entities("diabetes", node_types=["Disease"])
    assert len(disease) == 1
    assert disease[0]["node_id"] == "n1"

    subgraph = backend.query_subgraph("n1", max_hops=2)
    assert subgraph["center_node_id"] == "n1"
    assert subgraph["node_count"] >= 2
    assert subgraph["edge_count"] >= 1
    assert any(row["relation"] == "IMAGE_ASSOCIATED_WITH" for row in subgraph["edges"])


def test_portable_backend_image_search_filters(tmp_path: Path):
    processed = tmp_path / "data" / "processed"
    _build_portable_fixture(processed)
    backend = PortableGraphBackend.from_dir(processed)

    images_by_disease = backend.search_images(disease_id="n1")
    images_by_grade = backend.search_images(grade_id="n3")
    images_by_dataset = backend.search_images(dataset_id="n4")
    images_by_split = backend.search_images(split_id="n5")
    images_by_source = backend.search_images(source_id="retinamnist")
    images_by_dataset_name = backend.search_images(dataset="retina_dataset")
    images_intersection = backend.search_images(disease_id="n1", grade_id="n3", dataset_id="n4", split_id="n5")

    assert len(images_by_disease) == 1
    assert images_by_disease[0]["image_id"] == "n2"
    assert len(images_by_grade) == 1
    assert len(images_by_dataset) == 1
    assert len(images_by_split) == 1
    assert len(images_by_source) == 1
    assert len(images_by_dataset_name) == 1
    assert len(images_intersection) == 1
    assert images_intersection[0]["image_id"] == "n2"


def test_portable_backend_stats_from_graph(tmp_path: Path):
    processed = tmp_path / "data" / "processed"
    _build_portable_fixture(processed)
    backend = PortableGraphBackend.from_dir(processed)

    stats = backend.get_stats()
    assert stats["node_count"] == 5
    assert stats["edge_count"] == 4
    assert stats["image_node_count"] == 1
    assert stats["image_metadata_count"] == 1


def test_portable_backend_stats_details_are_safe_samples(tmp_path: Path):
    processed = tmp_path / "data" / "processed"
    _build_portable_fixture(processed)
    backend = PortableGraphBackend.from_dir(processed)

    nodes = backend.get_stats_details("nodes", limit=2)
    edges = backend.get_stats_details("evidence_claims", limit=5)
    images = backend.get_stats_details("images", limit=5)
    layer_c = backend.get_stats_details("layer_C", limit=10)

    assert nodes["kind"] == "nodes"
    assert nodes["count"] == 5
    assert set(nodes["items"][0]) >= {"node_id", "canonical_name", "source_ids", "kg_version"}
    assert "relative_path" not in nodes["items"][0]
    assert edges["count"] == 1
    assert edges["items"][0]["evidence_id"] == "ev1"
    assert "head_name" in edges["items"][0]
    assert images["items"][0]["image_id"] == "n2"
    assert "relative_path" not in images["items"][0]
    assert layer_c["count"] == 5
