"""FastAPI app for the course demo KGQA service."""

from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path
import struct
from typing import Any
import zlib

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from diabetes_mmkgqa_starter.db import PortableGraphBackend
from diabetes_mmkgqa_starter.qa import QAService
from diabetes_mmkgqa_starter.qa.service import SAFETY_NOTICE


DEFAULT_BACKEND_DIR = Path("data") / "processed"
DEFAULT_INTENT_PATH = Path("configs") / "intents.yaml"
DEFAULT_FRONTEND_DIR = Path("frontend")


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


def _with_preview_urls(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        image_id = str(item.get("image_id", "")).strip()
        if image_id:
            item.setdefault("preview_url", f"/images/{image_id}/preview.png")
        output.append(item)
    return output


def _enrich_qa_payload(payload: dict[str, Any]) -> dict[str, Any]:
    images = payload.get("images")
    if isinstance(images, list):
        payload["images"] = _with_preview_urls([dict(item) for item in images if isinstance(item, dict)])
    return payload


def _chunk(kind: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(kind + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", crc)


def _encode_png(array: Any) -> bytes:
    """Encode a numpy-like image array as a minimal PNG without extra dependencies."""

    try:
        import numpy as np
    except Exception as exc:
        raise RuntimeError("numpy is required to render image previews.") from exc

    image = np.asarray(array)
    if image.ndim == 3 and image.shape[-1] == 1:
        image = image[:, :, 0]
    if image.ndim not in {2, 3}:
        raise ValueError(f"Unsupported image shape: {image.shape}")

    if image.dtype != np.uint8:
        image = image.astype("float32")
        min_value = float(np.nanmin(image)) if image.size else 0.0
        max_value = float(np.nanmax(image)) if image.size else 0.0
        if max_value > min_value:
            image = (image - min_value) / (max_value - min_value) * 255.0
        image = np.clip(image, 0, 255).astype("uint8")

    height, width = int(image.shape[0]), int(image.shape[1])
    if image.ndim == 2:
        color_type = 0
        rows = [b"\x00" + image[row].tobytes() for row in range(height)]
    else:
        channels = int(image.shape[2])
        if channels == 3:
            color_type = 2
            rows = [b"\x00" + image[row].tobytes() for row in range(height)]
        elif channels == 4:
            color_type = 6
            rows = [b"\x00" + image[row].tobytes() for row in range(height)]
        else:
            raise ValueError(f"Unsupported channel count: {channels}")

    ihdr = struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0)
    return b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            _chunk(b"IHDR", ihdr),
            _chunk(b"IDAT", zlib.compress(b"".join(rows), 9)),
            _chunk(b"IEND", b""),
        ]
    )


def _source_npz_path(repo_root: Path, source_id: str) -> Path | None:
    if source_id == "retinamnist":
        return repo_root / "data" / "raw" / "retinamnist" / "retinamnist_224.npz"
    if source_id == "pneumoniamnist":
        return repo_root / "data" / "raw" / "pneumoniamnist" / "pneumoniamnist_224.npz"
    return None


