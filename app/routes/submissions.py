from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import BrandSubmissionCreate, BrandSubmissionOut
from app import crud

router = APIRouter(prefix="/submissions", tags=["Submissions"])

@router.post("/", response_model=BrandSubmissionOut)
async def submit_brand(submission: BrandSubmissionCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_submission(db, submission.dict())

@router.get("/", response_model=list[BrandSubmissionOut])
async def list_submissions(db: AsyncSession = Depends(get_db)):
    return await crud.get_submissions(db)

@router.post("/{submission_id}/approve")
async def approve_submission(submission_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.approve_submission(db, submission_id)
