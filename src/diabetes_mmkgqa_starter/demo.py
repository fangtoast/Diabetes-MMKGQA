"""Deterministic demo case runner for the educational platform."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import shutil
import subprocess
import tempfile
from typing import Any, TypedDict

from diabetes_mmkgqa_starter.db import PortableGraphBackend
from diabetes_mmkgqa_starter.qa import QAService


class DemoCaseError(ValueError):
    """Raised for unrecoverable demo generation configuration."""


class DemoDefinition(TypedDict):
    case_id: str
    title: str
    kind: str
    question: str
    note: str


DEFAULT_DEMO_CASES: list[DemoDefinition] = [
    {
        "case_id": "DEMO-001",
        "title": "Disease ambiguity clarification",
        "kind": "qa",
        "question": "症状 糖尿病",
        "note": "Demonstrate ambiguity handling for duplicated disease nodes.",
    },
    {
        "case_id": "DEMO-002",
        "title": "Guideline ambiguity clarification",
        "kind": "qa",
        "question": "指南 高血压",
        "note": "Demonstrate guideline intent with duplicated disease names.",
    },
    {
        "case_id": "DEMO-003",
        "title": "ICD clarification",
        "kind": "qa",
        "question": "ICD 编码 糖尿病视网膜病变",
        "note": "Demonstrate ICD lookup flow and disambiguation.",
    },
    {
        "case_id": "DEMO-004",
        "title": "Graph neighborhood check",
        "kind": "graph",
        "question": "e69defa2ca273bb80e04bac560004b920ef4bf03",
        "note": "Read graph neighborhood for a deterministic disease node id.",
    },
    {
        "case_id": "DEMO-005",
        "title": "Statistics snapshot",
        "kind": "stats",
        "question": "",
        "note": "Read current KG stats payload.",
    },
]


def run_demo_cases(
    *,
    repo_root: Path,
    output_dir: Path,
    processed_dir: Path,
    intents_path: Path,
    screenshot_dir: Path,
    output_json: str = "demo_cases.json",
    cases: list[DemoDefinition] | None = None,
    capture_screenshots: bool = True,
) -> dict[str, Any]:
    """Generate fixed demo case outputs against the portable backend."""

    demo_cases = cases or list(DEFAULT_DEMO_CASES)
    backend = PortableGraphBackend.from_dir(processed_dir)
    service = QAService(backend=backend, intents_path=intents_path)

    output_dir.mkdir(parents=True, exist_ok=True)
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    normalized_cases: list[dict[str, Any]] = []
    for case in demo_cases:
        result = _run_single_case(case, service, backend)
        normalized_cases.append(result)

    payload: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "kg_version": _infer_kg_version(backend),
        "case_count": len(normalized_cases),
        "cases": normalized_cases,
        "safety_notice": "课程演示、非临床诊断：本内容仅用于教学演示，不构成医疗建议。",
    }

    output_path = output_dir / output_json
    _write_json(output_path, payload)

    screenshot_payloads = _capture_case_html_screenshots(
        normalized_cases,
        screenshot_dir=screenshot_dir,
        capture=capture_screenshots,
    )

    for case in normalized_cases:
        matching = [item for item in screenshot_payloads if item["case_id"] == case["case_id"]]
        case["screenshot"] = matching[0] if matching else {"path": None, "status": "not_captured"}

    _write_json(output_path, payload)
    return {
        "output_path": str(output_path),
        "case_count": len(normalized_cases),
        "screenshot_count": len([case for case in screenshot_payloads if case.get("path") is not None]),
        "payload": payload,
    }


def _run_single_case(case: DemoDefinition, service: QAService, backend: PortableGraphBackend) -> dict[str, Any]:
    kind = case["kind"]
    if kind == "qa":
        response = service.ask(case["question"])
        return {
            "case_id": case["case_id"],
            "title": case["title"],
            "kind": kind,
            "question": case["question"],
            "note": case["note"],
            "status": response.get("status"),
            "response": response,
        }

    if kind == "graph":
        center_node_id = case["question"].strip()
        if not center_node_id:
            disease_nodes = [
                node_id
                for node_id, row in backend.nodes.items()
                if row.get("node_type") == "Disease"
            ]
            if not disease_nodes:
                raise DemoCaseError(f"DEMO case {case['case_id']} has no Disease node for graph neighborhood check")
            center_node_id = sorted(disease_nodes)[0]
        if not center_node_id:
            raise DemoCaseError(f"DEMO case {case['case_id']} requires a center node id")
        if center_node_id not in backend.nodes:
            return {
                "case_id": case["case_id"],
                "title": case["title"],
                "kind": kind,
                "question": center_node_id,
                "note": case["note"],
                "status": "not_found",
                "response": {
                    "node_id": center_node_id,
                    "error": "center_node_not_found",
                    "safety_notice": "课程演示、非临床诊断：本内容仅用于教学演示，不构成医疗建议。",
                },
            }

        graph = backend.query_subgraph(center_node_id, max_hops=2)
        return {
            "case_id": case["case_id"],
            "title": case["title"],
            "kind": kind,
            "question": center_node_id,
            "note": case["note"],
            "status": "ok",
            "response": {
                "node_id": center_node_id,
                "subgraph": graph,
                "safety_notice": "课程演示、非临床诊断：本内容仅用于教学演示，不构成医疗建议。",
            },
        }

    if kind == "stats":
        return {
            "case_id": case["case_id"],
            "title": case["title"],
            "kind": kind,
            "question": case["question"],
            "note": case["note"],
            "status": "ok",
            "response": {
                "metrics": backend.get_stats(),
                "safety_notice": "课程演示、非临床诊断：本内容仅用于教学演示，不构成医疗建议。",
            },
        }

    raise DemoCaseError(f"Unsupported demo case kind: {kind}")


def _capture_case_html_screenshots(
    cases: list[dict[str, Any]],
    *,
    screenshot_dir: Path,
    capture: bool,
) -> list[dict[str, str | None]]:
    if not capture:
        return [{"case_id": item["case_id"], "path": None, "status": "skipped"} for item in cases]

    chrome_path = shutil.which("chrome") or shutil.which("google-chrome") or shutil.which("msedge")
    if not chrome_path:
        for candidate in [
            Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
            Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
            Path("C:/Program Files/Microsoft/Edge/Application/msedge.exe"),
            Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
        ]:
            if candidate.exists():
                chrome_path = str(candidate)
                break

    if not chrome_path:
        return [{"case_id": item["case_id"], "path": None, "status": "browser_not_available"} for item in cases]

    output: list[dict[str, str | None]] = []
    for item in cases:
        screenshot_file = screenshot_dir / f"{item['case_id'].lower().replace('-', '_')}.png"
        rendered = _render_case_html(item)
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as fp:
            fp.write(rendered)
            html_path = Path(fp.name)

        args = [
            chrome_path,
            "--headless",
            "--disable-gpu",
            "--hide-scrollbars",
            "--window-size=1280,900",
            f"--screenshot={screenshot_file}",
            html_path.as_uri(),
        ]
        try:
            proc = subprocess.run(args, check=False, capture_output=True, text=True)
            if proc.returncode != 0:
                output.append({"case_id": item["case_id"], "path": None, "status": "failed"})
            else:
                output.append({"case_id": item["case_id"], "path": str(screenshot_file), "status": "captured"})
        finally:
            try:
                html_path.unlink()
            except OSError:
                pass

    return output


def _render_case_html(case: dict[str, Any]) -> str:
    payload = json.dumps(case, ensure_ascii=False, indent=2)
    escaped = payload.replace("</script>", "<\\/script>")
    return f"""<!doctype html>
<html lang=\"zh-CN\">
  <head>
    <meta charset=\"utf-8\" />
    <title>Demo {case['case_id']}</title>
    <style>
      body {{
        font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, Arial, sans-serif;
        padding: 16px;
      }}
      pre {{
        white-space: pre-wrap;
        word-break: break-word;
      }}
    </style>
  </head>
  <body>
    <h1>Demo {case['case_id']}: {case['title']}</h1>
    <pre>{escaped}</pre>
  </body>
</html>
"""


def _infer_kg_version(backend: PortableGraphBackend) -> str:
    try:
        return str(backend.get_stats().get("kg_version", "0.2.0"))
    except Exception:
        return "0.2.0"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
