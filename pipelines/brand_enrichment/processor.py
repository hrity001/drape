import asyncio
from tqdm.asyncio import tqdm
from .config import BATCH_SIZE
from .enricher import enrich_brand

SEM = asyncio.Semaphore(BATCH_SIZE)  # limit parallel LLM calls


async def safe_enrich(brand):
    async with SEM:
        return await enrich_brand(brand)


async def process_brands(brands):
    tasks = [safe_enrich(b) for b in brands]
    return await tqdm.gather(*tasks, desc="Enriching brands")
