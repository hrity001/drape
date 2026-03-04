import asyncio
from tqdm.asyncio import tqdm
from .config import BATCH_SIZE
from .enricher import enrich_brand

SEM = asyncio.Semaphore(BATCH_SIZE)  # limit parallel LLM calls


async def safe_enrich(brand):
    async with SEM:
        return await enrich_brand(brand)


async def process_brands(brands, max_retries=3):
    """Process brands with retry logic"""
    tasks = []
    for brand in brands:
        tasks.append(enrich_with_retry(brand, max_retries))
    return await asyncio.gather(*tasks)

async def enrich_with_retry(brand, max_retries=3):
    """Enrich a single brand with retry logic"""
    for attempt in range(max_retries):
        try:
            result = await enrich_brand(brand)
            if result.get("enrichment_status") != "failed":
                return result
            
            # If failed, retry
            if attempt < max_retries - 1:
                logging.warning(f"Retry {attempt + 1}/{max_retries} for {brand['name']}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        except Exception as e:
            if attempt < max_retries - 1:
                logging.error(f"Error enriching {brand['name']}, retrying: {e}")
                await asyncio.sleep(2 ** attempt)
            else:
                logging.error(f"Failed after {max_retries} attempts: {brand['name']}")
    
    return result  # Return last attempt result

