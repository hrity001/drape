import csv
from pathlib import Path

def review_brands():
    """Interactive CLI for manual brand review"""
    review_file = Path("pipelines/brands_needs_review.csv")
    
    if not review_file.exists():
        print("No brands need review!")
        return
    
    with review_file.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        brands = list(reader)
    
    print(f"\n{'='*60}")
    print(f"Manual Review Queue: {len(brands)} brands")
    print(f"{'='*60}\n")
    
    for idx, brand in enumerate(brands, 1):
        print(f"\n[{idx}/{len(brands)}] {brand['name']}")
        print(f"Website: {brand['website']}")
        print(f"Reason: {brand.get('review_reason', 'N/A')}")
        print(f"Current Data:")
        print(f"  - Country: {brand.get('country', 'MISSING')}")
        print(f"  - Category: {brand.get('category', 'MISSING')}")
        print(f"  - Price Range: {brand.get('price_range', 'MISSING')}")
        print(f"  - Confidence: {brand.get('confidence_score', '0.0')}")
        
        print("\nOptions:")
        print("  [s] Skip")
        print("  [e] Edit")
        print("  [q] Quit")
        
        choice = input("\nChoice: ").lower()
        
        if choice == 'q':
            break
        elif choice == 'e':
            # Add interactive editing here
            print("Edit functionality - implement as needed")
        
    print("\nReview session complete!")

if __name__ == "__main__":
    review_brands()
