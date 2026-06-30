# Backend — MCP Knowledge Assistant API

FastAPI backend that fronts the LangGraph agent + FastMCP tools + Qdrant.
Single-user demo, free stack (OpenRouter LLM + local FastEmbed embeddings).

## Phase 0 (done): Notes CRUD + shared service

- `app/services/notes_service.py` — single source of truth for note storage
  (UUID ids, full CRUD, `user_id`/`type` scoping). Imported by **both** the API
  and the MCP server, so chat-driven and UI-driven actions stay in sync.
- `app/main.py` — FastAPI app: `/health` + `/notes` CRUD.
- `app/mcp/server.py` — FastMCP tools, now delegating to `notes_service`.

## Run it

From the **`backend/`** directory, using the project venv at `../venv`.

1. Make sure Qdrant is up (Docker):
   ```
   docker ps   # expect a 'qdrant' container; if not: see ../README.md
   ```
2. Start the API:
   ```
   ../venv/Scripts/python -m uvicorn app.main:app --reload --port 8000
   ```
   - Health: http://localhost:8000/health
   - Interactive docs: http://localhost:8000/docs
3. (For chat, later) start the MCP server in another terminal:
   ```
   ../venv/Scripts/python -m app.mcp.server     # http://localhost:8001/mcp
   ```

## Phase 1 (done): Streaming chat + citations + history

- `app/services/agent_service.py` — builds the LangGraph agent (OpenRouter +
  MCP tools), streams answer tokens via `astream(stream_mode="messages")`, and
  captures tool calls.
- `app/services/citations.py` — parses tool outputs into structured sources.
- `app/db/` — SQLite store for sessions + messages (with citations JSON).
- `app/routers/chat.py` — `POST /chat` Server-Sent Events stream.
- `app/routers/history.py` — sessions list + message history.

`/chat` SSE event types: `session`, `citation`, `token`, `done`, `error`.

## API reference

| Method | Path                          | Purpose                       |
|--------|-------------------------------|-------------------------------|
| GET    | `/health`                     | API + Qdrant status           |
| GET    | `/notes`                      | List notes (newest first)     |
| GET    | `/notes/search?q=`            | Semantic search               |
| POST   | `/notes`                      | Create note                   |
| GET    | `/notes/{id}`                 | Get one note                  |
| PATCH  | `/notes/{id}`                 | Update (partial)              |
| DELETE | `/notes/{id}`                 | Delete                        |
| POST   | `/chat`                       | Streaming chat (SSE)          |
| GET    | `/sessions`                   | List chat sessions            |
| GET    | `/sessions/{id}/messages`     | Messages in a session         |
| DELETE | `/sessions/{id}`              | Delete a session              |

Both `/chat` (8000) and the MCP server (8001) must be running for chat.

## Coming next

- Phase 2: Next.js frontend (chat UI, notes, citations, sessions)
- Phase 3: document upload + ingestion
