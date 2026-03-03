import asyncio
import logging
from csv_reader import read_enriched_csv
from db_uploader import upload_brands_to_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

async def main():
    print("\n" + "="*60)
    print("Brand Database Upload")
    print("="*60 + "\n")
    
    # Read CSV
    csv_path = "brands_enriched.csv"
    print(f"📖 Reading brands from: {csv_path}")
    brands = read_enriched_csv(csv_path)
    
    # Filter out brands that need review (optional)
    print(f"\n📊 Total brands: {len(brands)}")
    
    needs_review = [b for b in brands if b.get("needs_review", "").lower() == "true"]
    ready_to_upload = [b for b in brands if b.get("needs_review", "").lower() != "true"]
    
    if needs_review:
        print(f"⚠️  Brands needing review: {len(needs_review)}")
        print(f"✓ Brands ready to upload: {len(ready_to_upload)}")
        
        response = input("\nUpload only reviewed brands? (y/n): ").lower()
        if response == 'y':
            brands_to_upload = ready_to_upload
        else:
            brands_to_upload = brands
    else:
        brands_to_upload = brands
    
    if not brands_to_upload:
        print("\n❌ No brands to upload!")
        return
    
    # Upload to database
    print(f"\n🚀 Uploading {len(brands_to_upload)} brands to database...")
    
    stats = await upload_brands_to_db(brands_to_upload, batch_size=10)
    
    # Print results
    print("\n" + "="*60)
    print("Upload Complete!")
    print("="*60)
    print(f"✓ Created: {stats['created']}")
    print(f"↻ Updated: {stats['updated']}")
    print(f"✗ Errors: {stats['errors']}")
    print(f"📊 Total: {stats['total']}")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
