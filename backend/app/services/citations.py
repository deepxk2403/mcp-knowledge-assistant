"""Turn raw agent tool calls into structured citation objects for the UI.

The MCP tools return human-readable strings (the LLM consumes text), so we
parse those strings back into structured items. Parsing is best-effort and
defensive: if a format is unexpected, we fall back to a raw-text source rather
than failing the whole response.

Citation shape returned to the frontend:
  {
    "tool":  "search_notes" | "search_web" | <other>,
    "type":  "note" | "web" | "generic",
    "query": "<the tool's query argument>",
    "items": [ {...} ]          # structured when possible
  }
"""

import re
from typing import Any, List


def extract_text(output: Any) -> str:
    """Tool outputs can be a str, a ToolMessage, or a list of content dicts."""
    if output is None:
        return ""
    if isinstance(output, str):
        return output
    # LangChain message-like object
    content = getattr(output, "content", None)
    if content is not None:
        output = content
    if isinstance(output, list):
        parts = []
        for item in output:
            if isinstance(item, dict):
                parts.append(item.get("text", "") or item.get("content", ""))
            else:
                parts.append(str(item))
        return "\n".join(p for p in parts if p)
    return str(output)


def _query_of(tool_input: Any) -> str:
    if isinstance(tool_input, dict):
        return tool_input.get("query") or tool_input.get("q") or ""
    return ""


def _parse_notes(text: str) -> List[dict]:
    items = []
    for chunk in text.split("\n\n---\n\n"):
        chunk = chunk.strip()
        if not chunk:
            continue
        m = re.search(r"\[id:([^\]]+)\]", chunk)
        s = re.search(r"\[score:([^\]]+)\]", chunk)
        # title is the remainder of the first line after the bracket tags
        first_line = chunk.splitlines()[0]
        title = re.sub(r"\[(id|score):[^\]]*\]\s*", "", first_line).strip()
        body = "\n".join(chunk.splitlines()[1:]).strip()
        items.append(
            {
                "id": m.group(1) if m else None,
                "title": title or "(untitled)",
                "snippet": body[:280],
                "score": s.group(1) if s else None,
            }
        )
    return items


def _parse_web(text: str) -> List[dict]:
    items = []
    for chunk in text.split("\n\n---\n\n"):
        lines = [ln for ln in chunk.strip().splitlines() if ln.strip()]
        if not lines:
            continue
        title = lines[0]
        url = lines[1] if len(lines) > 1 and lines[1].startswith("http") else ""
        snippet = " ".join(lines[2:]) if len(lines) > 2 else ""
        items.append({"title": title, "url": url, "snippet": snippet[:280]})
    return items


def build_citation(tool_name: str, tool_input: Any, output: Any) -> dict:
    text = extract_text(output).strip()
    query = _query_of(tool_input)

    if tool_name == "search_notes":
        if text and text != "No notes found.":
            return {"tool": tool_name, "type": "note", "query": query,
                    "items": _parse_notes(text)}
        return {"tool": tool_name, "type": "note", "query": query, "items": []}

    if tool_name == "search_web":
        if text and text != "Web search unavailable.":
            return {"tool": tool_name, "type": "web", "query": query,
                    "items": _parse_web(text)}
        return {"tool": tool_name, "type": "web", "query": query, "items": []}

    # Any other tool (add/list/update/delete): record as a generic action.
    return {"tool": tool_name, "type": "generic", "query": query,
            "items": [{"text": text[:280]}] if text else []}


# Only these tools produce user-facing citations worth showing as "sources".
CITABLE = {"search_notes", "search_web"}