def _render_image_preview(repo_root: Path, image_row: dict[str, Any]) -> bytes:
    source_id = str(image_row.get("source_id", "")).strip()
    source_file = str(image_row.get("source_file", "")).strip()
    image_index_raw = str(image_row.get("image_index", "")).strip()
    source_path = _source_npz_path(repo_root, source_id)
    if source_path is None:
        raise FileNotFoundError(f"Unsupported image source: {source_id}")
    if not source_path.exists():
        raise FileNotFoundError(f"Raw image root is missing: {source_path}")
    if not source_file:
        raise ValueError("Image row is missing source_file.")

    try:
        image_index = int(image_index_raw)
    except ValueError as exc:
        raise ValueError(f"Invalid image_index: {image_index_raw}") from exc

    try:
        import numpy as np
    except Exception as exc:
        raise RuntimeError("numpy is required to render image previews.") from exc

    with np.load(source_path, allow_pickle=False) as payload:
        if source_file not in payload.files:
            raise KeyError(f"{source_file} is not present in {source_path.name}")
        images = payload[source_file]
        if image_index < 0 or image_index >= len(images):
            raise IndexError(f"image_index out of range: {image_index}")
        return _encode_png(images[image_index])


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
    frontend_dir = root / DEFAULT_FRONTEND_DIR
    if frontend_dir.exists():
        app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="frontend")

        @app.get("/", include_in_schema=False)
        def root_redirect() -> RedirectResponse:
            return RedirectResponse(url="/ui")

        @app.get("/ui", include_in_schema=False)
        def ui_entrypoint() -> FileResponse:
            return FileResponse(frontend_dir / "index.html")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
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
        return _safe_notice(_enrich_qa_payload(dict(response)))

    @app.get("/entities/search")
    def entities_search(
            query: str | None = Query(default=None, description="Entity text or alias"),
            q: str | None = Query(default=None, description="Legacy alias for query"),
            node_types: str | None = Query(default=None, description="Comma-separated node types"),
            limit: int = Query(default=20, ge=1, le=200),
        ) -> dict[str, Any]:
            backend = _require_backend_ready(app)
            effective_query = query if query is not None else q
            if not effective_query:
                raise HTTPException(
                    status_code=422,
                    detail=[{"type": "missing", "loc": ["query", "query"], "msg": "Field required", "input": None}],
                )
            rows = backend.search_entities(
                effective_query,
                node_types=_parse_csv_list(node_types) or None,
                limit=limit,
            )
            return _safe_notice(
                {
                    "query": effective_query,
                    "node_types": _parse_csv_list(node_types),
                    "count": len(rows),
                    "items": rows,
                }
            )

    @app.get("/graph/overview")
    def graph_overview(
            limit: int = Query(default=120, ge=1, le=500),
            node_types: str | None = Query(default=None, description="Comma-separated node types"),
            relations: str | None = Query(default=None, description="Comma-separated relations"),
            layers: str | None = Query(default=None, description="Comma-separated knowledge layers"),
            include_images: bool = Query(default=False),
        ) -> dict[str, Any]:
            backend = _require_backend_ready(app)
            result = backend.query_overview(
                limit=limit,
                node_types=_parse_csv_list(node_types) or None,
                relations=_parse_csv_list(relations) or None,
                layers=_parse_csv_list(layers) or None,
                include_images=include_images,
            )
            return _safe_notice(result)

    @app.get("/graph/subgraph")
    def graph_subgraph(
            center_node_id: str | None = Query(default=None, description="Center node id"),
            node: str | None = Query(default=None, description="Legacy alias for center_node_id"),
            max_hops: int = Query(default=2, ge=0, le=5),
        ) -> dict[str, Any]:
            backend = _require_backend_ready(app)
            effective_node_id = center_node_id if center_node_id is not None else node
            if not effective_node_id:
                raise HTTPException(
                    status_code=422,
                    detail=[{"type": "missing", "loc": ["query", "center_node_id"], "msg": "Field required", "input": None}],
                )
            try:
                result = backend.query_subgraph(effective_node_id, max_hops=max_hops)
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
        image_items = _with_preview_urls(rows)
        return _safe_notice(
            {
                "count": len(image_items),
                "items": image_items,
                "images": image_items,
            }
        )

    @app.get("/images/{image_id}/preview.png")
    def image_preview(image_id: str) -> Response:
        state = _get_state(app)
        backend = _require_backend_ready(app)
        row = backend.images.get(image_id)
        if row is None:
            raise HTTPException(status_code=404, detail=f"Image not found: {image_id}")
        try:
            content = _render_image_preview(state.repo_root, row)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=503, detail=str(exc))
        except (KeyError, IndexError, RuntimeError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc))
        return Response(
            content=content,
            media_type="image/png",
            headers={"Cache-Control": "public, max-age=86400"},
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
