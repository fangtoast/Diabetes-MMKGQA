"""QA service layer built on top of the portable backend."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import re

from diabetes_mmkgqa_starter.db import PortableGraphBackend
from diabetes_mmkgqa_starter.qa.intent_router import IntentMatch, IntentRouter
from diabetes_mmkgqa_starter.qa.query_templates import build_subgraph_query


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
    QUERY_ALIASES = {
        "糖网": "糖尿病视网膜病变",
    }
    RELATION_LABELS = {
        "HAS_SYMPTOM": "症状或表现",
        "RECOMMENDS_TEST": "建议检查",
        "HAS_TEST_ITEM": "相关检查项",
        "TREATED_BY_DRUG": "相关药物",
        "TREATED_BY_NONDRUG": "非药物干预",
        "TREATED_BY_OPERATION": "手术或操作",
        "HAS_ADVERSE_EFFECT": "不良反应",
        "HAS_DOSE_AMOUNT": "剂量",
        "HAS_ADMIN_METHOD": "给药方式",
        "HAS_DOSE_FREQUENCY": "给药频率",
        "HAS_DURATION": "持续时间",
        "AFFECTS_ANATOMY": "影响部位",
        "HAS_CLASS": "疾病分类",
        "GOVERNED_BY": "指南依据",
        "HAS_ICD_CODE": "ICD 编码",
        "HAS_REFERENCE_RANGE": "参考范围",
        "HAS_UNIT": "计量单位",
        "HAS_DIAGNOSTIC_THRESHOLD": "诊断阈值",
        "HAS_STAGE": "分期或阶段",
        "HAS_CASE": "示例病例",
        "IMAGE_ASSOCIATED_WITH": "相关影像",
        "HAS_IMAGE_GRADE": "影像分级",
        "FROM_DATASET": "数据集来源",
        "IN_SPLIT": "数据拆分",
    }
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
    CHINESE_QUERY_FILLERS = (
        "需要做哪些",
        "有哪些",
        "是什么",
        "请问",
        "查询",
        "展示",
        "显示",
        "看看",
        "相关",
        "需要做",
        "要查什么",
        "查什么",
        "有什么",
        "建议",
        "症状",
        "表现",
        "检查项",
        "检查",
        "检验",
        "用药剂量",
        "用药频次",
        "用药",
        "药物治疗",
        "药物",
        "不良反应",
        "副作用",
        "用法",
        "用量",
        "剂量",
        "给药频率",
        "持续时间",
        "影响部位",
        "解剖",
        "分类",
        "疾病类型",
        "指南",
        "依据",
        "icd编码",
        "诊断码",
        "编码",
        "参考范围",
        "正常范围",
        "诊断阈值",
        "分界值",
        "分期",
        "阶段",
        "病程分期",
        "分级",
        "影像示例",
        "相关图片",
        "有什么图片",
        "图像展示",
        "图片分级",
        "影像分级",
        "数据集图片",
        "影像数据集",
        "数据集",
        "训练集",
        "验证集",
        "测试集",
        "数据拆分",
        "病例",
        "示例病例",
        "临床案例",
        "示例样本",
        "图像",
        "影像",
        "图片",
        "什么",
        "哪些",
        "多少",
        "请",
        "的",
        "吗",
    )

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

        candidates = self._narrow_supported_candidates(intent_match, candidates)
        if len(candidates) > 1:
            ranked = [self._expose_candidate(row) for row in candidates]
            evidence_ids: list[str] = []
            source_ids: list[str] = []
            for row in ranked:
                source_ids.extend(self._split_values(str(row.get("source_ids", ""))))
            return {
                "status": "clarification",
                "question": question,
                "intent": intent_match.intent.name,
                "matched_trigger": intent_match.matched_trigger,
                "entity": None,
                "answer": self._format_ambiguity_message(intent_match, ranked),
                "rows": [],
                "images": [],
                "evidence_ids": sorted({id_ for id_ in evidence_ids if id_}),
                "source_ids": sorted({id_ for id_ in source_ids if id_}),
                "kg_version": self._infer_version(),
                "safety_notice": SAFETY_NOTICE,
                "metadata": {
                    "candidates": ranked,
                    "max_rows": self.router.fallback_max_rows,
                    "candidate_count": len(ranked),
                },
            }

        entity = candidates[0]
        entity_id = str(entity["node_id"])
        graph = self.backend.query_subgraph(entity_id, max_hops=self.router.fallback_max_hops)
        query_template = build_subgraph_query(
            intent_match=intent_match,
            node_id=entity_id,
            max_hops=self.router.fallback_max_hops,
        )
        rows = self._collect_answers(intent_match, entity_id, graph["edges"], query_template.allowed_relations)
        images = self._collect_images(intent_match, entity)
        evidence_ids, source_ids = self._collect_metadata_ids(entity, rows, images)
        kg_version = self._infer_version(rows, entity)

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
                "kg_version": kg_version,
                "safety_notice": SAFETY_NOTICE,
                "metadata": {
                    "max_hops": self.router.fallback_max_hops,
                    "query_template": {
                        "name": query_template.name,
                        "read_only": query_template.read_only,
                        "max_hops": query_template.max_hops,
                    },
                },
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
                "kg_version": kg_version,
                "safety_notice": SAFETY_NOTICE,
                "metadata": {
                    "max_hops": self.router.fallback_max_hops,
                    "nodes_in_subgraph": graph.get("node_count", 0),
                    "relation_count": len(rows),
                    "image_count": len(images),
                    "query_template": {
                        "name": query_template.name,
                        "read_only": query_template.read_only,
                        "max_hops": query_template.max_hops,
                    },
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

        embedded = self._embedded_entity_candidates(question, intent_match.intent.entity_types)
        if embedded:
            return embedded[: self.router.fallback_max_rows]

        fallback_query = query_candidates[0]
        return self.backend.search_entities(
            fallback_query,
            node_types=None,
            limit=self.router.fallback_max_rows,
        )

    def _narrow_supported_candidates(self, intent_match: IntentMatch, candidates: list[dict]) -> list[dict]:
        if len(candidates) <= 1:
            return candidates

        supported: list[dict] = []
        allowed_relations = tuple(intent_match.intent.relations)
        for candidate in candidates:
            node_id = str(candidate.get("node_id", ""))
            if not node_id:
                continue
            try:
                graph = self.backend.query_subgraph(node_id, max_hops=1)
            except KeyError:
                continue
            rows = self._collect_answers(intent_match, node_id, graph["edges"], allowed_relations)
            images = self._collect_images(intent_match, candidate)
            if rows or images:
                supported.append(candidate)

        if len(supported) == 1:
            return supported
        return candidates

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
        without_trigger = normalized_question
        if normalized_trigger:
            without_trigger = without_trigger.replace(normalized_trigger, " ")
        stripped_question = self._strip_chinese_question_fillers(without_trigger)
        expanded_question = self._expand_query_aliases(stripped_question)
        tokens = re.findall(r"[0-9a-zA-Z\u4e00-\u9fff]+", stripped_question)
        trigger_tokens = {t for t in re.findall(r"[0-9a-zA-Z\u4e00-\u9fff]+", normalized_trigger)}

        content_tokens = [
            token
            for token in tokens
            if token.lower() not in self.STOP_WORDS and token.lower() not in trigger_tokens
        ]

        if not content_tokens:
            return []

        candidates = []
        if expanded_question and expanded_question != stripped_question:
            candidates.append(expanded_question)
        candidates.append(" ".join(content_tokens))
        if re.search(r"[\u4e00-\u9fff]", stripped_question):
            candidates.append("".join(content_tokens))
        for token in content_tokens:
            if token and len(token) >= 2:
                candidates.append(token)
        return self._dedup_non_empty(candidates)

    def _embedded_entity_candidates(self, question: str, intent_types: list[str]) -> list[dict]:
        normalized_question = self._normalize_text(question).lower()
        if not normalized_question:
            return []

        requested = set(intent_types or [])
        matches: list[tuple[int, str, dict]] = []
        seen: set[str] = set()
        for node_id, row in self.backend.nodes.items():
            node_type = str(row.get("node_type", ""))
            if requested and node_type not in requested:
                continue
            labels = [
                str(row.get("canonical_name", "")),
                str(row.get("node_id", "")),
                *self._split_values(str(row.get("aliases", ""))),
                *self._split_values(str(row.get("synonyms", ""))),
            ]
            best_label = ""
            for label in labels:
                normalized_label = self._normalize_text(label).lower()
                if len(normalized_label) < 2:
                    continue
                if normalized_label in normalized_question:
                    if len(normalized_label) > len(best_label):
                        best_label = normalized_label
            if best_label and node_id not in seen:
                seen.add(node_id)
                matches.append((-len(best_label), node_id, row))

        matches.sort(key=lambda item: (item[0], item[1]))
        return [row for _, _, row in matches]

    def _collect_answers(
        self,
        intent_match: IntentMatch,
        center_node_id: str,
        edges: list[dict],
        allowed_relations: tuple[str, ...],
    ) -> list[dict]:
        rows: list[dict] = []
        allowed = set(allowed_relations)
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
        if images:
            return self._format_image_answer(node_name, rows, images)

        if not rows:
            return (
                f"未检索到 {entity.get('canonical_name', node_name)} 的回答条目。"
                f"当前知识库范围内未发现可支持该意图的条目。"
            )

        relation_groups: dict[str, list[str]] = {}
        for row in rows:
            head_name = self._name(row.get("head_id", ""))
            tail_name = self._name(row.get("tail_id", ""))
            relation = str(row.get("relation", ""))
            if row.get("head_id") == entity.get("node_id"):
                target_name = tail_name
            elif row.get("tail_id") == entity.get("node_id"):
                target_name = head_name
            else:
                target_name = f"{head_name} / {tail_name}"
            relation_groups.setdefault(relation, [])
            if target_name not in relation_groups[relation]:
                relation_groups[relation].append(target_name)

        sentences = []
        for relation in sorted(relation_groups):
            label = self.RELATION_LABELS.get(relation, "相关条目")
            names = relation_groups[relation]
            visible = "、".join(names[: self.router.fallback_max_rows])
            if len(names) > self.router.fallback_max_rows:
                visible += f"等 {len(names)} 项"
            sentences.append(f"{node_name}的{label}包括：{visible}")

        return "；".join(sentences) + "。以上内容均来自当前知识图谱的结构化证据。"

    def _format_image_answer(self, node_name: str, rows: list[dict], images: list[dict]) -> str:
        datasets = self._unique_values(row.get("dataset", "") for row in images)
        splits = self._unique_values(row.get("split", "") for row in images)
        grades = self._unique_values(row.get("grade", "") for row in images)
        sources = self._unique_values(row.get("source_id", "") for row in images)
        evidence = self._unique_values(row.get("evidence_id", "") for row in images)
        parts = [
            f"已在当前知识库中找到 {node_name} 的相关影像候选 {len(images)} 张",
            f"关联影像关系 {len(rows)} 条" if rows else "",
            f"数据集：{'、'.join(datasets[:3])}" if datasets else "",
            f"数据拆分：{'、'.join(splits[:4])}" if splits else "",
            f"分级示例：{'、'.join(grades[:5])}" if grades else "",
            f"来源：{'、'.join(sources[:4])}" if sources else "",
            f"证据 ID 示例：{'、'.join(evidence[:3])}" if evidence else "",
        ]
        return "；".join(part for part in parts if part) + "。这些影像仅用于课程演示和数据集级展示，不构成诊断。"

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
            "answer": f"未在当前知识库找到可回答内容，原因：{reason}。这是课程演示，非临床诊断用途。",
            "rows": [],
            "images": [],
            "evidence_ids": [],
            "source_ids": [],
            "kg_version": self._infer_version(),
            "safety_notice": SAFETY_NOTICE,
            "metadata": metadata or {"query_supported": False},
        }

    def _collect_metadata_ids(self, entity: dict, rows: list[dict], images: list[dict] | None = None) -> tuple[list[str], list[str]]:
        evidence_ids: set[str] = set()
        source_ids: set[str] = set()

        for row in rows:
            evidence_ids.update(self._split_values(str(row.get("evidence_id", ""))))
            source_ids.update(self._split_values(str(row.get("source_id", ""))))
        for row in images or []:
            evidence_ids.update(self._split_values(str(row.get("evidence_id", ""))))
            source_ids.update(self._split_values(str(row.get("source_id", ""))))

        source_ids.update(self._split_values(str(entity.get("source_ids", ""))))
        evidence_ids.update(self._split_values(str(entity.get("evidence_id", ""))))

        return sorted(evidence_ids), sorted(source_ids)

    @staticmethod
    def _split_values(value: str) -> list[str]:
        if not value:
            return []
        parts = []
        for part in str(value).replace("|", ",").replace(";", ",").split(","):
            item = part.strip()
            if item:
                parts.append(item)
        return parts

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
            "source_ids": str(entity.get("source_ids", "")),
            "evidence_id": str(entity.get("evidence_id", "")),
            "kg_version": str(entity.get("kg_version", "")),
        }

    @staticmethod
    def _expose_candidate(entity: dict) -> dict:
        return {
            "node_id": str(entity.get("node_id", "")),
            "canonical_name": str(entity.get("canonical_name", "")),
            "node_type": str(entity.get("node_type", "")),
            "knowledge_layer": str(entity.get("knowledge_layer", "")),
            "source_ids": str(entity.get("source_ids", "")),
        }

    @staticmethod
    def _normalize_text(value: str) -> str:
        return " ".join((value or "").strip().lower().split())

    @classmethod
    def _strip_chinese_question_fillers(cls, value: str) -> str:
        text = value or ""
        for phrase in cls.CHINESE_QUERY_FILLERS:
            text = re.sub(re.escape(phrase), " ", text, flags=re.IGNORECASE)
        return " ".join(text.split())

    @classmethod
    def _expand_query_aliases(cls, value: str) -> str:
        text = value or ""
        for alias, canonical in cls.QUERY_ALIASES.items():
            text = re.sub(re.escape(alias), canonical, text, flags=re.IGNORECASE)
        return " ".join(text.split())

    @staticmethod
    def _unique_values(values) -> list[str]:  # type: ignore[no-untyped-def]
        seen: set[str] = set()
        output: list[str] = []
        for value in values:
            text = str(value or "").strip()
            if not text or text in seen:
                continue
            seen.add(text)
            output.append(text)
        return output

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
