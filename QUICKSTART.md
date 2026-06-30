# Quickstart — Full App (UI + Backend)

The product runs as **four** processes. Start them in this order.

| # | Process            | Port | Command (from `mcp-knowledge-agent/`)                              |
|---|--------------------|------|-------------------------------------------------------------------|
| 1 | Qdrant (Docker)    | 6333 | `docker start qdrant`  (or the `docker run …` in `README.md`)      |
| 2 | MCP server (tools) | 8001 | `cd backend && ../venv/Scripts/python -m app.mcp.server`          |
| 3 | Backend API        | 8000 | `cd backend && ../venv/Scripts/python -m uvicorn app.main:app --port 8000` |
| 4 | Frontend (React)   | 3000 | `cd frontend && npm run dev`                                       |

Then open **http://localhost:3000**.

## Prerequisites

- Docker Desktop running (for Qdrant).
- `OPENROUTER_API_KEY` set in `.env` (free key — the only key required).
- Python deps installed in `venv` (`backend/requirements.txt`); frontend deps
  installed (`cd frontend && npm install`).

## What you can do in the UI

- **Chat tab** — talk to the assistant. It can save/search/list/update/delete
  notes and (with a Tavily key) search the web. Answers stream in; sources show
  as clickable citation chips. Past chats live in the sidebar.
- **Notes tab** — semantic search, create, edit, delete notes directly.

Notes created in either place are the same data (the API and the MCP tools share
one `notes_service` against the same Qdrant collection).

## Architecture (recap)

```
React (3000) → FastAPI (8000) → LangGraph agent → FastMCP (8001) → Qdrant (6333)
                     │                                              + FastEmbed (local)
                     └→ SQLite (chat history)
```

## Troubleshooting

- **Chat says it couldn't reach a service** → Docker/Qdrant is down. Start
  Docker, then `docker start qdrant`.
- **Chat errors with rate limit** → the free OpenRouter model is busy; retry, or
  change `OPENROUTER_MODEL` in `.env`.
- **Frontend can't reach API** → make sure the backend (8000) and MCP (8001) are
  both running before chatting.
