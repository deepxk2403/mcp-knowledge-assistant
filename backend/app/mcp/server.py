"""Custom MCP server (FastMCP) — the tool layer for the agent.

Refactored for the product: the note tools now delegate to the shared
notes_service, so chat-driven actions and direct UI actions use identical
storage logic and stay in sync. Tools return human-readable strings because
the LLM agent consumes text; the underlying data is the same JSON the API
serves.

Run (from the backend/ directory so the `app` package is importable):
    python -m app.mcp.server

Endpoint: http://localhost:8001/mcp
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Allow `python app/mcp/server.py` as well as `-m app.mcp.server`.
BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastmcp import FastMCP

from app.config import TAVILY_API_KEY
from app.services import notes_service

mcp = FastMCP("PersonalKnowledge")


@mcp.tool()
def search_notes(query: str, top_k: int = 5):
    """Semantic search over saved notes."""
    notes = notes_service.search_notes(query=query, top_k=top_k)
    if not notes:
        return "No notes found."
    return "\n\n---\n\n".join(
        f"[id:{n['id']}] [score:{n.get('score')}] {n['title']}\n{n['content']}"
        for n in notes
    )


@mcp.tool()
def add_note(title: str, content: str, tags: Optional[str] = None):
    """Save a note to the vector store."""
    note = notes_service.create_note(title=title, content=content, tags=tags)
    return f"Saved note '{note['title']}' (id: {note['id']})."


@mcp.tool()
def list_notes(limit: int = 10):
    """List saved notes (most recently updated first)."""
    notes = notes_service.list_notes(limit=limit)
    if not notes:
        return "No notes saved yet."
    return "\n".join(
        f"{i + 1}. [id:{n['id']}] {n['title']} [{n['updated_at']}]"
        for i, n in enumerate(notes)
    )


@mcp.tool()
def update_note(
    note_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    tags: Optional[str] = None,
):
    """Update an existing note by id. Get ids from search_notes/list_notes."""
    note = notes_service.update_note(
        note_id, title=title, content=content, tags=tags
    )
    if note is None:
        return f"No note found with id {note_id}."
    return f"Updated note '{note['title']}' (id: {note['id']})."


@mcp.tool()
def delete_note(note_id: str):
    """Delete a note by id. Get ids from search_notes/list_notes."""
    ok = notes_service.delete_note(note_id)
    return (
        f"Deleted note {note_id}."
        if ok
        else f"No note found with id {note_id}."
    )


@mcp.tool()
def search_web(query: str, max_results: int = 5):
    """Web search using Tavily."""
    if not TAVILY_API_KEY:
        return "Web search unavailable."
    try:
        from tavily import TavilyClient

        response = TavilyClient(api_key=TAVILY_API_KEY).search(
            query=query, max_results=max_results
        )
        return "\n\n---\n\n".join(
            f"{r['title']}\n{r['url']}\n{r['content'][:300]}"
            for r in response["results"]
        )
    except Exception as e:  # noqa: BLE001
        return f"Search error: {e}"


@mcp.resource("notes://stats", description="Notes statistics")
def notes_stats():
    import json

    return json.dumps(notes_service.stats())


if __name__ == "__main__":
    print("MCP Server running on http://0.0.0.0:8001/mcp")
    mcp.run(transport="http", host="0.0.0.0", port=8001)
