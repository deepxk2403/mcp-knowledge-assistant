"""Pydantic request/response models for the API."""

from typing import Optional

from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    tags: Optional[str] = None


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[str] = None


class Note(BaseModel):
    id: str
    title: str
    content: str
    tags: str = ""
    created_at: str = ""
    updated_at: str = ""
    score: Optional[float] = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: Optional[str] = None


class Session(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str


class Message(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    citations: list = []
    created_at: str
