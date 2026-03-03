import re
from typing import Dict, Optional

def parse_query(query: str) -> Dict[str, Optional[str]]:
    """
    Extract structured filters from natural language query.
    
    Examples:
        "sustainable swimwear under ₹3000" -> {price_range: "low", category: "swimwear"}
        "luxury brands from India" -> {country: "India", price_range: "luxury"}
    """
    query_lower = query.lower()
    filters = {}
    
    # Extract country
    countries = ["india", "indian", "mumbai", "delhi", "bangalore", "goa"]
    for country in countries:
        if country in query_lower:
            filters["country"] = "India"
            break
    
    # Extract price range
    price_keywords = {
        "luxury": ["luxury", "high-end", "premium brands", "expensive"],
        "premium": ["premium", "upscale"],
        "mid": ["mid-range", "moderate", "affordable"],
        "low": ["budget", "cheap", "under", "₹1000", "₹2000", "₹3000"]
    }
    
    for price_tier, keywords in price_keywords.items():
        if any(kw in query_lower for kw in keywords):
            filters["price_range"] = price_tier
            break
    
    # Extract category (basic keyword matching)
    categories = {
        "swimwear": ["swimwear", "swim", "bikini", "beachwear"],
        "saree": ["saree", "sari", "drape"],
        "dress": ["dress", "dresses", "gown"],
        "casual": ["casual", "everyday", "relaxed"],
        "formal": ["formal", "office", "work"],
        "ethnic": ["ethnic", "traditional", "indian wear"],
        "western": ["western", "contemporary"],
        "accessories": ["accessories", "jewelry", "bags"],
    }
    
    for category, keywords in categories.items():
        if any(kw in query_lower for kw in keywords):
            filters["category"] = category
            break
    
    return filters
