from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import brands, submissions, users, leads, search, chat
import os

app = FastAPI(title="Drape — AI Fashion Stylist")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        os.getenv("FRONTEND_URL", ""),   # set this to your Vercel URL on Railway
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(brands.router)
app.include_router(submissions.router)
app.include_router(users.router)
app.include_router(leads.router)
app.include_router(search.router)
app.include_router(chat.router)
