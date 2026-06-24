"""Neo4j idempotent import utilities.

The module builds parameterized Cypher MERGE statements and executes them against a
Neo4j instance when available.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Sequence

from diabetes_mmkgqa_starter.graph_builder import _read_yaml


CypherExecutor = Callable[[str, dict], None]

NODE_CSV = "nodes.csv"
EDGE_CSV = "edges.csv"

_ID_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True)
class Neo4jLoadSummary:
    """Summary of a dry-run/import execution."""

    node_count: int
    edge_count: int
    statement_count: int


def _safe_identifier(value: str, *, fallback: str) -> str:
    """Return a safe Neo4j identifier, or fallback when unsafe."""

    if not value:
        return fallback
    token = str(value).strip()
    if _ID_PATTERN.fullmatch(token):
        return token
    return fallback


def _read_csv_rows(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _normalize_property_map(row: dict) -> dict:
    normalized = {}
    for key, value in row.items():
        if value is None or value == "":
            continue
        normalized[key] = value
    return normalized


def build_import_plan(
    nodes: list[dict],
    edges: list[dict],
    *,
    ontology_path: Path | None = None,
    unknown_relation_fallback: str = "UNKNOWN_REL",
) -> tuple[list[tuple[str, dict]], list[tuple[str, dict]], list[tuple[str, dict]]]:
    """Build setup, node, and edge MERGE statements for idempotent import."""

    setup_queries: list[tuple[str, dict]] = [
        (
            "CREATE CONSTRAINT node_id_unique IF NOT EXISTS\n"
            "FOR (n:KGNode)\n"
            "REQUIRE n.node_id IS UNIQUE",
            {},
        )
    ]

    allowed_relations = None
    if ontology_path is not None:
        ontology = _read_yaml(ontology_path)
        allowed_relations = {str(name) for name in ontology.get("relations", {})}

    node_queries: list[tuple[str, dict]] = []
    for row in nodes:
        node_id = row.get("node_id", "")
        if not node_id:
            continue
        label = _safe_identifier(str(row.get("node_type", "")), fallback="KGNode")
        query = (
            "MERGE (n:KGNode:{node_type} {{node_id: $node_id}})\n"
            "SET n += $props"
        ).format(node_type=label)
        node_queries.append((query, {"node_id": node_id, "props": _normalize_property_map(row)}))

    edge_queries: list[tuple[str, dict]] = []
    for row in edges:
        relation = str(row.get("relation", ""))
        if allowed_relations is not None and relation not in allowed_relations:
            continue
        safe_relation = _safe_identifier(relation, fallback=unknown_relation_fallback)
        if safe_relation == unknown_relation_fallback:
            continue

        head_id = row.get("head_id", "")
        tail_id = row.get("tail_id", "")
        edge_id = row.get("edge_id", "")
        if not (head_id and tail_id and edge_id):
            continue

        query = (
            "MATCH (h:KGNode {{node_id: $head_id}})\n"
            "MATCH (t:KGNode {{node_id: $tail_id}})\n"
            "MERGE (h)-[e:{relation} {{edge_id: $edge_id}}]->(t)\n"
            "SET e += $props"
        ).format(relation=safe_relation)
        edge_queries.append(
            (
                query,
                {
                    "head_id": head_id,
                    "tail_id": tail_id,
                    "edge_id": edge_id,
                    "props": _normalize_property_map(row),
                },
            )
        )

    return setup_queries, node_queries, edge_queries


def build_plan_from_files(
    processed_dir: Path,
    *,
    ontology_path: Path | None = None,
    unknown_relation_fallback: str = "UNKNOWN_REL",
) -> tuple[list[tuple[str, dict]], list[tuple[str, dict]], list[tuple[str, dict]]]:
    """Load graph CSV files and build Cypher plan."""

    nodes_path = processed_dir / NODE_CSV
    edges_path = processed_dir / EDGE_CSV
    if not nodes_path.exists() or not edges_path.exists():
        raise FileNotFoundError(
            f"Missing required graph artifacts in {processed_dir}: {nodes_path.name}, {edges_path.name}"
        )

    nodes = _read_csv_rows(nodes_path)
    edges = _read_csv_rows(edges_path)
    return build_import_plan(
        nodes,
        edges,
        ontology_path=ontology_path,
        unknown_relation_fallback=unknown_relation_fallback,
    )


def execute_plan(plan: Iterable[tuple[str, dict]], executor: CypherExecutor) -> None:
    """Execute query plan using caller-provided executor."""

    for query, params in plan:
        executor(query, params)


def execute_load(
    *,
    processed_dir: Path,
    uri: str | None = None,
    user: str = "neo4j",
    password: str | None = None,
    database: str = "neo4j",
    ontology_path: Path | None = None,
    dry_run: bool = False,
    unknown_relation_fallback: str = "UNKNOWN_REL",
) -> Neo4jLoadSummary:
    """Load graph artifacts into Neo4j with idempotent MERGE."""

    setup_queries, node_queries, edge_queries = build_plan_from_files(
        processed_dir,
        ontology_path=ontology_path,
        unknown_relation_fallback=unknown_relation_fallback,
    )
    statements = setup_queries + node_queries + edge_queries

    if dry_run:
        return Neo4jLoadSummary(
            node_count=len(node_queries),
            edge_count=len(edge_queries),
            statement_count=len(statements),
        )

    if uri is None:
        raise RuntimeError("Neo4j URI is required for load execution.")
    if password is None:
        raise RuntimeError("Neo4j password is required for load execution.")

    try:
        from neo4j import GraphDatabase
    except Exception as exc:
        raise RuntimeError("neo4j python driver is not installed. Add to requirements and retry.") from exc

    driver = GraphDatabase.driver(uri=uri, auth=(user, password))
    with driver.session(database=database) as session:
        execute_plan(setup_queries + node_queries, lambda query, params: session.run(query, **params))
        execute_plan(edge_queries, lambda query, params: session.run(query, **params))

    return Neo4jLoadSummary(
        node_count=len(node_queries),
        edge_count=len(edge_queries),
        statement_count=len(statements),
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import portable KG artifacts into Neo4j.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-dir", default=str(Path("data") / "processed"))
    parser.add_argument("--uri", default=os.getenv("NEO4J_URI", "bolt://localhost:7687"))
    parser.add_argument("--user", default=os.getenv("NEO4J_USER", "neo4j"))
    parser.add_argument("--password", default=os.getenv("NEO4J_PASSWORD"))
    parser.add_argument("--database", default=os.getenv("NEO4J_DATABASE", "neo4j"))
    parser.add_argument("--ontology-path", default="configs/ontology.yaml")
    parser.add_argument("--fallback-relation", default="UNKNOWN_REL")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    processed_dir = repo_root / args.output_dir
    ontology_path = repo_root / args.ontology_path

    summary = execute_load(
        processed_dir=processed_dir,
        uri=args.uri,
        user=args.user,
        password=args.password,
        database=args.database,
        ontology_path=ontology_path,
        dry_run=args.dry_run,
        unknown_relation_fallback=args.fallback_relation,
    )
    print(
        f"[neo4j-loader] summary: nodes={summary.node_count}, "
        f"edges={summary.edge_count}, statements={summary.statement_count}, dry_run={args.dry_run}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
