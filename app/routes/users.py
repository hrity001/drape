from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.schemas import UserCreate, UserOut, FeedbackCreate, FeedbackOut, SearchResult, UserRegister, UserLogin, TokenOut, EmbeddingUpdate
from app.models import User
from app import crud

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserOut)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_user(db, user.dict())

@router.post("/feedback", response_model=FeedbackOut)
async def submit_feedback(feedback: FeedbackCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_feedback(db, feedback.dict())


@router.get("/{user_id}/recommendations", response_model=list[SearchResult])
async def get_recommendations(user_id: int, limit: int = 10, db: AsyncSession = Depends(get_db)):
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user or user.preference_vector is None:
        raise HTTPException(status_code=404, detail="No preference vector yet — swipe some brands first")
    results = await crud.semantic_search_brands(db, user.preference_vector, limit=limit)
    return results


from app.schemas import UserRegister, UserLogin, TokenOut
from app.auth import hash_password, verify_password, create_access_token

@router.post("/register", response_model=TokenOut)
async def register(body: UserRegister, db: AsyncSession = Depends(get_db)):
    existing = await crud.get_user_by_email(db, body.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await crud.create_user(db, {
        "email": body.email,
        "name": body.name,
        "hashed_password": hash_password(body.password),
    })
    token = create_access_token(user.id)
    return {"access_token": token, "user_id": user.id, "has_completed_quiz": False}

@router.post("/login", response_model=TokenOut)
async def login(body: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user_by_email(db, body.email)
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(user.id)
    return {"access_token": token, "user_id": user.id, "has_completed_quiz": user.has_completed_quiz}

@router.patch("/{user_id}/preference_vector", response_model=UserOut)
async def set_preference_vector(user_id: int, body: EmbeddingUpdate, db: AsyncSession = Depends(get_db)):
    user = await crud.update_user_preference_vector(db, user_id, body.embedding)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
