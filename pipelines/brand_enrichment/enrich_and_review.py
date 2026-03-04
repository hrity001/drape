import asyncio
import csv
import logging
from pathlib import Path
from datetime import datetime

# Import existing modules
from brand_enrichment.loader import load_brands
from brand_enrichment.processor import process_brands
from brand_enrichment.writer import write_csv

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

VALID_PRICE_RANGES = ["low", "mid", "premium", "luxury"]
VALID_CATEGORIES = ["Fashion", "Accessories", "Footwear", "Jewelry", "Beauty", 
                    "Home & Living", "Sportswear", "Sustainable Fashion", "Luxury"]


def display_brand(brand, idx, total):
    """Display brand for review"""
    print(f"\n{'='*70}")
    print(f"[{idx}/{total}] {brand['name']}")
    print(f"{'='*70}")
    print(f"Website: {brand['website']}")
    print(f"Instagram: {brand.get('instagram_handle', 'N/A')}")
    print(f"\nEnriched Data:")
    print(f"  Country: {brand.get('country', 'MISSING')}")
    print(f"  Category: {brand.get('category', 'MISSING')}")
    print(f"  Price Range: {brand.get('price_range', 'MISSING')}")
    print(f"  Description: {brand.get('description', 'MISSING')[:80]}...")
    print(f"  Tags: {brand.get('tags', 'MISSING')}")
    print(f"  Confidence: {brand.get('confidence_score', '0.0')}")


def edit_brand(brand):
    """Interactive editing"""
    print(f"\n{'─'*70}")
    print("EDIT MODE - Press Enter to keep current value")
    print(f"{'─'*70}")
    
    edited = brand.copy()
    
    # Edit fields
    new_val = input(f"Country [{brand.get('country', '')}]: ").strip()
    if new_val: edited['country'] = new_val
    
    print(f"Categories: {', '.join(VALID_CATEGORIES)}")
    new_val = input(f"Category [{brand.get('category', '')}]: ").strip()
    if new_val: edited['category'] = new_val
    
    print(f"Price ranges: {', '.join(VALID_PRICE_RANGES)}")
    while True:
        new_val = input(f"Price Range [{brand.get('price_range', '')}]: ").strip().lower()
        if not new_val: break
        if new_val in VALID_PRICE_RANGES:
            edited['price_range'] = new_val
            break
        print(f"❌ Invalid! Must be: {', '.join(VALID_PRICE_RANGES)}")
    
    new_val = input(f"Description: ").strip()
    if new_val: edited['description'] = new_val
    
    new_val = input(f"Tags (comma-separated) [{brand.get('tags', '')}]: ").strip()
    if new_val: edited['tags'] = new_val
    
    new_val = input(f"Featured? (y/n) [{brand.get('is_featured', 'false')}]: ").strip().lower()
    if new_val in ['y', 'yes']: edited['is_featured'] = 'true'
    elif new_val in ['n', 'no']: edited['is_featured'] = 'false'
    
    edited['last_updated'] = datetime.utcnow().isoformat()
    edited['enrichment_status'] = 'reviewed'
    edited['needs_review'] = 'false'
    
    return edited


async def enrich_and_review():
    """Main enrichment and review workflow"""
    script_dir = Path(__file__).parent
    brands_csv = script_dir / "brands.csv"
    output_csv = script_dir / "brands_ready_for_upload.csv"
    
    print("\n" + "="*70)
    print("🤖 BRAND ENRICHMENT & REVIEW")
    print("="*70)
    
    # Step 1: Load and enrich
    print("\n📝 Step 1: Loading and enriching brands...")
    brands = load_brands(str(brands_csv))
    enriched = await process_brands(brands)
    
    successful = [b for b in enriched if b.get("enrichment_status") != "failed"]
    failed = [b for b in enriched if b.get("enrichment_status") == "failed"]
    
    print(f"✓ Enriched: {len(successful)}/{len(brands)}")
    print(f"✗ Failed: {len(failed)}/{len(brands)}")
    
    if not successful:
        print("\n❌ No brands to review!")
        return
    
    # Step 2: Interactive review
    print(f"\n📋 Step 2: Reviewing {len(successful)} brands...")
    print("="*70)
    
    approved = []
    rejected = []
    
    for idx, brand in enumerate(successful, 1):
        display_brand(brand, idx, len(successful))
        
        print(f"\n{'─'*70}")
        print("Options: [a]pprove | [e]dit | [r]eject | [s]kip | [q]uit")
        print(f"{'─'*70}")
        
        while True:
            choice = input("\nChoice: ").lower().strip()
            
            if choice == 'q':
                print("\n⏸️  Quitting...")
                break
            
            elif choice == 'a':
                brand['enrichment_status'] = 'approved'
                brand['needs_review'] = 'false'
                brand['last_updated'] = datetime.utcnow().isoformat()
                approved.append(brand)
                print("✓ Approved")
                break
            
            elif choice == 'e':
                edited = edit_brand(brand)
                confirm = input("\nApprove changes? (y/n): ").lower()
                if confirm == 'y':
                    approved.append(edited)
                    print("✓ Edited and approved")
                    break
            
            elif choice == 'r':
                rejected.append(brand)
                print("✗ Rejected")
                break
            
            elif choice == 's':
                print("⏭️  Skipped")
                break
            
            else:
                print("❌ Invalid choice")
        
        if choice == 'q':
            break
    
    # Step 3: Save approved brands
    if approved:
        write_csv(approved, str(output_csv))
        print(f"\n✓ Saved {len(approved)} approved brands to: {output_csv.name}")
    
    # Summary
    print("\n" + "="*70)
    print("REVIEW SUMMARY")
    print("="*70)
    print(f"✓ Approved: {len(approved)}")
    print(f"✗ Rejected: {len(rejected)}")
    print(f"⏭️  Skipped: {len(successful) - len(approved) - len(rejected)}")
    print("="*70)
    
    if approved:
        print(f"\n💡 Next step: Run upload_and_embed.py to upload to database")


if __name__ == "__main__":
    print("\n⚠️  Make sure Ollama is running: ollama serve\n")
    response = input("Start enrichment and review? (y/n): ").lower()
    if response == 'y':
        asyncio.run(enrich_and_review())
    else:
        print("Cancelled.")
