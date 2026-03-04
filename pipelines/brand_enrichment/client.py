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
                "format": "json",
                "temperature": 0.3,  # Lower = more consistent (0.0-1.0)
                "top_p": 0.9,        # Nucleus sampling
                "top_k": 40          # Limit vocabulary
            },
        )
    response.raise_for_status()
    return response.json()["response"]
