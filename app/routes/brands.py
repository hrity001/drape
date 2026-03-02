from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import BrandCreate, BrandOut, EmbeddingUpdate
from app import crud
from app.schemas import SearchResult 

router = APIRouter(prefix="/brands", tags=["Brands"])

@router.post("/", response_model=BrandOut)
async def create_brand(brand: BrandCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_brand(db, brand.dict())

@router.get("/", response_model=list[BrandOut])
async def list_brands(db: AsyncSession = Depends(get_db)):
    return await crud.get_brands(db)

@router.get("/{brand_id}", response_model=BrandOut)
async def get_brand(brand_id: int, db: AsyncSession = Depends(get_db)):
    brand = await crud.get_brand(db, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand

#getting similar brands routes
@router.get("/{brand_id}/similar", response_model=list[SearchResult])
async def get_similar_brands(brand_id: int, limit: int = 5, db: AsyncSession = Depends(get_db)):
    """Get brands with similar style/aesthetic to this brand."""
    return await crud.get_similar_brands(db, brand_id, limit)


@router.patch("/{brand_id}/embedding", response_model=BrandOut)
async def update_embedding(brand_id: int, body: EmbeddingUpdate, db: AsyncSession = Depends(get_db)):
    brand = await crud.update_brand_embedding(db, brand_id, body.embedding)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand
