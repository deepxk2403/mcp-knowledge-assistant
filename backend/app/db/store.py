"""CRUD for chat sessions and messages."""

import json
import time
import uuid
from typing import List, Optional

from app.db.database import get_conn


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


# --- sessions ---

def create_session(title: str = "New chat") -> dict:
    sid = str(uuid.uuid4())
    now = _now()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO sessions (id, title, created_at, updated_at) "
            "VALUES (?, ?, ?, ?)",
            (sid, title, now, now),
        )
    return {"id": sid, "title": title, "created_at": now, "updated_at": now}


def list_sessions() -> List[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM sessions ORDER BY updated_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def get_session(session_id: str) -> Optional[dict]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
    return dict(row) if row else None


def touch_session(session_id: str, title: Optional[str] = None) -> None:
    with get_conn() as conn:
        if title is not None:
            conn.execute(
                "UPDATE sessions SET updated_at = ?, title = ? WHERE id = ?",
                (_now(), title, session_id),
            )
        else:
            conn.execute(
                "UPDATE sessions SET updated_at = ? WHERE id = ?",
                (_now(), session_id),
            )


def delete_session(session_id: str) -> bool:
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        return cur.rowcount > 0


# --- messages ---

def add_message(
    session_id: str,
    role: str,
    content: str,
    citations: Optional[list] = None,
) -> dict:
    mid = str(uuid.uuid4())
    now = _now()
    cjson = json.dumps(citations or [])
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO messages (id, session_id, role, content, citations, "
            "created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (mid, session_id, role, content, cjson, now),
        )
    return {
        "id": mid,
        "session_id": session_id,
        "role": role,
        "content": content,
        "citations": citations or [],
        "created_at": now,
    }


def get_messages(session_id: str) -> List[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM messages WHERE session_id = ? ORDER BY created_at ASC",
            (session_id,),
        ).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["citations"] = json.loads(d.get("citations") or "[]")
        out.append(d)
    return out
