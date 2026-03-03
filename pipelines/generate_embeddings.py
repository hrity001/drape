import asyncio
import requests
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.models import Brand
from app.database import DATABASE_URL

OLLAMA_URL = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"


def get_embedding(text: str) -> list:
    """Get embedding from Ollama"""
    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": EMBED_MODEL, "prompt": text},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()["embedding"]
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return None


def create_brand_text(brand) -> str:
    """Create searchable text from brand data"""
    parts = [brand.name]
    
    if brand.description:
        parts.append(brand.description)
    
    if brand.category:
        parts.extend(brand.category)
    
    if brand.tags:
        parts.extend(brand.tags)
    
    if brand.country:
        parts.append(brand.country)
    
    if brand.price_range:
        parts.append(brand.price_range)
    
    return " ".join(parts)


async def generate_embeddings_for_all_brands():
    """Generate embeddings for all brands without embeddings"""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get all brands without embeddings
        result = await session.execute(
            select(Brand).where(Brand.embedding == None)
        )
        brands = result.scalars().all()
        
        if not brands:
            print("✓ All brands already have embeddings!")
            return
        
        print(f"\n📊 Found {len(brands)} brands without embeddings")
        print("🚀 Generating embeddings...\n")
        
        success_count = 0
        error_count = 0
        
        for idx, brand in enumerate(brands, 1):
            try:
                # Create searchable text
                brand_text = create_brand_text(brand)
                
                # Get embedding
                embedding = get_embedding(brand_text)
                
                if embedding:
                    brand.embedding = embedding
                    success_count += 1
                    print(f"[{idx}/{len(brands)}] ✓ {brand.name}")
                else:
                    error_count += 1
                    print(f"[{idx}/{len(brands)}] ✗ {brand.name} - Failed to get embedding")
                
                # Commit in batches of 5
                if idx % 5 == 0:
                    await session.commit()
                    print(f"  → Committed batch\n")
                    
            except Exception as e:
                error_count += 1
                print(f"[{idx}/{len(brands)}] ✗ {brand.name} - Error: {e}")
        
        # Final commit
        await session.commit()
        
        print("\n" + "="*60)
        print("Embedding Generation Complete!")
        print("="*60)
        print(f"✓ Success: {success_count}")
        print(f"✗ Errors: {error_count}")
        print(f"📊 Total: {len(brands)}")
        print("="*60 + "\n")
    
    await engine.dispose()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Brand Embedding Generator")
    print("="*60)
    print("\n⚠️  Make sure Ollama is running: ollama serve\n")
    
    response = input("Continue? (y/n): ").lower()
    if response == 'y':
        asyncio.run(generate_embeddings_for_all_brands())
    else:
        print("Cancelled.")
