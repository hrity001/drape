import csv
import logging
from pathlib import Path

FIELDS = [
    "name",
    "website",
    "instagram_handle",
    "country",
    "category",
    "price_range",
    "description",
    "tags",
    "is_featured",
    "enrichment_status",
    "confidence_score",
    "needs_review",
    "review_reason",
    "last_updated",
]

def write_csv(data, output_file):
    try:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with output_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(data)
        
        logging.info(f"Successfully wrote {len(data)} brands to {output_file}")
    except Exception as e:
        logging.error(f"Failed to write CSV: {e}")
        raise
