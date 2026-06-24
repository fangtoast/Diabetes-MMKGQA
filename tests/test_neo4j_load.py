from __future__ import annotations

from pathlib import Path

import yaml

from diabetes_mmkgqa_starter.db import neo4j_loader


def _write_yaml(path: Path, payload: dict) -> None:
    path.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")


def _sample_ontology(path: Path) -> None:
    _write_yaml(
        path,
        {
            "version": "0.2.0",
            "relations": {
                "HAS_SYMPTOM": {},
                "MENTIONED_IN": {},
            },
        },
    )


class _MergeMemoryDriver:
    def __init__(self) -> None:
        self.nodes = set()
        self.edges = set()
        self.statements = []

    def __call__(self, query: str, params: dict) -> None:
        self.statements.append((query, params))
        if query.startswith("MERGE (n:"):
            self.nodes.add(params.get("node_id", ""))
        if "MERGE (h)-[e:" in query:
            self.edges.add(params.get("edge_id", ""))


def test_build_import_plan_is_idempotent_shape(tmp_path: Path):
    ontology_file = tmp_path / "ontology.yaml"
    _sample_ontology(ontology_file)

    nodes = [
        {
            "node_id": "n_symptom_headache",
            "node_type": "Symptom",
            "canonical_name": "headache",
            "knowledge_layer": "A",
            "source_ids": "manual",
            "kg_version": "0.2.0",
        },
        {
            "node_id": "n_disease_hyper",
            "node_type": "Disease",
            "canonical_name": "hypertension",
            "knowledge_layer": "C",
            "source_ids": "manual",
            "kg_version": "0.2.0",
        },
    ]
    edges = [
        {
            "head_id": "n_disease_hyper",
            "tail_id": "n_symptom_headache",
            "edge_id": "e_hyper_has_symptom",
            "relation": "HAS_SYMPTOM",
            "source_id": "manual",
            "extraction_method": "manual",
            "confidence": "1.0",
            "knowledge_layer": "C",
            "kg_version": "0.2.0",
        }
    ]

    setup_queries, node_queries, edge_queries = neo4j_loader.build_import_plan(
        nodes,
        edges,
        ontology_path=ontology_file,
    )

    assert any("CREATE CONSTRAINT" in q for q, _ in setup_queries)
    assert all("MERGE" in q for q, _ in node_queries)
    assert all("MERGE" in q for q, _ in edge_queries)
    assert all("CREATE" not in q for q, _ in node_queries)
    assert all("CREATE" not in q for q, _ in edge_queries)

    memory = _MergeMemoryDriver()
    neo4j_loader.execute_plan(setup_queries + node_queries + edge_queries, memory)
    neo4j_loader.execute_plan(setup_queries + node_queries + edge_queries, memory)

    assert len(memory.nodes) == 2
    assert len(memory.edges) == 1
    assert len([s for s in memory.statements if s[0].startswith("CREATE CONSTRAINT")]) >= 1


def test_execute_load_dry_run_counts_files(tmp_path: Path):
    ontology_file = tmp_path / "ontology.yaml"
    _sample_ontology(ontology_file)

    sample_dir = tmp_path / "processed"
    sample_dir.mkdir()
    (sample_dir / "nodes.csv").write_text(
        "node_id,node_type,canonical_name,knowledge_layer,source_ids,kg_version\n"
        "n_symptom_headache,Symptom,headache,A,manual,0.2.0\n"
        "n_disease_hyper,Disease,hypertension,C,manual,0.2.0\n",
        encoding="utf-8",
    )
    (sample_dir / "edges.csv").write_text(
        "head_id,tail_id,edge_id,relation,source_id,extraction_method,confidence,knowledge_layer,kg_version\n"
        "n_disease_hyper,n_symptom_headache,e1,HAS_SYMPTOM,manual,manual,1.0,C,0.2.0\n",
        encoding="utf-8",
    )

    summary = neo4j_loader.execute_load(
        processed_dir=sample_dir,
        uri="bolt://localhost:7687",
        user="neo4j",
        password="pass",
        ontology_path=ontology_file,
        dry_run=True,
    )

    assert summary.node_count == 2
    assert summary.edge_count == 1
    assert summary.statement_count == 4


def test_execute_load_requires_credentials(tmp_path: Path):
    ontology_file = tmp_path / "ontology.yaml"
    _sample_ontology(ontology_file)

    sample_dir = tmp_path / "processed"
    sample_dir.mkdir()
    (sample_dir / "nodes.csv").write_text(
        "node_id,node_type,canonical_name,knowledge_layer,source_ids,kg_version\n",
        encoding="utf-8",
    )
    (sample_dir / "edges.csv").write_text(
        "head_id,tail_id,edge_id,relation,source_id,extraction_method,confidence,knowledge_layer,kg_version\n",
        encoding="utf-8",
    )

    try:
        neo4j_loader.execute_load(processed_dir=sample_dir, ontology_path=ontology_file)
    except RuntimeError as err:
        assert "URI is required" in str(err)
    else:
        raise AssertionError("expected RuntimeError for missing URI")
