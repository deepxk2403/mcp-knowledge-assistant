# Project 3 — Custom MCP Server + LangGraph Agent (Fully-Free Stack)

A personal knowledge assistant built on the **Model Context Protocol (MCP)**.
A custom FastMCP server exposes tools (semantic note memory + web search); a
LangGraph ReAct agent discovers and calls those tools over HTTP.

```
User Query -> LangGraph Agent -> MultiServerMCPClient -> MCP Server (FastMCP)
                                                          |-- Qdrant (notes)  + FastEmbed (local)
                                                          |-- Tavily (web)
```

## Free stack (no paid keys)

| Concern        | Original          | This setup (free)                         |
|----------------|-------------------|-------------------------------------------|
| Embeddings     | OpenAI            | **FastEmbed** `BAAI/bge-small-en-v1.5` (local, no key) |
| Agent LLM      | Anthropic Claude  | **OpenRouter** free model (one free key)  |
| Web search     | Tavily            | Tavily (free tier, optional)              |
| Vector store   | Qdrant (Docker)   | Qdrant (Docker)                           |

The note-memory tools (`add_note`, `list_notes`, `search_notes`) need **no API
key at all** — embeddings run locally. Only the agent's LLM needs a (free)
OpenRouter key.

## Status on this machine

| Component                    | Status                                          |
|------------------------------|-------------------------------------------------|
| venv + dependencies          | installed (`venv/`)                             |
| Qdrant (Docker, :6333)       | running                                         |
| MCP server (:8001)           | running                                         |
| Memory pipeline (no keys)    | VERIFIED via `test_memory.py`                   |
| Agent wiring                 | VERIFIED via `test_connection.py`               |
| Full agent run               | needs `OPENROUTER_API_KEY` in `.env`            |

## 1. Add your free OpenRouter key

Get one at https://openrouter.ai/keys, then put it in [.env](.env):

```
OPENROUTER_API_KEY=sk-or-...
# OPENROUTER_MODEL=meta-llama/llama-3.3-70b-instruct:free   # optional override
TAVILY_API_KEY=                                              # optional web search
```

> The agent is a tool-calling ReAct agent, so the OpenRouter model **must
> support function/tool calling**. Good free options: `meta-llama/llama-3.3-70b-instruct:free`,
> `qwen/qwen-2.5-72b-instruct`, `deepseek/deepseek-chat`. If a model ignores
> tools, switch `OPENROUTER_MODEL`.

## 2. Start the MCP server (own terminal)

```
venv/Scripts/python mcp_server.py
```
Serves MCP at http://localhost:8001/mcp.

## 3. Verify without keys (optional)

```
venv/Scripts/python test_connection.py   # tool discovery + list_notes
venv/Scripts/python test_memory.py       # add -> list -> semantic search
```

## 4. Run the agent (needs OpenRouter key)

```
venv/Scripts/python mcp_agent.py "Save a note titled 'RAG Tips': Always use hybrid search"
venv/Scripts/python mcp_agent.py "What did I learn about retrieval?"
venv/Scripts/python mcp_agent.py "What notes do I have?"
venv/Scripts/python mcp_agent.py "Search the web for news about LangGraph 2026"   # needs Tavily
```

## Compatibility fixes applied vs. the original handout

The handout code targets older library versions. Updated for current releases:

1. **Embeddings -> local FastEmbed** (`mcp_server.py`). No OpenAI key; `EMBED_DIM`
   changed 1536 -> 384 to match `bge-small-en-v1.5`.
2. **Agent LLM -> OpenRouter** via `ChatOpenAI(base_url=...)` (`mcp_agent.py`),
   replacing `init_chat_model("anthropic:...")`.
3. **`MultiServerMCPClient` is not a context manager** anymore
   (`langchain-mcp-adapters` 0.1.0+) — instantiated directly, then `get_tools()`.
4. **`qdrant.search()` -> `qdrant.query_points(...).points`** (qdrant-client 1.12+).

## Inspect the server interactively (optional)

```
npx @modelcontextprotocol/inspector http://localhost:8001/mcp
```
