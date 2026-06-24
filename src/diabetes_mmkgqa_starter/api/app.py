"""FastAPI app for the course demo KGQA service."""

from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from diabetes_mmkgqa_starter.db import PortableGraphBackend
from diabetes_mmkgqa_starter.qa import QAService
from diabetes_mmkgqa_starter.qa.service import SAFETY_NOTICE


DEFAULT_BACKEND_DIR = Path("data") / "processed"
DEFAULT_INTENT_PATH = Path("configs") / "intents.yaml"


@dataclass
class RuntimeState:
    """Runtime backend state used by endpoints."""

    backend: PortableGraphBackend | None
    qa_service: QAService | None
    startup_error: str | None
    repo_root: Path
    processed_dir: Path


class QARequest(BaseModel):
    """Request payload for QA endpoint."""

    question: str


def _resolve_repo_root(repo_root: str | Path | None) -> Path:
    if repo_root is None:
        return Path(__file__).resolve().parents[3]
    return Path(repo_root).resolve()


def _safe_notice(payload: dict[str, Any]) -> dict[str, Any]:
    payload.setdefault("safety_notice", SAFETY_NOTICE)
    return payload


def _parse_csv_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    parts: list[str] = []
    for token in raw.replace(";", ",").split(","):
        token = token.strip()
        if token:
            parts.append(token)
    return parts


def _bootstrap_components(
    repo_root: Path,
    processed_dir: str | Path,
    intents_path: str | Path | None,
) -> RuntimeState:
    resolved_processed = Path(processed_dir)
    if not resolved_processed.is_absolute():
        resolved_processed = repo_root / resolved_processed

    resolved_intents = Path(intents_path) if intents_path is not None else None
    if resolved_intents is not None and not resolved_intents.is_absolute():
        resolved_intents = repo_root / resolved_intents

    try:
        backend = PortableGraphBackend.from_dir(
            resolved_processed,
            ontology_path=repo_root / "configs/ontology.yaml",
        )
        service = QAService(
            backend=backend,
            intents_path=resolved_intents,
        )
        return RuntimeState(
            backend=backend,
            qa_service=service,
            startup_error=None,
            repo_root=repo_root,
            processed_dir=resolved_processed,
        )
    except Exception as exc:  # keep service startable even when backend is blocked
        return RuntimeState(
            backend=None,
            qa_service=None,
            startup_error=str(exc),
            repo_root=repo_root,
            processed_dir=resolved_processed,
        )


def _get_state(app: FastAPI) -> RuntimeState:
    state = getattr(app.state, "runtime", None)
    if not isinstance(state, RuntimeState):
        raise RuntimeError("Runtime state is unavailable. Did the app initialize correctly?")
    return state


def _require_qa_ready(app: FastAPI) -> QAService:
    state = _get_state(app)
    if state.qa_service is None:
        raise HTTPException(
            status_code=503,
            detail="Knowledge graph backend is not available yet. Please run data/kg/load first.",
        )
    return state.qa_service


def _require_backend_ready(app: FastAPI) -> PortableGraphBackend:
    state = _get_state(app)
    if state.backend is None:
        raise HTTPException(
            status_code=503,
            detail="Knowledge graph backend is not available yet. Please run data/kg/load first.",
        )
    return state.backend


def create_app(
    *,
    repo_root: str | Path | None = None,
    processed_dir: str | Path = DEFAULT_BACKEND_DIR,
    intents_path: str | Path | None = DEFAULT_INTENT_PATH,
) -> FastAPI:
    """Build the educational API application."""

    root = _resolve_repo_root(repo_root)
    state = _bootstrap_components(root, processed_dir, intents_path)

    app = FastAPI(
        title="Diabetes Multi-disease Multimodal KGQA API",
        version="0.1.0",
        description=(
            "Course demo API for multimodal medical KGQA. "
            "This is educational only and not a clinical diagnostic tool."
        ),
    )
    app.state.runtime = state

    @app.get("/health")
    def health() -> dict[str, Any]:
        state = _get_state(app)
        payload: dict[str, Any] = {
            "status": "ready" if state.backend is not None else "blocked",
            "backend": "portable",
            "backend_ready": state.backend is not None,
            "repo_root": str(state.repo_root),
            "processed_dir": str(state.processed_dir),
        }
        if state.startup_error is not None:
            payload["startup_error"] = state.startup_error
        if state.backend is not None:
            payload["summary"] = asdict(state.backend.summary)
        return _safe_notice(payload)

    @app.post("/qa")
    def answer_question(payload: QARequest) -> dict[str, Any]:
        service = _require_qa_ready(app)
        response = service.ask(payload.question)
        return _safe_notice(dict(response))

    @app.get("/entities/search")
    def entities_search(
        query: str = Query(..., min_length=1, description="Entity text or alias"),
        node_types: str | None = Query(default=None, description="Comma-separated node types"),
        limit: int = Query(default=20, ge=1, le=200),
    ) -> dict[str, Any]:
        backend = _require_backend_ready(app)
        rows = backend.search_entities(
            query,
            node_types=_parse_csv_list(node_types) or None,
            limit=limit,
        )
        return _safe_notice(
            {
                "query": query,
                "node_types": _parse_csv_list(node_types),
                "count": len(rows),
                "items": rows,
            }
        )

    @app.get("/graph/subgraph")
    def graph_subgraph(
        center_node_id: str = Query(..., min_length=1, description="Center node id"),
        max_hops: int = Query(default=2, ge=0, le=5),
    ) -> dict[str, Any]:
        backend = _require_backend_ready(app)
        try:
            result = backend.query_subgraph(center_node_id, max_hops=max_hops)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc))
        return _safe_notice(result)

    @app.get("/images/search")
    def images_search(
        disease_id: str | None = Query(default=None),
        grade_id: str | None = Query(default=None),
        dataset_id: str | None = Query(default=None),
        split_id: str | None = Query(default=None),
        limit: int = Query(default=20, ge=1, le=200),
    ) -> dict[str, Any]:
        backend = _require_backend_ready(app)
        rows = backend.search_images(
            disease_id=disease_id,
            grade_id=grade_id,
            dataset_id=dataset_id,
            split_id=split_id,
            limit=limit,
        )
        return _safe_notice(
            {
                "count": len(rows),
                "items": rows,
            }
        )

    @app.get("/stats")
    def graph_stats() -> dict[str, Any]:
        backend = _require_backend_ready(app)
        return _safe_notice(backend.get_stats())

    @app.exception_handler(HTTPException)
    async def _http_exception_handler(_request, exc):  # type: ignore[no-untyped-def]
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "safety_notice": SAFETY_NOTICE},
        )

    return app


app = create_app()
