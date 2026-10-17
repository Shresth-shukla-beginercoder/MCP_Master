
import asyncio

from fastmcp import Client
from langchain.mcp import MCPAdapter
from pathlib import Path


async def main():
    client = Client(Path("src/servers/stdio_server.py"))

    async with MCPAdapter(client) as adapter:
        tools = await adapter.list_tools(cache_mode="use")

        print("Available LangChain tools:")
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")


if __name__ == "__main__":
    asyncio.run(main())
