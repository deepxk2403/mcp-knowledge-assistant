"""
Custom MCP server using FastMCP v2+.

Exposes:
1. search_notes
2. add_note
3. list_notes
4. search_web

Run:
python mcp_server.py

Endpoint:
http://localhost:8001/mcp

Test:
npx @modelcontextprotocol/inspector http://localhost:8001/mcp
"""

import json
import os
import time
import uuid
from typing import Optional

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    PointStruct,
)

load_dotenv()

# Local, free embedding model (no API key, runs on CPU). The model is
# downloaded once (~130 MB) on first use and cached locally.
EMBED_MODEL_NAME = os.environ.get(
    "EMBED_MODEL", "BAAI/bge-small-en-v1.5"
)

# Lazy-initialized so the server boots instantly and only pays the model
# load/download cost the first time an embedding is actually needed.
_embed_model = None


def _get_embed_model():
    global _embed_model
    if _embed_model is None:
        _embed_model = TextEmbedding(model_name=EMBED_MODEL_NAME)
    return _embed_model


qdrant = QdrantClient(
    url=os.environ.get(
        "QDRANT_URL",
        "http://localhost:6333"
    )
)

COLLECTION = "mcp_notes"
EMBED_DIM = 384  # BAAI/bge-small-en-v1.5 produces 384-dim vectors

mcp = FastMCP("PersonalKnowledge")


def _ensure_collection():

    existing = [
        c.name
        for c in qdrant.get_collections().collections
    ]

    if COLLECTION not in existing:

        qdrant.create_collection(
            COLLECTION,
            vectors_config=VectorParams(
                size=EMBED_DIM,
                distance=Distance.COSINE,
            ),
        )


def _embed(text: str):

    # fastembed returns a generator of numpy arrays; take the first vector
    # and convert to a plain Python list for Qdrant.
    embedding = next(iter(_get_embed_model().embed([text])))
    return embedding.tolist()


@mcp.tool()
def search_notes(
    query: str,
    top_k: int = 5,
):

    """
    Semantic note search.
    """

    _ensure_collection()

    # qdrant-client 1.12+ replaced .search() with .query_points().
    results = qdrant.query_points(
        collection_name=COLLECTION,
        query=_embed(query),
        limit=top_k,
    ).points

    if not results:
        return "No notes found."

    return "\n\n---\n\n".join(
        [
            (
                f"[Score:{r.score:.3f}] "
                f"{r.payload.get('title','?')}\n"
                f"{r.payload.get('content','')}"
            )
            for r in results
        ]
    )


@mcp.tool()
def add_note(
    title: str,
    content: str,
    tags: Optional[str] = None,
):

    """
    Save note to vector store.
    """

    _ensure_collection()

    note_id = (
        abs(hash(uuid.uuid4().hex))
        % (2**63)
    )

    qdrant.upsert(
        collection_name=COLLECTION,
        points=[
            PointStruct(
                id=note_id,
                vector=_embed(
                    f"{title}\n{content}"
                ),
                payload={
                    "title": title,
                    "content": content,
                    "tags": tags or "",
                    "created_at": time.strftime(
                        "%Y-%m-%d %H:%M"
                    ),
                },
            )
        ],
    )

    return f"Saved note: '{title}'"


@mcp.tool()
def list_notes(
    limit: int = 10,
):

    """
    List saved notes.
    """

    _ensure_collection()

    results, _ = qdrant.scroll(
        collection_name=COLLECTION,
        limit=limit,
        with_payload=True,
    )

    if not results:
        return "No notes saved yet."

    return "\n".join(
        [
            (
                f"{i+1}. "
                f"{r.payload.get('title','?')} "
                f"[{r.payload.get('created_at','')}]"
            )
            for i, r in enumerate(results)
        ]
    )


@mcp.tool()
def search_web(
    query: str,
    max_results: int = 5,
):

    """
    Web search using Tavily.
    """

    api_key = os.environ.get(
        "TAVILY_API_KEY",
        ""
    )

    if not api_key:
        return "Web search unavailable."

    try:

        from tavily import TavilyClient

        response = (
            TavilyClient(
                api_key=api_key
            )
            .search(
                query=query,
                max_results=max_results,
            )
        )

        return "\n\n---\n\n".join(
            [
                (
                    f"{r['title']}\n"
                    f"{r['url']}\n"
                    f"{r['content'][:300]}"
                )
                for r in response["results"]
            ]
        )

    except Exception as e:
        return f"Search error: {e}"


@mcp.resource(
    "notes://stats",
    description="Notes statistics",
)
def notes_stats():

    _ensure_collection()

    info = qdrant.get_collection(
        COLLECTION
    )

    return json.dumps(
        {
            "total_notes":
            info.points_count
        }
    )


if __name__ == "__main__":

    print(
        "MCP Server running"
    )

    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8001,
    )
