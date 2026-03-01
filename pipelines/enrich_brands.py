"""
Phase 3: AI Brand Enrichment Pipeline (Ollama)
------------------------------------------------
Fetches all brands without embeddings from the API, generates
768-dim embeddings using Ollama's nomic-embed-text model, and
stores them back via PATCH /brands/{id}/embedding.

Prerequisites:
    1. Ollama running locally: https://ollama.com
    2. nomic-embed-text model pulled:
         ollama pull nomic-embed-text

Usage:
    python -m pipelines.enrich_brands
"""

import requests
import time

API_BASE_URL = "http://localhost:8000"
OLLAMA_URL = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"


def get_embedding(text: str) -> list[float] | None:
    """Call Ollama to get a 768-dim embedding for the given text."""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": EMBED_MODEL, "prompt": text},
            timeout=30,
        )
        if response.status_code == 200:
            return response.json()["embedding"]
        else:
            print(f"  ⚠️  Ollama error {response.status_code}: {response.text}")
            return None
    except requests.RequestException as e:
        print(f"  ❌ Ollama request failed: {e}")
        return None


def build_embed_text(brand: dict) -> str:
    """Combine brand fields into a rich text for embedding."""
    parts = []
    if brand.get("name"):
        parts.append(f"Brand: {brand['name']}")
    if brand.get("description"):
        parts.append(brand["description"])
    if brand.get("category"):
        parts.append(f"Categories: {', '.join(brand['category'])}")
    if brand.get("tags"):
        parts.append(f"Tags: {', '.join(brand['tags'])}")
    if brand.get("price_range"):
        parts.append(f"Price range: {brand['price_range']}")
    if brand.get("country"):
        parts.append(f"Country: {brand['country']}")
    return ". ".join(parts)


def update_brand_embedding(brand_id: int, embedding: list[float]) -> bool:
    """PATCH the brand's embedding via the API."""
    try:
        response = requests.patch(
            f"{API_BASE_URL}/brands/{brand_id}/embedding",
            json={"embedding": embedding},
            timeout=10,
        )
        if response.status_code == 200:
            return True
        else:
            print(f"  ⚠️  API error {response.status_code}: {response.text}")
            return False
    except requests.RequestException as e:
        print(f"  ❌ API request failed: {e}")
        return False


def check_ollama() -> bool:
    """Check if Ollama is running and the model is available."""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = [m["name"] for m in response.json().get("models", [])]
            if any(EMBED_MODEL in m for m in models):
                return True
            else:
                print(f"❌ Model '{EMBED_MODEL}' not found in Ollama.")
                print(f"   Run: ollama pull {EMBED_MODEL}")
                return False
        return False
    except requests.RequestException:
        print("❌ Ollama is not running. Start it with: ollama serve")
        return False


def run():
    print("🔍 Checking Ollama...")
    if not check_ollama():
        return

    print("✅ Ollama ready.\n")

    # Fetch all brands
    try:
        response = requests.get(f"{API_BASE_URL}/brands/", timeout=10)
        brands = response.json()
    except Exception as e:
        print(f"❌ Failed to fetch brands: {e}")
        return

    print(f"📦 Found {len(brands)} brands. Generating embeddings...\n")

    enriched = 0
    skipped = 0

    for brand in brands:
        brand_id = brand["id"]
        name = brand.get("name", f"Brand #{brand_id}")

        # Build text to embed
        embed_text = build_embed_text(brand)
        if not embed_text.strip():
            print(f"  ⏭️  Skipping '{name}' — no text to embed")
            skipped += 1
            continue

        print(f"  🧠 Embedding: {name}")
        embedding = get_embedding(embed_text)

        if embedding:
            success = update_brand_embedding(brand_id, embedding)
            if success:
                print(f"     ✅ Saved ({len(embedding)}-dim vector)")
                enriched += 1
            else:
                skipped += 1
        else:
            skipped += 1

        time.sleep(0.1)  # Small delay between Ollama calls

    print(f"\n✅ Done. {enriched} brands enriched, {skipped} skipped.")


if __name__ == "__main__":
    run()

# Made with Bob
