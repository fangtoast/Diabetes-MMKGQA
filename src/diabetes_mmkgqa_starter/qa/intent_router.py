"""Intent routing and parser contract helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml


DEFAULT_INTENT_PATH = Path("configs") / "intents.yaml"


def _normalize_text(value: str) -> str:
    return " ".join((value or "").strip().lower().split())


def _to_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return [str(item) for item in value]


@dataclass(frozen=True)
class IntentDefinition:
    """Strongly-typed intent definition from YAML."""

    name: str
    description: str
    entity_types: list[str]
    relations: list[str]
    triggers: list[str]


@dataclass(frozen=True)
class IntentMatch:
    """One matched intent candidate."""

    intent: IntentDefinition
    matched_trigger: str
    confidence: int
    intent_rank: int
    trigger_rank: int


class IntentMatchError(ValueError):
    """Raised when the intent contract has malformed data."""


def load_intent_contract(path: Path | str | None = None) -> tuple[list[IntentDefinition], dict]:
    """Load intents and fallback settings from a project yaml."""

    path = Path(path or DEFAULT_INTENT_PATH)
    with path.open("r", encoding="utf-8-sig") as file:
        payload = yaml.safe_load(file) or {}

    if not isinstance(payload, dict):
        raise IntentMatchError(f"Intent contract payload must be a mapping in {path}")

    items = payload.get("intents", [])
    if not isinstance(items, list) or not items:
        raise IntentMatchError(f"Intent contract in {path} does not define a non-empty intents list")

    parsed: list[IntentDefinition] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if not name:
            raise IntentMatchError(f"intent #{index} missing name")

        description = str(item.get("description", "")).strip()
        entity_types = _to_list(item.get("entity_types", []))
        relation_values = item.get("relations", item.get("relation", []))
        relations = _to_list(relation_values)
        triggers = _to_list(item.get("triggers", []))

        if not entity_types or not relations or not triggers:
            raise IntentMatchError(f"intent {name} must define entity_types, relations, and triggers")

        parsed.append(
            IntentDefinition(
                name=name,
                description=description,
                entity_types=entity_types,
                relations=relations,
                triggers=[t for t in triggers if str(t).strip()],
            )
        )

    if not parsed:
        raise IntentMatchError(f"No valid intents in {path}")

    fallback = payload.get("fallback", {})
    if not isinstance(fallback, dict):
        fallback = {}
    return parsed, fallback


class IntentRouter:
    """Route questions to configured intents by trigger phrase matching."""

    def __init__(
        self,
        intents: Iterable[IntentDefinition] | None = None,
        *,
        fallback_max_hops: int = 2,
        fallback_max_rows: int = 20,
    ) -> None:
        self.intents = list(intents or [])
        self.fallback_max_hops = fallback_max_hops
        self.fallback_max_rows = fallback_max_rows

    @classmethod
    def from_file(
        cls,
        path: Path | str | None = None,
        *,
        fallback_max_hops: int = 2,
        fallback_max_rows: int = 20,
    ) -> "IntentRouter":
        intents, fallback = load_intent_contract(path)
        if fallback_max_hops == 2:
            fallback_max_hops = int(fallback.get("max_hops", fallback_max_hops))
        if fallback_max_rows == 20:
            fallback_max_rows = int(fallback.get("max_rows", fallback_max_rows))
        return cls(
            intents,
            fallback_max_hops=fallback_max_hops,
            fallback_max_rows=fallback_max_rows,
        )

    def route(self, question: str) -> IntentMatch | None:
        q = _normalize_text(question)
        if not q:
            return None

        candidates: list[tuple[int, int, int, IntentDefinition, str]] = []
        for intent_rank, intent in enumerate(self.intents):
            for trigger_rank, trigger in enumerate(intent.triggers):
                t = _normalize_text(str(trigger))
                if not t:
                    continue
                if t in q:
                    # prefer longer trigger phrase (more specific) then stable index order
                    confidence = len(t)
                    candidates.append(( -confidence, intent_rank, trigger_rank, intent, t))

        if not candidates:
            return None

        candidates.sort(key=lambda row: (row[0], row[1], row[2]))
        _, intent_rank, trigger_rank, intent, trigger = candidates[0]
        return IntentMatch(
            intent=intent,
            matched_trigger=trigger,
            confidence=-candidates[0][0],
            intent_rank=intent_rank,
            trigger_rank=trigger_rank,
        )
