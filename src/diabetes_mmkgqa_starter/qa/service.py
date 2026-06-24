"""QA service layer built on top of the portable backend."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import re

from diabetes_mmkgqa_starter.db import PortableGraphBackend
from diabetes_mmkgqa_starter.qa.intent_router import IntentMatch, IntentRouter


KG_VERSION_FALLBACK = "0.2.0"
SAFETY_NOTICE = "课程演示、非临床诊断：本内容仅用于教学演示，不构成医疗建议。"


@dataclass(frozen=True)
class QAResponse:
    """Canonical payload for QA execution results."""

    status: str
    question: str
    intent: str | None
    matched_trigger: str | None
    entity: dict | None
    answer: str
    rows: list[dict]
    images: list[dict]
    evidence_ids: list[str]
    source_ids: list[str]
    kg_version: str
    safety_notice: str = SAFETY_NOTICE
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "question": self.question,
            "intent": self.intent,
            "matched_trigger": self.matched_trigger,
            "entity": self.entity,
            "answer": self.answer,
            "rows": self.rows,
            "images": self.images,
            "evidence_ids": self.evidence_ids,
            "source_ids": self.source_ids,
            "kg_version": self.kg_version,
            "safety_notice": self.safety_notice,
            "metadata": self.metadata or {},
        }


class QAService:
    """Deterministic medical QA service without LLM-generated query synthesis."""

    IMAGE_RELATIONS = {"IMAGE_ASSOCIATED_WITH", "HAS_IMAGE_GRADE", "FROM_DATASET", "IN_SPLIT"}
    STOP_WORDS = {
        "of",
        "the",
        "for",
        "show",
        "what",
        "which",
        "are",
        "is",
        "a",
        "an",
        "to",
        "in",
        "on",
        "at",
        "be",
        "by",
        "or",
        "and",
        "can",
        "could",
        "symptom",
        "symptoms",
        "image",
        "images",
        "retina",
        "xray",
        "x-ray",
    }

    def __init__(
        self,
        *,
        backend: PortableGraphBackend,
        intents_path: str | Path | None = None,
    ) -> None:
        self.backend = backend
        self.router = IntentRouter.from_file(intents_path)

    def ask(self, question: str) -> dict:
        question = question.strip()
        if not question:
            return self._unknown(question, "empty question")

        intent_match = self.router.route(question)
        if intent_match is None:
            return self._unknown(question, "unrecognized intent")

        candidates = self._link_entity(question, intent_match)
        if not candidates:
            return self._unknown(
                question,
                "no entity matched",
                intent=intent_match.intent.name,
                matched_trigger=intent_match.matched_trigger,
                metadata={"candidates": []},
            )

        if len(candidates) > 1:
            ranked = [self._expose_candidate(row) for row in candidates]
            return {
                "status": "clarification",
                "question": question,
                "intent": intent_match.intent.name,
                "matched_trigger": intent_match.matched_trigger,
                "entity": None,
                "answer": self._format_ambiguity_message(intent_match, ranked),
                "rows": [],
                "images": [],
                "evidence_ids": [],
                "source_ids": [],
                "kg_version": self._infer_version(),
                "safety_notice": SAFETY_NOTICE,
                "metadata": {
                    "candidates": ranked,
                    "max_rows": self.router.fallback_max_rows,
                },
            }

        entity = candidates[0]
        entity_id = str(entity["node_id"])
        graph = self.backend.query_subgraph(entity_id, max_hops=self.router.fallback_max_hops)
        rows = self._collect_answers(intent_match, entity_id, graph["edges"])
        images = self._collect_images(intent_match, entity)
        evidence_ids = sorted({str(row.get("evidence_id", "")) for row in rows if row.get("evidence_id", "")})
        source_ids = sorted({str(row.get("source_id", "")) for row in rows if row.get("source_id", "")})

        if not rows and not images and intent_match.intent.relations:
            return {
                "status": "not_found",
                "question": question,
                "intent": intent_match.intent.name,
                "matched_trigger": intent_match.matched_trigger,
                "entity": self._expose_entity(entity),
                "answer": (
                    f"未能在当前知识库中找到关于 {entity.get('canonical_name', entity_id)} 的 "
                    f"{intent_match.intent.name} 信息。"
                ),
                "rows": [],
                "images": images,
                "evidence_ids": evidence_ids,
                "source_ids": source_ids,
                "kg_version": self._infer_version(rows, entity),
                "safety_notice": SAFETY_NOTICE,
                "metadata": {"max_hops": self.router.fallback_max_hops},
            }

        return {
            "status": "ok",
            "question": question,
            "intent": intent_match.intent.name,
            "matched_trigger": intent_match.matched_trigger,
            "entity": self._expose_entity(entity),
            "answer": self._format_answer(entity, rows, images, intent_match),
            "rows": rows,
            "images": images,
            "evidence_ids": evidence_ids,
            "source_ids": source_ids,
            "kg_version": self._infer_version(rows, entity),
            "safety_notice": SAFETY_NOTICE,
            "metadata": {
                "max_hops": self.router.fallback_max_hops,
                "nodes_in_subgraph": graph.get("node_count", 0),
            },
        }

    def _link_entity(self, question: str, intent_match: IntentMatch) -> list[dict]:
        query_candidates = self._candidate_search_queries(question, intent_match.matched_trigger)
        if not query_candidates:
            query_candidates = [question]

        nodes: list[dict] = []
        seen: set[str] = set()

        for query in query_candidates:
            for row in self._search_by_type(query, intent_match.intent.entity_types):
                node_id = str(row.get("node_id", ""))
                if node_id and node_id not in seen:
                    seen.add(node_id)
                    nodes.append(row)

            if nodes:
                break

        if nodes:
            return nodes[: self.router.fallback_max_rows]

        fallback_query = query_candidates[0]
        return self.backend.search_entities(
            fallback_query,
            node_types=None,
            limit=self.router.fallback_max_rows,
        )

    def _search_by_type(self, query: str, intent_types: list[str]) -> list[dict]:
        if not query:
            return []

        rows = self.backend.search_entities(
            query,
            node_types=intent_types or None,
            limit=self.router.fallback_max_rows,
        )
        if rows:
            return rows

        return self.backend.search_entities(
            query,
            node_types=None,
            limit=self.router.fallback_max_rows,
        )

    def _candidate_search_queries(self, question: str, trigger: str) -> list[str]:
        normalized_question = self._normalize_text(question)
        normalized_trigger = self._normalize_text(trigger)
        tokens = re.findall(r"[0-9a-zA-Z\u4e00-\u9fff]+", normalized_question)
        trigger_tokens = {t for t in re.findall(r"[0-9a-zA-Z\u4e00-\u9fff]+", normalized_trigger)}

        content_tokens = [
            token
            for token in tokens
            if token.lower() not in self.STOP_WORDS and token.lower() not in trigger_tokens
        ]

        if not content_tokens:
            return []

        candidates = [" ".join(content_tokens)]
        for token in content_tokens:
            if token and len(token) >= 2:
                candidates.append(token)
        return self._dedup_non_empty(candidates)

    def _collect_answers(self, intent_match: IntentMatch, center_node_id: str, edges: list[dict]) -> list[dict]:
        rows: list[dict] = []
        allowed = set(intent_match.intent.relations)
        for row in edges:
            relation = str(row.get("relation", ""))
            if relation not in allowed and allowed:
                continue

            head = str(row.get("head_id", ""))
            tail = str(row.get("tail_id", ""))
            if head != center_node_id and tail != center_node_id:
                continue
            rows.append(row)

        return sorted(rows, key=lambda item: (str(item.get("relation", "")), str(item.get("edge_id", ""))))

    def _collect_images(self, intent_match: IntentMatch, entity: dict) -> list[dict]:
        if not (set(intent_match.intent.relations) & self.IMAGE_RELATIONS):
            return []

        node_id = str(entity.get("node_id", ""))
        node_type = str(entity.get("node_type", ""))
        if not node_id:
            return []

        if node_type == "ImageGrade":
            return self.backend.search_images(grade_id=node_id, limit=self.router.fallback_max_rows)
        if node_type == "Dataset":
            return self.backend.search_images(dataset_id=node_id, limit=self.router.fallback_max_rows)
        if node_type == "DataSplit":
            return self.backend.search_images(split_id=node_id, limit=self.router.fallback_max_rows)
        if "IMAGE_ASSOCIATED_WITH" in intent_match.intent.relations:
            return self.backend.search_images(disease_id=node_id, limit=self.router.fallback_max_rows)
        return []

    def _format_answer(self, entity: dict, rows: list[dict], images: list[dict], intent_match: IntentMatch) -> str:
        node_name = str(entity.get("canonical_name", entity.get("node_id", "")))
        if not rows:
            if images:
                return f"已找到 {entity.get('canonical_name', node_name)} 的相关影像候选（{len(images)} 张）。"
            return f"未检索到 {entity.get('canonical_name', node_name)} 的回答条目。"

        rendered = []
        for row in rows:
            head_name = self._name(row.get("head_id", ""))
            tail_name = self._name(row.get("tail_id", ""))
            relation = str(row.get("relation", ""))
            if row.get("head_id") == entity.get("node_id"):
                rendered.append(f"{node_name} -> {relation} -> {tail_name}")
            elif row.get("tail_id") == entity.get("node_id"):
                rendered.append(f"{head_name} -> {relation} -> {node_name}")
            else:
                rendered.append(f"{head_name} -> {relation} -> {tail_name}")

        image_note = ""
        if images:
            image_note = f" 同时返回 {len(images)} 条图像候选。"
        relations_text = "、".join(rendered[: self.router.fallback_max_rows])
        return f"{intent_match.intent.name} 检索结果：{relations_text}。{image_note}"

    def _format_ambiguity_message(self, intent_match: IntentMatch, ranked_candidates: list[dict]) -> str:
        labels = [f"{item['canonical_name']}({item['node_type']})" for item in ranked_candidates]
        top = " / ".join(labels)
        return f"问题匹配到意图 {intent_match.intent.name}，但实体存在歧义。请指定目标实体：{top}"

    def _unknown(self, question: str, reason: str, *, intent: str | None = None, matched_trigger: str | None = None, metadata: dict | None = None) -> dict:
        return {
            "status": "not_found",
            "question": question,
            "intent": intent,
            "matched_trigger": matched_trigger,
            "entity": None,
            "answer": f"未在当前知识库找到可回答内容，原因：{reason}。",
            "rows": [],
            "images": [],
            "evidence_ids": [],
            "source_ids": [],
            "kg_version": self._infer_version(),
            "safety_notice": SAFETY_NOTICE,
            "metadata": metadata or {},
        }

    def _infer_version(self, rows: list[dict] | None = None, entity: dict | None = None) -> str:
        for row in rows or []:
            version = str(row.get("kg_version", "")).strip()
            if version:
                return version
        if entity:
            version = str(entity.get("kg_version", "")).strip()
            if version:
                return version

        stats = self.backend.get_stats()
        version = str(stats.get("kg_version", "")).strip()
        if version:
            return version
        return KG_VERSION_FALLBACK

    def _name(self, node_id: str) -> str:
        node = self.backend.get_node(node_id)
        if not node:
            return node_id
        return str(node.get("canonical_name", node_id))

    def _expose_entity(self, entity: dict) -> dict:
        return {
            "node_id": str(entity.get("node_id", "")),
            "canonical_name": str(entity.get("canonical_name", "")),
            "node_type": str(entity.get("node_type", "")),
            "knowledge_layer": str(entity.get("knowledge_layer", "")),
        }

    @staticmethod
    def _expose_candidate(entity: dict) -> dict:
        return {
            "node_id": str(entity.get("node_id", "")),
            "canonical_name": str(entity.get("canonical_name", "")),
            "node_type": str(entity.get("node_type", "")),
            "knowledge_layer": str(entity.get("knowledge_layer", "")),
        }

    @staticmethod
    def _normalize_text(value: str) -> str:
        return " ".join((value or "").strip().lower().split())

    @staticmethod
    def _dedup_non_empty(items: list[str]) -> list[str]:
        dedup: list[str] = []
        seen: set[str] = set()
        for item in items:
            cleaned = " ".join((item or "").split())
            if not cleaned or cleaned in seen:
                continue
            dedup.append(cleaned)
            seen.add(cleaned)
        return dedup
