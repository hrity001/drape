import sys
import asyncio
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import logging

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.models import Brand
from app.database import DATABASE_URL

logging.basicConfig(level=logging.INFO)

async def get_or_create_brand(session: AsyncSession, brand_data: dict):
    """
    Get existing brand or create new one.
    Updates existing brand if found by website or instagram_handle.
    """
    # Try to find existing brand by website or instagram
    stmt = select(Brand).where(
        (Brand.website == brand_data.get("website")) |
        (Brand.instagram_handle == brand_data.get("instagram_handle"))
    )
    result = await session.execute(stmt)
    existing_brand = result.scalar_one_or_none()
    
    if existing_brand:
        # Update existing brand
        for key, value in brand_data.items():
            if hasattr(existing_brand, key) and value is not None:
                setattr(existing_brand, key, value)
        logging.info(f"Updated existing brand: {brand_data['name']}")
        return existing_brand, False
    else:
        # Create new brand
        new_brand = Brand(**brand_data)
        session.add(new_brand)
        logging.info(f"Created new brand: {brand_data['name']}")
        return new_brand, True


async def upload_brands_to_db(brands_data: list[dict], batch_size: int = 10):
    """
    Upload enriched brands to database.
    
    Args:
        brands_data: List of brand dictionaries from CSV
        batch_size: Number of brands to commit at once
    """
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    created_count = 0
    updated_count = 0
    error_count = 0
    
    async with async_session() as session:
        for idx, brand_dict in enumerate(brands_data, 1):
            try:
                # Prepare data for database
                db_brand_data = prepare_brand_for_db(brand_dict)
                
                # Get or create brand
                brand, is_new = await get_or_create_brand(session, db_brand_data)
                
                if is_new:
                    created_count += 1
                else:
                    updated_count += 1
                
                # Commit in batches
                if idx % batch_size == 0:
                    await session.commit()
                    logging.info(f"Committed batch: {idx}/{len(brands_data)}")
                    
            except Exception as e:
                error_count += 1
                logging.error(f"Error processing {brand_dict.get('name', 'Unknown')}: {e}")
                await session.rollback()
        
        # Final commit
        await session.commit()
    
    await engine.dispose()
    
    return {
        "created": created_count,
        "updated": updated_count,
        "errors": error_count,
        "total": len(brands_data)
    }


def prepare_brand_for_db(brand_dict: dict) -> dict:
    """
    Transform CSV brand data to match database schema.
    
    Database expects:
    - category: ARRAY(String) - but CSV has single string
    - tags: ARRAY(String) - but CSV has comma-separated string
    """
    db_data = {
        "name": brand_dict.get("name"),
        "website": brand_dict.get("website"),
        "instagram_handle": brand_dict.get("instagram_handle"),
        "country": brand_dict.get("country"),
        "price_range": brand_dict.get("price_range"),
        "description": brand_dict.get("description"),
        "is_featured": brand_dict.get("is_featured", "False").lower() == "true",
    }
    
    # Convert category string to array
    category = brand_dict.get("category", "")
    if category:
        db_data["category"] = [category.strip()]
    else:
        db_data["category"] = []
    
    # Convert tags string to array
    tags = brand_dict.get("tags", "")
    if tags:
        db_data["tags"] = [t.strip() for t in tags.split(",") if t.strip()]
    else:
        db_data["tags"] = []
    
    # Remove None values
    return {k: v for k, v in db_data.items() if v is not None}
