from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import BrandLeadCreate, BrandLeadOut, BrandOut
from app import crud

router = APIRouter(prefix="/leads", tags=["Leads"])

@router.post("/", response_model=BrandLeadOut)
async def create_lead(lead: BrandLeadCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_brand_lead(db, lead.dict())

@router.get("/", response_model=list[BrandLeadOut])
async def list_leads(db: AsyncSession = Depends(get_db)):
    return await crud.get_brand_leads(db)

@router.post("/{lead_id}/promote", response_model=BrandOut)
async def promote_lead(lead_id: int, db: AsyncSession = Depends(get_db)):
    brand = await crud.promote_lead_to_brand(db, lead_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Lead not found")
    return brand

# Made with Bob
