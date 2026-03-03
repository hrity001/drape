import json
import asyncio
import logging
import re
from pydantic import ValidationError

from .client import call_ollama
from .schema import EnrichedBrand, LLMBrandData
from .scraper import fetch_website_text
from .pricing import classify_price


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
You are a structured brand profiler.

Using the website content below, generate STRICT JSON only.

Brand: {name}

Website Content:
{website_text}

Return ONLY valid JSON:

{{
  "country": "",
  "category": "",
  "price_range": "",
  "description": "",
  "tags": "",
  "is_featured": false,
  "confidence_score": 0.0
}}

Rules:
- Description under 30 words
- Tags lowercase, comma-separated, no spaces
- No explanation
- price_range must be one of: low, mid, premium, luxury
- Do NOT use currency symbols
- confidence_score: 0.0-1.0 based on data quality (1.0 = very confident, 0.0 = uncertain)
- Set confidence_score lower if information is unclear or missing
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
