"""Assemble reproducible report inputs for the diabetes multimodal KGQA project."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import argparse
import csv
import json
import textwrap
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover
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


def _md_cell(value: Any) -> str:
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ")


def _count_csv_column(path: Path, column: str) -> dict[str, int]:
    if not path.exists():
        return {}
    counts: Counter[str] = Counter()
    with path.open("r", encoding="utf-8", newline="") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            value = (row.get(column) or "").strip()
            if value:
                counts[value] += 1
    return dict(sorted(counts.items()))


def _read_processed_counts(processed_dir: Path) -> dict[str, dict[str, int]]:
    return {
        "edge_extraction_methods": _count_csv_column(processed_dir / "edges.csv", "extraction_method"),
        "edge_sources": _count_csv_column(processed_dir / "edges.csv", "source_id"),
    }


def _source_status(source: dict[str, Any]) -> str:
    source_id = str(source.get("source_id", ""))
    checksum = str(source.get("checksum", ""))
    if source_id == "diakg" and "TO_BE_FILLED" in checksum:
        return "authorized full root required before full DiaKG claims"
    if source_id == "manual_diakg_fallback":
        return "fallback fixture for offline course demo"
    return "registered source"


def _render_markdown(
    stats: dict[str, Any],
    manifest: dict[str, Any],
    demo: dict[str, Any] | None,
    processed_counts: dict[str, dict[str, int]] | None = None,
) -> str:
    safety_notice = "Educational non-clinical notice (for teaching demonstration only)."
    layer_counts = stats.get("layered_statistics", {}).get("layer_counts", {})
    layer_breakdown = stats.get("layered_statistics", {}).get("layer_breakdown", {})
    schema_counts = stats.get("schema_validation", {}).get("counts", {})
    nodes_by_type = schema_counts.get("nodes_by_type", {})
    relations = schema_counts.get("relations", {})
    edge_extraction_methods = (processed_counts or {}).get("edge_extraction_methods", {})
    edge_sources = (processed_counts or {}).get("edge_sources", {})
    warnings = stats.get("warnings", [])

    lines = [
        "# Report Inputs",
        "",
        f"- generation_time: {datetime.now(timezone.utc).isoformat()}",
        f"- data_version: {stats.get('kg_version', 'unknown')}",
        "- reproducibility: All outputs can be regenerated from the listed commands and checked config versions.",
        "- evidence_contract: evidence/source/kg_version/safety_notice",
        "- safety_notice: " + safety_notice,
        "",
        "## Reproducible commands",
        "",
        "```bash",
        "python -m diabetes_mmkgqa_starter.cli data --repo-root .",
        "python -m diabetes_mmkgqa_starter.cli kg --repo-root .",
        "python -m diabetes_mmkgqa_starter.cli load --backend portable --repo-root . --output-dir data/processed --ontology-path configs/ontology.yaml",
        "python -m diabetes_mmkgqa_starter.cli demo --repo-root . --processed-dir data/processed --demo-output-dir docs/cases --demo-output-json demo_cases.json",
        "python -m diabetes_mmkgqa_starter.cli report --repo-root .",
        "python -m diabetes_mmkgqa_starter.cli package --repo-root . --package-output-dir deliverables --package-name diabetes_mmkgqa_deliverables.zip",
        "```",
        "",
        "## Stats summary (from data/processed/stats.json)",
        "",
        f"- canonical_entity_count: {stats.get('canonical_entity_count', 0)}",
        f"- unique_semantic_triples_count: {stats.get('unique_semantic_triples_count', 0)}",
        f"- evidence_backed_relation_claim_count: {stats.get('evidence_backed_relation_claim_count', 0)}",
        f"- provenance_edge_count: {stats.get('provenance_edge_count', 0)}",
        f"- image_metadata_count: {stats.get('image_metadata_count', 0)}",
        f"- image_node_count: {stats.get('image_node_count', 0)}",
        f"- node_count: {stats.get('node_count', 0)}",
        f"- edge_count: {stats.get('edge_count', 0)}",
        f"- entity_type_count: {len(nodes_by_type)}",
        f"- relation_type_count: {len(relations)}",
        f"- A/B/C Layered Nodes: A={layer_counts.get('node', {}).get('A', 0)} / B={layer_counts.get('node', {}).get('B', 0)} / C={layer_counts.get('node', {}).get('C', 0)}",
        f"- A/B/C Layered Edges: A={layer_counts.get('edge', {}).get('A', 0)} / B={layer_counts.get('edge', {}).get('B', 0)} / C={layer_counts.get('edge', {}).get('C', 0)}",
        "",
    ]

    if warnings:
        lines.extend(["### Warnings", ""])
        for item in warnings:
            lines.append(f"- {item}")
        lines.append("")

    if layer_breakdown:
        lines.extend(
            [
                "### Layer detail (C layer)",
                "",
                f"- C-layer disease nodes: {layer_breakdown.get('C', {}).get('disease_count', 0)}",
                f"- C-layer image nodes: {layer_breakdown.get('C', {}).get('image_node_count', 0)}",
                f"- C-layer multimodal edge count: {layer_breakdown.get('C', {}).get('multimodal_edge_count', 0)}",
                "",
            ]
        )

    if nodes_by_type:
        lines.extend(["### Entity types", "", "| entity_type | count |", "|---|---:|"])
        for node_type, count in sorted(nodes_by_type.items()):
            lines.append(f"| {_md_cell(node_type)} | {count} |")
        lines.append("")

    if relations:
        lines.extend(["### Relation types", "", "| relation_type | count |", "|---|---:|"])
        for relation, count in sorted(relations.items()):
            lines.append(f"| {_md_cell(relation)} | {count} |")
        lines.append("")

    if edge_extraction_methods:
        lines.extend(["### Edge extraction methods", "", "| extraction_method | edge_count |", "|---|---:|"])
        for method, count in sorted(edge_extraction_methods.items()):
            lines.append(f"| {_md_cell(method)} | {count} |")
        lines.append("")

    if edge_sources:
        lines.extend(["### Edge source counts", "", "| source_id | edge_count |", "|---|---:|"])
        for source_id, count in sorted(edge_sources.items()):
            lines.append(f"| {_md_cell(source_id)} | {count} |")
        lines.append("")

    sources = manifest.get("sources", []) if isinstance(manifest.get("sources"), list) else []
    if sources:
        lines.extend(
            [
                "## Source manifest",
                "",
                "Full DiaKG raw data is not redistributed by this repository. The reproducible offline course graph uses `manual_diakg_fallback` unless an authorized `diakg` root is provided and its checksum is recorded.",
                "",
                "| source_id | root_file | extractor | checksum | status |",
                "|---|---|---|---|---|",
            ]
        )
        for source in sources:
            lines.append(
                "| "
                + _md_cell(source.get("source_id", "")) + " | "
                + _md_cell(source.get("root_file", "")) + " | "
                + _md_cell(source.get("extractor", "")) + " | "
                + _md_cell(source.get("checksum", "")) + " | "
                + _md_cell(_source_status(source)) + " |"
            )
        lines.append("")

    lines.extend(["## Demo cases", ""])
    if demo and demo.get("cases"):
        cases = demo.get("cases", [])
        lines.append(f"- case_count: {demo.get('case_count', len(cases))}")
        lines.append("- cases:")
        for case in cases:
            line = textwrap.indent(
                f"- `{case.get('case_id', '')}` {case.get('title', '')} ({case.get('status', '')})",
                "  ",
            )
            lines.append(line)
            screenshot = case.get("screenshot")
            if isinstance(screenshot, dict):
                status = screenshot.get("status", "")
                path = screenshot.get("path")
                lines.append(textwrap.indent(f"screenshot: {status} {path or ''}".rstrip(), "    "))
    else:
        lines.append("- demo cases were not found in docs/cases/demo_cases.json")

    lines.extend(
        [
            "",
            "## Deliverables",
            "",
            "- data/processed/stats.json",
            "- data/processed/nodes.csv",
            "- data/processed/edges.csv",
            "- data/processed/schema.json",
            "- docs/cases/demo_cases.json",
            "- docs/screenshots/ (ui_qa.png, ui_image.png, ui_stats.png, demo_001.png ... demo_005.png)",
            "- deliverables/diabetes_mmkgqa_deliverables.zip",
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
    processed_counts = _read_processed_counts(stats_path.parent)

    output_path.write_text(_render_markdown(stats, manifest, demo, processed_counts), encoding="utf-8")
    print(f"[report] wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
