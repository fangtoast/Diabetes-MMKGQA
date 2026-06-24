"""Safe, parameterized query template definitions for QA workflows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import re

from diabetes_mmkgqa_starter.qa.intent_router import IntentMatch


_SAFE_NODE_ID = re.compile(r"^[A-Za-z0-9._-]+$")


class QAQueryTemplateError(ValueError):
    """Raised when intent/query parameters cannot produce a safe template."""


@dataclass(frozen=True)
class QueryTemplate:
    """A read-only template payload intended for controlled graph backends."""

    query: str
    parameters: dict[str, Any]
    read_only: bool = True
    name: str | None = None
    allowed_relations: tuple[str, ...] = ()
    max_hops: int = 0

    def to_payload(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "parameters": dict(self.parameters),
            "read_only": self.read_only,
        }


def build_subgraph_query(
    *,
    intent_match: IntentMatch,
    node_id: str,
    max_hops: int = 2,
    include_node_neighbors: bool = True,
) -> QueryTemplate:
    """Return a deterministic read-only query plan with parameterized values.

    Args:
        intent_match: matched intent carrying allowed relations.
        node_id: resolved graph node identifier (must be deterministic, not user text).
        max_hops: hop limit for downstream expansion.
        include_node_neighbors: compatibility flag for future backend extensions.
    """

    if not node_id or not _SAFE_NODE_ID.fullmatch(str(node_id)):
        raise QAQueryTemplateError("Invalid node_id for query template")
    if not isinstance(max_hops, int) or max_hops < 0:
        raise QAQueryTemplateError("max_hops must be a non-negative integer")
    if not include_node_neighbors:
        raise QAQueryTemplateError("include_node_neighbors must be True in this implementation")

    relations = [r for r in dict.fromkeys([str(r).strip() for r in intent_match.intent.relations or []]) if r]
    if not relations:
        raise QAQueryTemplateError(
            f"intent {intent_match.intent.name} has no configured relations; template is unsafe without relation allowlist"
        )

    query = (
        "MATCH (center)-[r*0..$max_hops]-(neighbor)\n"
        "WHERE center.node_id = $node_id\n"
        "AND (size($relations) = 0 OR r.relation IN $relations)\n"
        "WITH center, neighbor, r\n"
        "RETURN center, neighbor, r\n"
    )

    parameters = {
        "node_id": node_id,
        "relations": relations,
        "max_hops": max_hops,
    }
    return QueryTemplate(
        query=query,
        parameters=parameters,
        read_only=True,
        name="subgraph_by_node",
        allowed_relations=tuple(relations),
        max_hops=max_hops,
    )


def validate_query_payload(payload: QueryTemplate) -> None:
    """Validate that a template payload is query-only and parameterized."""

    if not payload.read_only:
        raise QAQueryTemplateError("query payload must be read-only")
    if "$node_id" not in payload.query:
        raise QAQueryTemplateError("query must be parameterized by $node_id")
    if "$relations" not in payload.query:
        raise QAQueryTemplateError("query must be parameterized by $relations")
    if "$max_hops" not in payload.query and "max_hops" in payload.parameters:
        raise QAQueryTemplateError("query must be parameterized by $max_hops")
    if "{" in payload.query or "}" in payload.query:
        raise QAQueryTemplateError("query template must not use Python/Rust/str.format-style interpolation")
