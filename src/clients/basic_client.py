import asyncio
from fastmcp import Client
from pathlib import Path


async def main():
    async with Client(Path("src/servers/stdio_server.py")) as client:
        tools = await client.list_tools()
        print("Available tools:", [tool.name for tool in tools])

        result = await client.call_tool(
            "fetch_data",
            {"path": "/data/example"}
        )
        print("Tool result:", result)


if __name__ == "__main__":
    asyncio.run(main())