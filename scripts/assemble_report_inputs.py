"""Assemble reproducible report input artifacts for the project handoff."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import textwrap
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover - yaml fallback for environments without runtime dependency
    yaml = None


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Expected file does not exist: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _read_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    if yaml is None:
        raise RuntimeError("PyYAML is required to read data/source_manifest.yaml")
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return payload if isinstance(payload, dict) else {}


def _render_markdown(stats: dict[str, Any], manifest: dict[str, Any], demo: dict[str, Any] | None, output_path: Path) -> str:
    safety_notice = "课程演示、非临床诊断"
    layer_counts = stats.get("layered_statistics", {}).get("layer_counts", {})
    layer_breakdown = stats.get("layered_statistics", {}).get("layer_breakdown", {})

    lines = [
        "# Report Inputs",
        "",
        f"- 生成时间：{datetime.now(timezone.utc).isoformat()}",
        f"- 数据版本：{stats.get('kg_version', 'unknown')}",
        f"- 根证据：所有医学问答与 API 响应均要求返回 evidence/source/kg_version/safety_notice。",
        f"- 安全声明：{safety_notice}",
        "",
        "## 快速命令",
        "",
        "```bash",
        "python -m diabetes_mmkgqa_starter.cli --repo-root . data",
        "python -m diabetes_mmkgqa_starter.cli --repo-root . kg --skip-retina --skip-pneumonia",
        "python -m diabetes_mmkgqa_starter.cli --repo-root . load --backend portable --output-dir data/processed --ontology-path configs/ontology.yaml",
        "python -m diabetes_mmkgqa_starter.cli demo --repo-root . --processed-dir data/processed --demo-output-dir docs/cases --demo-output-json demo_cases.json --no-demo-screenshots",
        "python scripts/assemble_report_inputs.py --stats-path data/processed/stats.json --output docs/report_inputs.md",
        "```",
        "",
        "## 统计指标（来自 stats.json）",
        "",
        f"- canonical_entity_count: {stats.get('canonical_entity_count', 0)}",
        f"- unique_semantic_triples_count: {stats.get('unique_semantic_triples_count', 0)}",
        f"- evidence_backed_relation_claim_count: {stats.get('evidence_backed_relation_claim_count', 0)}",
        f"- provenance_edge_count: {stats.get('provenance_edge_count', 0)}",
        f"- image_metadata_count: {stats.get('image_metadata_count', 0)}",
        f"- image_node_count: {stats.get('image_node_count', 0)}",
        f"- node_count: {stats.get('node_count', 0)}",
        f"- edge_count: {stats.get('edge_count', 0)}",
        "",
        f"- A/B/C Layered Nodes: A={layer_counts.get('node', {}).get('A', 0)} / B={layer_counts.get('node', {}).get('B', 0)} / C={layer_counts.get('node', {}).get('C', 0)}",
        f"- A/B/C Layered Edges: A={layer_counts.get('edge', {}).get('A', 0)} / B={layer_counts.get('edge', {}).get('B', 0)} / C={layer_counts.get('edge', {}).get('C', 0)}",
        "",
    ]

    if layer_breakdown:
        lines.extend(
            [
                "### 层内细分",
                "",
                f"- B层 Guideline 数：{layer_breakdown.get('B', {}).get('guideline_count', 0)}",
                f"- B层 ICD_Code 数：{layer_breakdown.get('B', {}).get('icd_code_count', 0)}",
                f"- B层 StandardRule 数：{layer_breakdown.get('B', {}).get('standard_rule_count', 0)}",
                f"- C层 Disease 数：{layer_breakdown.get('C', {}).get('disease_count', 0)}",
                f"- C层 图像边数：{layer_breakdown.get('C', {}).get('multimodal_edge_count', 0)}",
                "",
            ]
        )

    sources = manifest.get("sources", []) if isinstance(manifest.get("sources"), list) else []
    if sources:
        lines.extend(["## 数据源清单（from source_manifest）", "", "| source_id | root_file | checksum | license_or_terms |"])
        lines.append("|---|---|---|---|")
        for source in sources:
            lines.append(
                "| "
                + str(source.get("source_id", "")) + " | "
                + str(source.get("root_file", "")) + " | "
                + str(source.get("checksum", "")) + " | "
                + str(source.get("license_or_terms", "")) + " |"
            )
        lines.append("")

    lines.extend(["## Demo cases", ""])
    if demo and demo.get("cases"):
        lines.append(f"- case_count: {demo.get('case_count', len(demo.get('cases', [])))}")
        lines.append("- cases:")
        for case in demo["cases"]:
            lines.append(
                textwrap.indent(
                    f"- `{case.get('case_id', '')}` {case.get('title', '')} "
                    f"({case.get('status', '')})",
                    "  ",
                )
            )
            if case.get("screenshot"):
                lines.append(textwrap.indent(f"screenshot: {case['screenshot'].get('path')}", "    "))
    else:
        lines.append("- 未检测到演示案例输出；执行命令见上文 `cli demo`。")

    lines.extend(
        [
            "",
            "## 交付材料",
            "",
            "- `data/processed/stats.json`（本次报告统计）",
            "- `data/processed/nodes.csv` / `edges.csv`（图谱主文件）",
            "- `data/processed/schema.json`（Schema 校验结果）",
            "- `docs/cases/demo_cases.json`（固定 demo 输入与输出）",
            "- `docs/screenshots/`（演示截图，若环境支持可生成）",
            "",
        ]
    )

    return "\n".join(lines).strip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Assemble report input documents for DOC-001.")
    parser.add_argument("--stats-path", default="data/processed/stats.json")
    parser.add_argument("--manifest-path", default="data/source_manifest.yaml")
    parser.add_argument("--demo-path", default="docs/cases/demo_cases.json")
    parser.add_argument("--output", default="docs/report_inputs.md")
    args = parser.parse_args(argv)

    stats_path = Path(args.stats_path)
    manifest_path = Path(args.manifest_path)
    demo_path = Path(args.demo_path)
    output_path = Path(args.output)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    stats = _read_json(stats_path)
    manifest = _read_manifest(manifest_path)
    demo = _read_json(demo_path) if demo_path.exists() else None

    output_path.write_text(_render_markdown(stats, manifest, demo, output_path), encoding="utf-8")
    print(f"[report] wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
