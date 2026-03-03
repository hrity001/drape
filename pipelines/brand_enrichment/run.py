import asyncio
import time
from .loader import load_brands
from .processor import process_brands
from .writer import write_csv

async def main():
    start_time = time.time()
    
    brands = load_brands("pipelines/brands.csv")
    enriched = await process_brands(brands)
    
    # Separate brands needing review
    needs_review = [b for b in enriched if b.get("needs_review", False)]
    complete = [b for b in enriched if not b.get("needs_review", False)]
    
    # Calculate stats
    successful = sum(1 for b in enriched if b.get("enrichment_status") != "failed")
    failed = len(enriched) - successful
    
    # Write main output
    write_csv(enriched, "pipelines/brands_enriched.csv")
    
    # Write review queue if needed
    if needs_review:
        write_csv(needs_review, "pipelines/brands_needs_review.csv")
    
    elapsed = time.time() - start_time
    print(f"\n{'='*50}")
    print(f"Pipeline complete in {elapsed:.2f}s")
    print(f"✓ Successful: {successful}/{len(brands)}")
    print(f"✗ Failed: {failed}/{len(brands)}")
    print(f"⚠️  Needs Review: {len(needs_review)}/{len(brands)}")
    if needs_review:
        print(f"\n📋 Review queue saved to: pipelines/brands_needs_review.csv")
        print("\nBrands needing review:")
        for b in needs_review:
            print(f"  - {b['name']}: {b.get('review_reason', 'Unknown')}")
    print(f"{'='*50}")

if __name__ == "__main__":
    asyncio.run(main())
