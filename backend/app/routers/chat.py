"""Streaming chat endpoint (Server-Sent Events).

POST /chat streams the assistant's reply token-by-token, emits citation events
as tools are used, and persists the full exchange to SQLite. The first user
message of a new session becomes the session title.
"""

import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.db import store
from app.schemas import ChatRequest
from app.services import agent_service

router = APIRouter(tags=["chat"])


def _sse(event: dict) -> str:
    return f"data: {json.dumps(event)}\n\n"


@router.post("/chat")
async def chat(req: ChatRequest):
    # Resolve or create the session.
    session = store.get_session(req.session_id) if req.session_id else None
    if session is None:
        title = req.message[:60] + ("…" if len(req.message) > 60 else "")
        session = store.create_session(title=title)

    history = store.get_messages(session["id"])
    store.add_message(session["id"], "user", req.message)

    async def gen():
        # Tell the client which session this is (esp. for new sessions).
        yield _sse({"type": "session", "id": session["id"],
                    "title": session["title"]})

        final_content = ""
        final_citations = []
        async for event in agent_service.stream_chat(history, req.message):
            if event["type"] == "done":
                final_content = event["content"]
                final_citations = event["citations"]
            yield _sse(event)

        # Persist the assistant turn and bump the session.
        if final_content or final_citations:
            store.add_message(
                session["id"], "assistant", final_content, final_citations
            )
        store.touch_session(session["id"])

    return StreamingResponse(gen(), media_type="text/event-stream")
