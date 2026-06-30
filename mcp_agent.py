"""
LangGraph Agent
Consumes tools exposed by MCP server.
"""

import asyncio
import os
import sys

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from langchain_mcp_adapters.client import (
    MultiServerMCPClient
)

from langgraph.prebuilt import (
    create_react_agent
)

load_dotenv()

# OpenRouter is OpenAI-API-compatible, so we use ChatOpenAI pointed at its
# base URL. Pick a *free* model that supports tool/function calling (required
# by the ReAct agent). Override with the OPENROUTER_MODEL env var if desired.
OPENROUTER_MODEL = os.environ.get(
    "OPENROUTER_MODEL",
    "meta-llama/llama-3.3-70b-instruct:free",
)


async def run_agent(
    query: str,
):

    print(f"\nQuery: {query}\n")

    # As of langchain-mcp-adapters 0.1.0+, MultiServerMCPClient is no longer
    # an async context manager. Instantiate it and call get_tools() directly.
    client = MultiServerMCPClient(
        {
            "knowledge": {
                "url":
                "http://localhost:8001/mcp",

                "transport":
                "http",
            }
        }
    )

    tools = (
        await client.get_tools()
    )

    print(
        "Available tools:",
        [t.name for t in tools]
    )

    model = ChatOpenAI(
        model=OPENROUTER_MODEL,
        temperature=0,
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ.get("OPENROUTER_API_KEY", ""),
    )

    agent = (
        create_react_agent(
            model,
            tools,
        )
    )

    result = (
        await agent.ainvoke(
            {
                "messages": [
                    {
                        "role":
                        "user",

                        "content":
                        query,
                    }
                ]
            }
        )
    )

    print(
        "\nResponse:\n"
    )

    print(
        result[
            "messages"
        ][-1].content
    )


if __name__ == "__main__":

    query = (
        " ".join(
            sys.argv[1:]
        )
        if len(sys.argv) > 1
        else "List my notes"
    )

    asyncio.run(
        run_agent(query)
    )
