import csv
import logging
from pathlib import Path

def load_brands(filepath: str):
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"{filepath} not found")

    brands = []
    required_fields = {"name", "website", "instagram_handle"}

    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        
        # Validate headers
        if not required_fields.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"CSV missing required fields: {required_fields}")
        
        for idx, row in enumerate(reader, start=2):
            # Validate row data
            if not all(row.get(field, "").strip() for field in required_fields):
                logging.warning(f"Row {idx}: Missing required fields, skipping")
                continue
                
            brands.append({
                "name": row["name"].strip(),
                "website": row["website"].strip(),
                "instagram_handle": row["instagram_handle"].strip(),
            })

    logging.info(f"Loaded {len(brands)} brands from {filepath}")
    return brands
