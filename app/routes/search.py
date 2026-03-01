from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import SearchQuery, SearchResult
from app import crud
import requests
from pydantic import BaseModel


router = APIRouter(prefix="/search", tags=["Search"])

OLLAMA_URL = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"

def get_query_embedding(text: str) -> list:
    r = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=30,
    )
    return r.json()["embedding"]

@router.post("/brands", response_model=list[SearchResult])
async def search_brands(body: SearchQuery, db: AsyncSession = Depends(get_db)):
    # Step A: Parse filters from query using LLM
    from pipelines.query_parser import parse_query
    filters = parse_query(body.query)

    # Step B: Manual overrides take priority
    country    = body.country    or filters.get("country")
    price_range = body.price_range or filters.get("price_range")
    category   = body.category   or filters.get("category")

    # Step C: Embed the query
    query_vector = get_query_embedding(body.query)

    # Step D: pgvector search
    results = await crud.semantic_search_brands(
        db, query_vector, country, price_range, category, body.limit
    )
    return results


class EmbedRequest(BaseModel):
    text: str

@router.post("/embed")
async def embed_text(body: EmbedRequest):
    """Embed a text string using Ollama nomic-embed-text. Used by the style quiz."""
    embedding = get_query_embedding(body.text)
    return {"embedding": embedding}
