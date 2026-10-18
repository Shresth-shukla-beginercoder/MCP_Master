
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastmcp import Client
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATIC_DIR = Path(__file__).resolve().parent / "static"

load_dotenv(PROJECT_ROOT / ".env")


@asynccontextmanager
async def lifespan(app: FastAPI):
    server_path = PROJECT_ROOT / "src" / "servers" / "stdio_server.py"
    client = Client(server_path)

    async with MCPAdapter(client) as adapter:
        tools = await adapter.list_tools()

        model = ChatGoogleGenerativeAI(
            model="gemini-3.8-flash"
        )

        app.state.agent = create_agent(
            model=model,
            tools=tools,
            system_prompt=(
                "You are a helpful AI assistant connected to MCP tools. "
                "Use fetch_data to read text files and process_data to "
                "analyze CSV files when appropriate. Explain results clearly. "
                "Use the conversation history to understand follow-up questions."
            ),
        )

        print("Gemini MCP chatbot backend is ready!")
        yield


app = FastAPI(
    title="MCP Master Chatbot",
    lifespan=lifespan,
)


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = Field(default_factory=list)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    try:
        messages = [
            {
                "role": item.role,
                "content": item.content,
            }
            for item in request.history
        ]

        messages.append({
            "role": "user",
            "content": message,
        })

        result = await app.state.agent.ainvoke({
            "messages": messages
        })

        last_message = result["messages"][-1]
        answer = getattr(last_message, "text", None)

        if not answer:
            content = last_message.content
            answer = (
                content
                if isinstance(content, str)
                else str(content)
            )

        return {"reply": answer}

    except Exception as error:
        print(f"Chat request failed: {error}")
        raise HTTPException(
            status_code=500,
            detail="The AI could not process your message. Check the backend terminal.",
        ) from error


@app.get("/")
async def home():
    return FileResponse(STATIC_DIR / "index.html")
