
import asyncio
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


async def main():
    model = ChatGoogleGenerativeAI(
        model="gemini-3.8-flash",
        temperature=0
    )

    response = await model.ainvoke(
        "Explain what an MCP server does in 2 simple sentences."
    )

    print("Gemini response:")
    print(response.text)


if __name__ == "__main__":
    asyncio.run(main())
