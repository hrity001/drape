from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

class LLMBrandData(BaseModel):
    country: str
    category: str
    price_range: Literal["low", "mid", "premium", "luxury"]
    description: str
    tags: str
    is_featured: bool
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.0)  # NEW

class EnrichedBrand(BaseModel):
    name: str
    website: str
    instagram_handle: str
    country: str | None = None
    category: str | None = None
    price_range: Literal["low", "mid", "premium", "luxury"] | None = None
    description: str | None = None
    tags: str | None = None
    is_featured: bool = False
    enrichment_status: str | None = None
    confidence_score: float = 0.0  # NEW
    needs_review: bool = False  # NEW
    review_reason: str | None = None  # NEW
    last_updated: str | None = None  # NEW
