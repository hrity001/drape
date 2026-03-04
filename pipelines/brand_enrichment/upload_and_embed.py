import asyncio
import sys
import logging
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from brand_enrichment.csv_reader import read_enriched_csv
from brand_enrichment.db_uploader import upload_brands_to_db
from generate_embeddings import generate_embeddings_for_all_brands

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


async def upload_and_embed():
    """Upload brands to DB and generate embeddings"""
    script_dir = Path(__file__).parent
    input_csv = script_dir / "brands_ready_for_upload.csv"
    
    print("\n" + "="*70)
    print("📤 UPLOAD TO DATABASE & GENERATE EMBEDDINGS")
    print("="*70)
    
    # Check if file exists
    if not input_csv.exists():
        print(f"\n❌ File not found: {input_csv.name}")
        print("💡 Run enrich_and_review.py first!")
        return
    
    # Step 1: Upload to database
    print("\n📤 Step 1: Uploading brands to database...")
    print("-"*70)
    
    try:
        brands = read_enriched_csv(str(input_csv))
        print(f"📊 Found {len(brands)} brands to upload")
        
        stats = await upload_brands_to_db(brands, batch_size=10)
        
        print(f"\n✓ Created: {stats['created']}")
        print(f"↻ Updated: {stats['updated']}")
        print(f"✗ Errors: {stats['errors']}")
        
        if stats['errors'] > 0:
            print("\n⚠️  Some brands failed to upload. Check logs.")
            return
        
    except Exception as e:
        print(f"\n❌ Upload failed: {e}")
        return
    
    # Step 2: Generate embeddings
    print("\n🧠 Step 2: Generating embeddings...")
    print("-"*70)
    
    try:
        await generate_embeddings_for_all_brands()
        print("\n✓ Embeddings generated successfully")
    except Exception as e:
        print(f"\n❌ Embedding generation failed: {e}")
        print("⚠️  Make sure Ollama is running: ollama serve")
        return
    
    # Summary
    print("\n" + "="*70)
    print("🎉 COMPLETE!")
    print("="*70)
    print(f"✓ {stats['created'] + stats['updated']} brands in database")
    print(f"✓ Embeddings generated for semantic search")
    print("="*70)


if __name__ == "__main__":
    print("\n⚠️  Prerequisites:")
    print("  1. Ollama must be running: ollama serve")
    print("  2. Database must be accessible")
    print("  3. brands_ready_for_upload.csv must exist\n")
    
    response = input("Continue? (y/n): ").lower()
    if response == 'y':
        asyncio.run(upload_and_embed())
    else:
        print("Cancelled.")
