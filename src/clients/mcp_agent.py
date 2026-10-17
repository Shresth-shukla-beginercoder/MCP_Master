
import asyncio
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import Client
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


async def main():
    server_path = Path("src/servers/stdio_server.py")
    client = Client(server_path)

    model = ChatGoogleGenerativeAI(
        model="gemini-3.8-flash"
    )

    async with MCPAdapter(client) as adapter:
        tools = await adapter.list_tools()

        print("Available MCP tools:", [tool.name for tool in tools])

        agent = create_agent(
            model=model,
            tools=tools,
            system_prompt=(
                "You are an assistant that can use MCP tools. "
                "When the user asks you to fetch or process data, "
                "call the appropriate tool. Explain the result clearly."
            ),
        )

        print("\nMCP Agent is ready!")
        print("Type 'exit' to quit.\n")

        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in {"exit", "quit"}:
                print("Agent: Goodbye!")
                break

            if not user_input:
                continue

            try:
                result = await agent.ainvoke(
                    {
                        "messages": [
                            {
                                "role": "user",
                                "content": user_input,
                            }
                        ]
                    }
                )

                print("\nAgent:")
                print(result["messages"][-1].text)
                print()

            except Exception as error:
                print(f"\nError: {error}\n")


if __name__ == "__main__":
    asyncio.run(main())
