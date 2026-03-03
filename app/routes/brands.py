from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models import Brand
from app.schemas import BrandOut, BrandCreate

router = APIRouter(prefix="/brands", tags=["brands"])


@router.get("/", response_model=List[BrandOut])
async def get_brands(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all brands"""
    result = await db.execute(
        select(Brand).offset(skip).limit(limit)
    )
    brands = result.scalars().all()
    return brands


@router.get("/{brand_id}", response_model=BrandOut)
async def get_brand(brand_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific brand by ID"""
    result = await db.execute(
        select(Brand).where(Brand.id == brand_id)
    )
    brand = result.scalar_one_or_none()
    
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    return brand


@router.post("/", response_model=BrandOut)
async def create_brand(
    brand: BrandCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new brand"""
    db_brand = Brand(**brand.model_dump())
    db.add(db_brand)
    await db.commit()
    await db.refresh(db_brand)
    return db_brand


@router.get("/featured/", response_model=List[BrandOut])
async def get_featured_brands(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get featured brands"""
    result = await db.execute(
        select(Brand).where(Brand.is_featured == True).limit(limit)
    )
    brands = result.scalars().all()
    return brands
