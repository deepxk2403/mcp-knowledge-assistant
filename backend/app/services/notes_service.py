"""Shared note storage logic backed by Qdrant.

This module is the single source of truth for note CRUD. It is imported by
BOTH the FastAPI routers (direct UI actions) and the FastMCP server (chat-driven
actions), so the two paths never drift apart.

Notes are stored as points in the Qdrant collection with:
  - a UUID string id (so notes can be addressed for get/update/delete)
  - payload: {id, title, content, tags, created_at, updated_at, user_id, type}
  - type == "note" (documents added later use type == "document" in the same
    collection, kept separate via a filter)
"""

import time
import uuid
from typing import List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as qm

from app.config import COLLECTION, EMBED_DIM, QDRANT_URL, DEFAULT_USER
from app.services.embeddings import embed

_client: Optional[QdrantClient] = None


def _qdrant() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(url=QDRANT_URL)
    return _client


def ensure_collection() -> None:
    client = _qdrant()
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION not in existing:
        client.create_collection(
            COLLECTION,
            vectors_config=qm.VectorParams(
                size=EMBED_DIM, distance=qm.Distance.COSINE
            ),
        )


def _note_filter(user_id: str) -> qm.Filter:
    """Restrict operations to this user's notes (not documents)."""
    return qm.Filter(
        must=[
            qm.FieldCondition(key="type", match=qm.MatchValue(value="note")),
            qm.FieldCondition(
                key="user_id", match=qm.MatchValue(value=user_id)
            ),
        ]
    )


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def _to_dict(payload: dict, score: Optional[float] = None) -> dict:
    out = {
        "id": payload.get("id"),
        "title": payload.get("title", ""),
        "content": payload.get("content", ""),
        "tags": payload.get("tags", ""),
        "created_at": payload.get("created_at", ""),
        "updated_at": payload.get("updated_at", ""),
    }
    if score is not None:
        out["score"] = round(score, 4)
    return out


def create_note(
    title: str,
    content: str,
    tags: Optional[str] = None,
    user_id: str = DEFAULT_USER,
) -> dict:
    ensure_collection()
    note_id = str(uuid.uuid4())
    now = _now()
    payload = {
        "id": note_id,
        "title": title,
        "content": content,
        "tags": tags or "",
        "created_at": now,
        "updated_at": now,
        "user_id": user_id,
        "type": "note",
    }
    _qdrant().upsert(
        collection_name=COLLECTION,
        points=[
            qm.PointStruct(
                id=note_id,
                vector=embed(f"{title}\n{content}"),
                payload=payload,
            )
        ],
    )
    return _to_dict(payload)


def get_note(note_id: str, user_id: str = DEFAULT_USER) -> Optional[dict]:
    ensure_collection()
    records = _qdrant().retrieve(
        collection_name=COLLECTION, ids=[note_id], with_payload=True
    )
    if not records:
        return None
    payload = records[0].payload or {}
    if payload.get("type") != "note" or payload.get("user_id") != user_id:
        return None
    return _to_dict(payload)


def list_notes(
    limit: int = 50,
    offset: int = 0,
    user_id: str = DEFAULT_USER,
) -> List[dict]:
    ensure_collection()
    records, _ = _qdrant().scroll(
        collection_name=COLLECTION,
        scroll_filter=_note_filter(user_id),
        limit=limit,
        offset=offset,
        with_payload=True,
    )
    notes = [_to_dict(r.payload or {}) for r in records]
    notes.sort(key=lambda n: n.get("updated_at", ""), reverse=True)
    return notes


def search_notes(
    query: str,
    top_k: int = 5,
    user_id: str = DEFAULT_USER,
) -> List[dict]:
    ensure_collection()
    result = _qdrant().query_points(
        collection_name=COLLECTION,
        query=embed(query),
        query_filter=_note_filter(user_id),
        limit=top_k,
        with_payload=True,
    )
    return [_to_dict(p.payload or {}, score=p.score) for p in result.points]


def update_note(
    note_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    tags: Optional[str] = None,
    user_id: str = DEFAULT_USER,
) -> Optional[dict]:
    existing = get_note(note_id, user_id=user_id)
    if existing is None:
        return None

    new_title = title if title is not None else existing["title"]
    new_content = content if content is not None else existing["content"]
    new_tags = tags if tags is not None else existing["tags"]

    payload = {
        "id": note_id,
        "title": new_title,
        "content": new_content,
        "tags": new_tags,
        "created_at": existing["created_at"],
        "updated_at": _now(),
        "user_id": user_id,
        "type": "note",
    }

    # Re-embed only when the searchable text actually changed.
    text_changed = (
        title is not None and title != existing["title"]
    ) or (content is not None and content != existing["content"])

    point = qm.PointStruct(
        id=note_id,
        vector=embed(f"{new_title}\n{new_content}") if text_changed else None,
        payload=payload,
    )
    if text_changed:
        _qdrant().upsert(collection_name=COLLECTION, points=[point])
    else:
        # Metadata-only change: update payload without re-embedding.
        _qdrant().set_payload(
            collection_name=COLLECTION, payload=payload, points=[note_id]
        )
    return _to_dict(payload)


def delete_note(note_id: str, user_id: str = DEFAULT_USER) -> bool:
    if get_note(note_id, user_id=user_id) is None:
        return False
    _qdrant().delete(
        collection_name=COLLECTION,
        points_selector=qm.PointIdsList(points=[note_id]),
    )
    return True


def stats(user_id: str = DEFAULT_USER) -> dict:
    ensure_collection()
    count = _qdrant().count(
        collection_name=COLLECTION,
        count_filter=_note_filter(user_id),
        exact=True,
    ).count
    return {"total_notes": count}
