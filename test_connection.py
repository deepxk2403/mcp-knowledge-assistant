"""
Connectivity smoke test (no API keys needed).

Verifies:
1. The agent process can reach the MCP server over HTTP.
2. Tool discovery works (MCP -> LangChain tool conversion).
3. A real tool call (list_notes) executes end-to-end:
   client -> HTTP -> MCP server -> Qdrant -> back.
   list_notes only touches Qdrant, so it needs no OpenAI/Anthropic keys.
"""
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient


async def main():
    client = MultiServerMCPClient(
        {"knowledge": {"url": "http://localhost:8001/mcp", "transport": "http"}}
    )
    tools = await client.get_tools()

    print("[1] Connected to MCP server.")
    print("[2] Discovered tools:")
    for t in tools:
        first_line = (
            t.description.strip().splitlines()[0]
            if t.description else ""
        )
        print(f"      - {t.name}: {first_line}")

    list_tool = next(t for t in tools if t.name == "list_notes")
    result = await list_tool.ainvoke({"limit": 10})
    print("[3] Live tool call -> list_notes(limit=10) returned:")
    print(f"      {result!r}")

    print("\nPIPELINE OK: agent -> MCP client -> HTTP -> server -> Qdrant.")


if __name__ == "__main__":
    asyncio.run(main())
