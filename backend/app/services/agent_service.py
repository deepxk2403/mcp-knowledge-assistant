"""Builds and runs the LangGraph agent, streaming tokens and citations.

The agent connects to the FastMCP server (the tool layer) and uses an
OpenRouter model. We stream via `astream_events` so we can emit answer tokens
as they arrive AND capture tool calls (to build citations) in the same pass.
"""

import asyncio
from typing import AsyncGenerator, Dict, List

from langchain_core.messages import AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient

from app.config import OPENROUTER_API_KEY, OPENROUTER_MODEL
from app.services.citations import CITABLE, build_citation

# Prefer the new API; fall back to the LangGraph prebuilt if unavailable.
try:
    from langchain.agents import create_agent as _create_agent
except Exception:  # noqa: BLE001
    from langgraph.prebuilt import create_react_agent as _create_agent

MCP_URL = "http://localhost:8001/mcp"

SYSTEM_PROMPT = (
    "You are a helpful personal knowledge assistant. "
    "You can save, search, list, update, and delete the user's notes, and "
    "search the web.\n"
    "Use search_web for current events, live facts, or anything that is not in "
    "the user's notes. Use the notes tools for the user's own saved content.\n"
    "IMPORTANT: The user's notes can change between messages — they may add or "
    "delete notes in the UI at any time. Earlier messages in this conversation "
    "may be out of date. Whenever the user asks what notes they have, to recall "
    "something, or to find/search notes, you MUST call list_notes or "
    "search_notes to get the CURRENT state before answering. Never answer about "
    "their notes from memory or earlier turns. "
    "Cite what you used. Be concise."
)

_agent = None
_lock = asyncio.Lock()


async def _get_agent():
    """Lazily build the agent once per process (connect MCP, load tools)."""
    global _agent
    if _agent is not None:
        return _agent
    async with _lock:
        if _agent is not None:
            return _agent
        client = MultiServerMCPClient(
            {"knowledge": {"url": MCP_URL, "transport": "http"}}
        )
        tools = await client.get_tools()
        model = ChatOpenAI(
            model=OPENROUTER_MODEL,
            temperature=0,
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )
        _agent = _create_agent(model, tools)
        return _agent


def _to_lc_messages(history: List[Dict], user_message: str) -> List[Dict]:
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in history:
        if m.get("role") in ("user", "assistant") and m.get("content"):
            msgs.append({"role": m["role"], "content": m["content"]})
    msgs.append({"role": "user", "content": user_message})
    return msgs


async def stream_chat(
    history: List[Dict], user_message: str
) -> AsyncGenerator[Dict, None]:
    """Yield event dicts:
       {"type":"token","text":...}
       {"type":"citation","data":{...}}
       {"type":"done","content":...,"citations":[...]}
       {"type":"error","message":...}
    """
    agent = await _get_agent()
    messages = _to_lc_messages(history, user_message)

    answer_parts: List[str] = []
    citations: List[Dict] = []
    # Map tool_call_id -> the args the model passed (to recover the query for
    # citations, since ToolMessage itself doesn't carry the input args).
    tool_args: Dict[str, dict] = {}

    def _content_text(content) -> str:
        if isinstance(content, list):
            return "".join(
                b.get("text", "") for b in content if isinstance(b, dict)
            )
        return content or ""

    try:
        async for item in agent.astream(
            {"messages": messages}, stream_mode="messages"
        ):
            chunk = item[0] if isinstance(item, tuple) else item

            # Remember tool-call args from the model's tool-requesting message.
            for tc in getattr(chunk, "tool_calls", None) or []:
                if tc.get("id"):
                    tool_args[tc["id"]] = tc.get("args", {}) or {}

            if isinstance(chunk, ToolMessage):
                name = getattr(chunk, "name", "")
                if name in CITABLE:
                    args = tool_args.get(
                        getattr(chunk, "tool_call_id", None), {}
                    )
                    citation = build_citation(name, args, chunk.content)
                    citations.append(citation)
                    yield {"type": "citation", "data": citation}

            elif isinstance(chunk, AIMessage):
                text = _content_text(chunk.content)
                if text:
                    answer_parts.append(text)
                    yield {"type": "token", "text": text}

        yield {
            "type": "done",
            "content": "".join(answer_parts).strip(),
            "citations": citations,
        }

    except Exception as e:  # noqa: BLE001
        yield {"type": "error", "message": str(e)}
