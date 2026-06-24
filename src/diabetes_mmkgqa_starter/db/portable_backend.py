"""Portable graph backend loaded from processed KG export files."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from pathlib import Path
import csv
import json
from typing import Iterable


@dataclass(frozen=True)
class PortableBackendSummary:
    """Summary data for portable backend readiness."""

    node_count: int
    edge_count: int
    image_count: int
    stat_source: str


class PortableGraphBackend:
    """Load and query portable graph exports without Neo4j.

    The backend is intentionally conservative and deterministic so it can be used
    as a fallback in environments without Docker/Neo4j.
    """

    def __init__(self, processed_dir: Path, *, ontology_path: Path | None = None) -> None:
        self.processed_dir = Path(processed_dir).resolve()
        self.ontology_path = ontology_path
        self._require_artifacts()
        self.nodes = {row["node_id"]: row for row in self._read_rows("nodes.csv") if row.get("node_id")}
        self.edges = list(self._read_rows("edges.csv"))
        self.images = {row["image_id"]: row for row in self._read_rows("images.csv") if row.get("image_id")}
        self.documents = {row["document_id"]: row for row in self._read_rows("documents.csv") if row.get("document_id")}
        self.evidence = {row["evidence_id"]: row for row in self._read_rows("evidence.csv") if row.get("evidence_id")}
        self.triples = list(self._read_rows("triples.tsv"))
        self._stats = self._read_stats(self.processed_dir / "stats.json")
        self._index_outgoing, self._index_incoming = self._build_indices(self.edges)

    @classmethod
    def from_dir(cls, processed_dir: Path, *, ontology_path: Path | None = None) -> "PortableGraphBackend":
        """Factory helper to avoid naming ambiguity."""

        return cls(processed_dir, ontology_path=ontology_path)

    @property
    def summary(self) -> PortableBackendSummary:
        return PortableBackendSummary(
            node_count=len(self.nodes),
            edge_count=len(self.edges),
            image_count=len(self.images),
            stat_source="stats.json" if (self.processed_dir / "stats.json").exists() else "computed",
        )

    def health(self) -> dict[str, object]:
        """Return a simple health payload for runner and API readiness checks."""

        return {
            "ok": True,
            "backend": "portable",
            "processed_dir": str(self.processed_dir),
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "image_count": len(self.images),
        }

    def get_node(self, node_id: str) -> dict | None:
        """Return a single node payload by id."""

        return self.nodes.get(node_id)

    def search_entities(self, query: str, *, node_types: list[str] | None = None, limit: int = 20) -> list[dict]:
        """Find entities by canonical id/name fragments.

        The search is case-insensitive and deterministic.
        """

        if limit <= 0:
            return []
        q = (query or "").strip().lower()
        if not q:
            return []

        requested = set(node_types or [])
        matches: list[tuple[int, str, dict]] = []
        for node_id, row in self.nodes.items():
            node_type = row.get("node_type", "")
            if requested and node_type and node_type not in requested:
                continue

            canonical = str(row.get("canonical_name", "")).lower()
            alias_text = str(row.get("synonyms", "")).lower()
            score = self._match_score(q, canonical, row.get("node_id", ""))
            if score is None:
                score = self._match_score(q, alias_text)
            if score is None:
                continue
            matches.append((score, node_id, row))

        matches.sort(key=lambda item: (item[0], item[1]))
        return [row for _, _, row in matches[: max(limit, 0)]]

    def query_subgraph(self, center_node_id: str, *, max_hops: int = 2) -> dict:
        """Explore an undirected neighborhood around one node."""

        if center_node_id not in self.nodes:
            raise KeyError(f"Node not found: {center_node_id}")
        if max_hops < 0:
            raise ValueError("max_hops must be non-negative.")

        visited_nodes = {center_node_id}
        visited_edges: set[str] = set()
        selected_edges: list[dict] = []
        queue: deque[tuple[str, int]] = deque([(center_node_id, 0)])

        while queue:
            node_id, depth = queue.popleft()
            if depth >= max_hops:
                continue

            for direction_edges in (
                self._index_outgoing.get(node_id, []),
                self._index_incoming.get(node_id, []),
            ):
                for edge in direction_edges:
                    edge_id = edge.get("edge_id", "")
                    if edge_id in visited_edges:
                        continue
                    visited_edges.add(edge_id)
                    selected_edges.append(edge)

                    for neighbor_id in (edge.get("head_id", ""), edge.get("tail_id", "")):
                        if not neighbor_id or neighbor_id == node_id:
                            continue
                        if neighbor_id not in visited_nodes and neighbor_id in self.nodes:
                            visited_nodes.add(neighbor_id)
                            queue.append((neighbor_id, depth + 1))

        payload_nodes = [self.nodes[node_id] for node_id in sorted(visited_nodes)]
        payload_nodes.sort(key=lambda row: str(row.get("node_id", "")))
        selected_edges.sort(key=lambda row: (row.get("head_id", ""), row.get("relation", ""), row.get("tail_id", "")))
        return {
            "center_node_id": center_node_id,
            "nodes": payload_nodes,
            "edges": selected_edges,
            "edge_count": len(selected_edges),
            "node_count": len(payload_nodes),
        }

    def search_images(
        self,
        *,
        disease_id: str | None = None,
        grade_id: str | None = None,
        dataset_id: str | None = None,
        split_id: str | None = None,
        limit: int = 20,
    ) -> list[dict]:
        """Filter image metadata by known relations in processed files."""

        if limit <= 0:
            return []

        image_ids = set(self.images)
        if disease_id is not None:
            image_ids &= set(self._linked_neighbors(disease_id, "IMAGE_ASSOCIATED_WITH"))
        if grade_id is not None:
            image_ids &= set(self._linked_neighbors(grade_id, "HAS_IMAGE_GRADE"))
        if dataset_id is not None:
            image_ids &= set(self._linked_neighbors(dataset_id, "FROM_DATASET"))
        if split_id is not None:
            image_ids &= set(self._linked_neighbors(split_id, "IN_SPLIT"))
        if not image_ids:
            return []

        ordered = [self.images[i] for i in sorted(image_ids) if i in self.images]
        return ordered[:limit]

    def get_stats(self) -> dict[str, object]:
        """Return stats payload from file when available, else compute from exports."""

        if self._stats:
            return dict(self._stats)
        return {
            "kg_version": "0.2.0",
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "image_node_count": sum(1 for row in self.nodes.values() if row.get("node_type") == "Image"),
            "image_metadata_count": len(self.images),
            "canonical_entity_count": len({(row.get("node_type"), row.get("canonical_name")) for row in self.nodes.values()}),
            "unique_semantic_triples_count": len({(row.get("head_id"), row.get("relation"), row.get("tail_id")) for row in self.edges}),
            "quality_gate": {"passed": True},
        }

    def _linked_neighbors(self, endpoint_id: str, relation: str) -> list[str]:
        """Return image ids linked to a relation endpoint."""

        image_ids: set[str] = set()
        for edge in self.edges:
            if edge.get("relation") != relation:
                continue
            head_id = edge.get("head_id", "")
            tail_id = edge.get("tail_id", "")
            if head_id == endpoint_id and tail_id in self.images:
                image_ids.add(tail_id)
            if tail_id == endpoint_id and head_id in self.images:
                image_ids.add(head_id)
        return sorted(image_ids)

    def _read_rows(self, filename: str) -> list[dict]:
        path = self.processed_dir / filename
        if not path.exists():
            return []
        if path.suffix.lower() in {".csv", ".tsv"}:
            return self._read_csv(path)
        if path.suffix.lower() == ".json":
            return self._read_json_array(path)
        return []

    def _read_csv(self, path: Path) -> list[dict]:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            return [dict(row) for row in csv.DictReader(f)]

    def _read_json_array(self, path: Path) -> list[dict]:
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        if isinstance(payload, list):
            return [dict(item) for item in payload]
        if isinstance(payload, dict):
            first = payload.get("items")
            if isinstance(first, list):
                return [dict(item) for item in first]
        return []

    def _read_stats(self, path: Path) -> dict | None:
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        return payload if isinstance(payload, dict) else None

    def _require_artifacts(self) -> None:
        nodes_path = self.processed_dir / "nodes.csv"
        edges_path = self.processed_dir / "edges.csv"
        missing = []
        if not nodes_path.exists():
            missing.append("nodes.csv")
        if not edges_path.exists():
            missing.append("edges.csv")
        if missing:
            raise FileNotFoundError(
                f"Missing required graph artifacts in {self.processed_dir}: {', '.join(missing)}"
            )

    def _build_indices(self, edges: Iterable[dict]) -> tuple[dict[str, list[dict]], dict[str, list[dict]]]:
        outgoing: dict[str, list[dict]] = {}
        incoming: dict[str, list[dict]] = {}
        for edge in edges:
            head_id = edge.get("head_id", "")
            tail_id = edge.get("tail_id", "")
            if not head_id or not tail_id:
                continue
            outgoing.setdefault(head_id, []).append(edge)
            incoming.setdefault(tail_id, []).append(edge)
        for values in outgoing.values():
            values.sort(key=lambda row: (row.get("relation", ""), row.get("edge_id", "")))
        for values in incoming.values():
            values.sort(key=lambda row: (row.get("relation", ""), row.get("edge_id", "")))
        return outgoing, incoming

    @staticmethod
    def _match_score(query: str, candidate: str, node_id: str | None = None) -> int | None:
        if not candidate:
            return None
        hay = str(candidate).strip().lower()
        if hay == query:
            return 0
        if hay.startswith(query):
            return 1
        if query in hay:
            return 2
        if node_id and node_id.startswith(query):
            return 3
        return None
