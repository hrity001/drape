from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import brands, submissions, users, leads, search

app = FastAPI(title="AI Fashion Stylist Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(brands.router)
app.include_router(submissions.router)
app.include_router(users.router)
app.include_router(leads.router)
app.include_router(search.router)
