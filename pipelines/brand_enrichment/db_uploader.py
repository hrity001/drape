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

async def upload_brands_to_db(brands, batch_size=10):
    """Upload brands with duplicate detection"""
    stats = {"created": 0, "updated": 0, "errors": 0, "skipped": 0, "total": len(brands)}
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        for i in range(0, len(brands), batch_size):
            batch = brands[i:i + batch_size]
            
            for brand_data in batch:
                try:
                    # Filter out fields that don't exist in Brand model
                    valid_fields = {
                        'name', 'website', 'instagram_handle', 'country', 
                        'category', 'price_range', 'description', 'tags', 
                        'is_featured'
                    }
                    
                    # Clean the data - only keep valid fields
                    clean_data = {
                        k: v for k, v in brand_data.items() 
                        if k in valid_fields and v and v != ''
                    }
                    
                    # Convert string booleans to actual booleans
                    if 'is_featured' in clean_data:
                        clean_data['is_featured'] = clean_data['is_featured'].lower() in ['true', '1', 'yes']
                    
                    # Convert comma-separated strings to arrays for category and tags
                    if 'category' in clean_data and isinstance(clean_data['category'], str):
                        clean_data['category'] = [clean_data['category']]
                    
                    if 'tags' in clean_data and isinstance(clean_data['tags'], str):
                        clean_data['tags'] = [t.strip() for t in clean_data['tags'].split(',')]
                    
                    # Check for duplicate by website
                    result = await session.execute(
                        select(Brand).where(Brand.website == clean_data["website"])
                    )
                    existing_brand = result.scalar_one_or_none()
                    
                    if existing_brand:
                        # Update existing brand
                        for key, value in clean_data.items():
                            if hasattr(existing_brand, key) and value:
                                setattr(existing_brand, key, value)
                        stats["updated"] += 1
                        logging.info(f"Updated: {clean_data['name']}")
                    else:
                        # Create new brand
                        brand = Brand(**clean_data)
                        session.add(brand)
                        stats["created"] += 1
                        logging.info(f"Created: {clean_data['name']}")
                    
                except Exception as e:
                    stats["errors"] += 1
                    logging.error(f"Error with {brand_data.get('name', 'Unknown')}: {e}")
            
            await session.commit()

    await engine.dispose()
    return stats





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
