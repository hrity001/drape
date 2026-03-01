import httpx
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import ChatRequest, ChatResponse
from app import crud

router = APIRouter(prefix="/chat", tags=["Chat"])

OLLAMA_URL = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"
CHAT_MODEL  = "llama3.2"


async def embed(text: str) -> list[float]:
    """Embed the user's message using nomic-embed-text."""
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": EMBED_MODEL, "prompt": text},
        )
        return r.json()["embedding"]


async def call_llm(system: str, history: list, user_message: str) -> str:
    """Call llama3.2 with system prompt + conversation history."""
    messages = [{"role": "system", "content": system}]
    for turn in history:
        messages.append({"role": turn.role, "content": turn.content})
    messages.append({"role": "user", "content": user_message})

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(
            f"{OLLAMA_URL}/api/chat",
            json={"model": CHAT_MODEL, "messages": messages, "stream": False},
        )
        return r.json()["message"]["content"]


def build_system_prompt(brands: list[dict]) -> str:
    """Build the RAG system prompt — inject real brand data."""
    brand_lines = []
    for b in brands:
        line = f"- {b['name']}"
        if b.get("price_range"):
            line += f" | Price: {b['price_range']}"
        if b.get("country"):
            line += f" | Country: {b['country']}"
        if b.get("category"):
            line += f" | Category: {', '.join(b['category'])}"
        if b.get("description"):
            line += f" | About: {b['description'][:120]}"
        if b.get("website"):
            line += f" | Website: {b['website']}"
        brand_lines.append(line)

    brand_context = "\n".join(brand_lines)

    return f"""You are Drape, an AI fashion stylist specialising in indie and homegrown Indian fashion brands.

You ONLY recommend brands from the list below. Never invent or hallucinate brand names.
If none of the brands match the user's request, say so honestly and suggest they try a different search.

Available brands:
{brand_context}

Guidelines:
- Be warm, specific, and helpful — like a knowledgeable friend, not a search engine
- Always explain WHY a brand fits the user's request
- Mention price range and website when relevant
- Keep responses concise (3–5 sentences max per brand recommendation)
- If the user asks for an outfit, suggest different brands for different pieces
"""


@router.post("/", response_model=ChatResponse)
async def chat(body: ChatRequest, db: AsyncSession = Depends(get_db)):
    # Step 1: Embed the user's message (non-blocking)
    query_vec = await embed(body.message)

    # Step 2: Retrieve top 5 most relevant brands from pgvector
    brands = await crud.semantic_search_brands(db, query_vec, limit=5)

    # Step 3: Build RAG system prompt with real brand data
    system_prompt = build_system_prompt(brands)

    # Step 4: Call llama3.2 with history + user message (non-blocking)
    reply = await call_llm(system_prompt, body.history or [], body.message)

    return ChatResponse(reply=reply, brands=brands)
