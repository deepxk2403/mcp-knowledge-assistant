"""FastAPI application entrypoint.

Phase 0: health check + note CRUD. Chat, history, and documents routers are
added in later phases.

Run (from the backend/ directory):
    uvicorn app.main:app --reload --port 8000
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS, QDRANT_URL
from app.db.database import init_db
from app.routers import chat, history, notes
from app.services import notes_service

app = FastAPI(title="MCP Knowledge Assistant API", version="0.2.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def no_store(request: Request, call_next):
    """Prevent browsers/proxies from caching API reads, so a list fetched
    right after a create/delete always reflects the current state."""
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    return response


@app.on_event("startup")
def _startup():
    init_db()


app.include_router(notes.router)
app.include_router(chat.router)
app.include_router(history.router)


@app.get("/health", tags=["meta"])
def health():
    """Reports API status and whether Qdrant is reachable."""
    qdrant_ok = True
    detail = None
    try:
        notes_service.ensure_collection()
        stats = notes_service.stats()
    except Exception as e:  # noqa: BLE001
        qdrant_ok = False
        stats = {}
        detail = str(e)
    return {
        "status": "ok" if qdrant_ok else "degraded",
        "qdrant_url": QDRANT_URL,
        "qdrant_reachable": qdrant_ok,
        "notes": stats.get("total_notes"),
        "detail": detail,
    }
