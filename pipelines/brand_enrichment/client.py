import httpx
from .config import OLLAMA_URL, CHAT_MODEL, TIMEOUT

async def call_ollama(prompt: str):

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": CHAT_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json" 
            },
        )

    response.raise_for_status()
    return response.json()["response"]