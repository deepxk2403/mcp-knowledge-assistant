"""Note CRUD endpoints. Thin layer over notes_service."""

from typing import List

from fastapi import APIRouter, HTTPException, Query

from app.schemas import Note, NoteCreate, NoteUpdate
from app.services import notes_service

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("", response_model=List[Note])
def list_notes(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    return notes_service.list_notes(limit=limit, offset=offset)


@router.get("/search", response_model=List[Note])
def search_notes(
    q: str = Query(..., min_length=1),
    top_k: int = Query(5, ge=1, le=50),
):
    return notes_service.search_notes(query=q, top_k=top_k)


@router.post("", response_model=Note, status_code=201)
def create_note(body: NoteCreate):
    return notes_service.create_note(
        title=body.title, content=body.content, tags=body.tags
    )


@router.get("/{note_id}", response_model=Note)
def get_note(note_id: str):
    note = notes_service.get_note(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.patch("/{note_id}", response_model=Note)
def update_note(note_id: str, body: NoteUpdate):
    note = notes_service.update_note(
        note_id,
        title=body.title,
        content=body.content,
        tags=body.tags,
    )
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: str):
    if not notes_service.delete_note(note_id):
        raise HTTPException(status_code=404, detail="Note not found")
    return None
