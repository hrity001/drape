import json
import asyncio
import logging
import re
from pydantic import ValidationError

from .client import call_ollama
from .schema import EnrichedBrand, LLMBrandData
from .scraper import fetch_website_text



from .config import MAX_RETRIES


def calculate_review_needs(brand_data: dict) -> tuple[bool, str | None]:
    """
    Determine if brand needs manual review based on:
    1. Missing critical fields
    2. Low confidence score
    3. Failed enrichment
    """
    reasons = []
    
    # Check for missing critical fields
    critical_fields = ["country", "category", "price_range"]
    missing_fields = [f for f in critical_fields if not brand_data.get(f)]
    
    if missing_fields:
        reasons.append(f"Missing: {', '.join(missing_fields)}")
    
    # Check confidence score
    confidence = brand_data.get("confidence_score", 0.0)
    if confidence < 0.6:
        reasons.append(f"Low confidence: {confidence:.2f}")
    
    # Check enrichment status
    if brand_data.get("enrichment_status") in ["failed", "no_website_content"]:
        reasons.append(f"Status: {brand_data.get('enrichment_status')}")
    
    needs_review = len(reasons) > 0
    review_reason = "; ".join(reasons) if needs_review else None
    
    return needs_review, review_reason



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def build_prompt(name: str, website_text: str):
    return f"""
You are an expert fashion brand analyst. 


EXAMPLE 1:
Brand: Fabindia
Output: {{
  "country": "India",
  "category": "Fashion",
  "price_range": "mid",
  "description": "Contemporary Indian clothing with traditional crafts and handloom textiles for modern living",
  "tags": "handloom,ethnic,sustainable,cotton,artisanal,indian,contemporary",
  "is_featured": false,
  "confidence_score": 0.95
}}


EXAMPLE 2:
Brand: Anita Dongre
Output: {{
  "country": "India",
  "category": "Luxury",
  "price_range": "premium",
  "description": "Luxury Indian fashion designer known for sustainable bridal wear and contemporary ethnic clothing",
  "tags": "luxury,bridal,sustainable,designer,ethnic,handcrafted,premium",
  "is_featured": true,
  "confidence_score": 0.92
}}
Now analyze this brand:
Brand Name: {name}

Website Content:
{website_text[:3000]}

Extract the following information and return ONLY valid JSON:

{{
  "country": "Country where brand is based (e.g., India, USA, UK, France)",
  "category": "Primary category (Fashion, Accessories, Footwear, Jewelry, Beauty, Home & Living, Sportswear, Sustainable Fashion, or Luxury)",
  "price_range": "One of: low, mid, premium, luxury",
  "description": "Concise 20-30 word brand description highlighting unique value",
  "tags": "5-8 relevant lowercase tags, comma-separated (e.g., sustainable,handmade,cotton,minimalist)",
  "is_featured": false,
  "confidence_score": 0.0
}}

GUIDELINES:

Country:
- Look for "About Us", "Contact", "Shipping" sections
- Check for currency symbols (₹=India, $=USA, £=UK, €=Europe)
- Look for phone numbers with country codes
- If unclear, use "India" as default for Indian fashion brands

Category:
- Fashion: Clothing, apparel, ethnic wear, western wear
- Accessories: Bags, jewelry, scarves, belts
- Footwear: Shoes, sandals, heels
- Sustainable Fashion: Eco-friendly, organic, ethical brands

Price Range (based on product prices or brand positioning):
- low: Under ₹2000 or $30 (mass market, affordable)
- mid: ₹2000-8000 or $30-120 (contemporary, accessible premium)
- premium: ₹8000-25000 or $120-400 (designer, high-quality)
- luxury: Above ₹25000 or $400+ (haute couture, luxury designer)

Description:
- Focus on brand's unique selling proposition
- Mention style aesthetic (minimalist, bohemian, contemporary, traditional)
- Include target audience if clear (women, men, unisex)
- Highlight key materials or craftsmanship if mentioned

Tags:
- Include: style keywords, materials, sustainability aspects, occasion types
- Examples: handwoven, linen, sustainable, workwear, festive, minimalist, artisanal
- Use lowercase, no spaces between words in compound terms

Confidence Score:
- 0.9-1.0: All information clearly stated on website
- 0.7-0.8: Most information found, some inference needed
- 0.5-0.6: Limited information, significant inference
- 0.3-0.4: Very limited information, mostly guesswork
- 0.0-0.2: Almost no relevant information found

Return ONLY the JSON object, no explanations.
"""


def safe_extract_json(text: str):
    """
    Safely extract first JSON object from LLM response.
    Non-greedy match to avoid capturing multiple objects.
    """
    match = re.search(r"\{[\s\S]*?\}", text)
    if not match:
        raise ValueError("No JSON found in LLM response")

    return json.loads(match.group(0))


async def enrich_brand(brand: dict):
    from datetime import datetime
    
    website_text = await fetch_website_text(brand["website"])

    if not website_text:
        logging.warning(f"No website content for {brand['name']}")
        brand["enrichment_status"] = "no_website_content"
        brand["needs_review"] = True
        brand["review_reason"] = "No website content available"
        brand["last_updated"] = datetime.utcnow().isoformat()
        return brand
    
    for attempt in range(MAX_RETRIES):
        try:
            raw = await call_ollama(
                build_prompt(brand["name"], website_text)
            )

            data = safe_extract_json(raw)

            # Validate ONLY LLM fields
            validated_llm = LLMBrandData(**data)

            # Merge original + LLM data
            final_brand = EnrichedBrand(
                name=brand["name"],
                website=brand["website"],
                instagram_handle=brand["instagram_handle"],
                last_updated=datetime.utcnow().isoformat(),
                **validated_llm.model_dump()
            )
            
            # Calculate if needs review
            brand_dict = final_brand.model_dump()
            needs_review, review_reason = calculate_review_needs(brand_dict)
            brand_dict["needs_review"] = needs_review
            brand_dict["review_reason"] = review_reason

            if needs_review:
                logging.warning(f"⚠️  {brand['name']} needs review: {review_reason}")
            else:
                logging.info(f"✓ Enriched {brand['name']} (confidence: {validated_llm.confidence_score:.2f})")
            
            return brand_dict

        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            wait_time = 2 ** attempt
            logging.warning(
                f"[Retry {attempt+1}/{MAX_RETRIES}] "
                f"{brand['name']} failed: {e} - Waiting {wait_time}s"
            )
            await asyncio.sleep(wait_time)

    logging.error(f"✗ Failed to enrich {brand['name']} after {MAX_RETRIES} retries")
    brand["enrichment_status"] = "failed"
    brand["needs_review"] = True
    brand["review_reason"] = "Enrichment failed after retries"
    brand["last_updated"] = datetime.utcnow().isoformat()
    return brand
