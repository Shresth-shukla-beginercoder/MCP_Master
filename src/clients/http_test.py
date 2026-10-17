
import asyncio

from fastmcp import Client


async def main():
    # Connect to the running HTTP MCP server.
    async with Client("http://127.0.0.1:8000/mcp") as client:

        # Discover available tools.
        tools = await client.list_tools()
        print("Available HTTP MCP tools:")
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")

        # Test 1: Read a real text file.
        print("\n--- Testing fetch_data ---")
        result = await client.call_tool(
            "fetch_data",
            {"path": "sample.txt"},
        )
        print(result)

        # Test 2: Analyze a real CSV file.
        print("\n--- Testing process_data ---")
        result = await client.call_tool(
            "process_data",
            {"path": "sales.csv"},
        )
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
