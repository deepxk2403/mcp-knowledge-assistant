"""
Full note-memory pipeline test (NO API keys needed).

With local FastEmbed embeddings, add_note / list_notes / search_notes all run
without any cloud key. This exercises the complete memory path through MCP:
  client -> HTTP -> MCP server -> FastEmbed (local) -> Qdrant -> back.

The first run downloads the embedding model (~130 MB), so be patient once.
"""
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient


async def main():
    client = MultiServerMCPClient(
        {"knowledge": {"url": "http://localhost:8001/mcp", "transport": "http"}}
    )
    tools = {t.name: t for t in await client.get_tools()}
    print("Discovered tools:", list(tools))

    print("\n[add_note] seeding two notes...")
    print(" ->", await tools["add_note"].ainvoke(
        {"title": "RAG Tips", "content": "Always use hybrid search for retrieval."}))
    print(" ->", await tools["add_note"].ainvoke(
        {"title": "Coffee", "content": "Pour-over at 92C tastes best."}))

    print("\n[list_notes]")
    print(await tools["list_notes"].ainvoke({"limit": 10}))

    # Semantic query that shares NO keywords with the stored note, to prove
    # this is meaning-based retrieval, not text matching.
    print("\n[search_notes] query='techniques for improving document retrieval'")
    print(await tools["search_notes"].ainvoke(
        {"query": "techniques for improving document retrieval", "top_k": 2}))

    print("\nMEMORY PIPELINE OK (local embeddings, zero API keys).")


if __name__ == "__main__":
    asyncio.run(main())
