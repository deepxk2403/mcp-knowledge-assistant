"""Chat history: list sessions, read a session's messages, delete a session."""

from typing import List

from fastapi import APIRouter, HTTPException

from app.db import store
from app.schemas import Message, Session

router = APIRouter(prefix="/sessions", tags=["history"])


@router.get("", response_model=List[Session])
def list_sessions():
    return store.list_sessions()


@router.get("/{session_id}/messages", response_model=List[Message])
def get_messages(session_id: str):
    if store.get_session(session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return store.get_messages(session_id)


@router.delete("/{session_id}", status_code=204)
def delete_session(session_id: str):
    if not store.delete_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return None
