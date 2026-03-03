import csv
from pathlib import Path
import logging

def read_enriched_csv(filepath: str) -> list[dict]:
    """
    Read enriched brands CSV file.
    
    Args:
        filepath: Path to the enriched CSV file
        
    Returns:
        List of brand dictionaries
    """
    path = Path(filepath)
    
    if not path.exists():
        raise FileNotFoundError(f"{filepath} not found")
    
    brands = []
    
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            brands.append(dict(row))
    
    logging.info(f"Read {len(brands)} brands from {filepath}")
    return brands
