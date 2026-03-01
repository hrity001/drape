from pydantic import BaseModel
from typing import List, Optional

class EmbeddingUpdate(BaseModel):
    embedding: List[float]

class BrandLeadCreate(BaseModel):
    name: Optional[str] = None
    instagram_handle: Optional[str] = None
    website: Optional[str] = None
    country: Optional[str] = None
    source: Optional[str] = None  # e.g. "shopify", "google", "meta_ads"
    raw_data: Optional[str] = None

class BrandLeadOut(BrandLeadCreate):
    id: int
    is_processed: bool
    model_config = {"from_attributes": True}

class BrandBase(BaseModel):
    name: str
    instagram_handle: Optional[str] = None
    website: Optional[str] = None
    country: Optional[str] = None
    category: Optional[List[str]] = None
    price_range: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None

class BrandCreate(BrandBase):
    pass

class BrandOut(BrandBase):
    id: int
    is_featured: bool
    model_config = {"from_attributes": True}

class BrandSubmissionCreate(BaseModel):
    name: str
    instagram_handle: Optional[str] = None
    website: Optional[str] = None
    country: Optional[str] = None
    category: Optional[List[str]] = None
    price_range: Optional[str] = None
    description: Optional[str] = None
    images: Optional[List[str]] = None

class BrandSubmissionOut(BrandSubmissionCreate):
    id: int
    is_approved: bool
    model_config = {"from_attributes": True}

class UserCreate(BaseModel):
    email: str
    name: Optional[str] = None

class UserOut(UserCreate):
    id: int
    model_config = {"from_attributes": True}

class FeedbackCreate(BaseModel):
    user_id: int
    brand_id: int
    liked: bool

class FeedbackOut(FeedbackCreate):
    id: int
    model_config = {"from_attributes": True}

class SearchQuery(BaseModel):
    query: str                           # "sustainable swimwear from India under ₹3000"
    country: Optional[str] = None        # manual override
    price_range: Optional[str] = None    # manual override
    category: Optional[str] = None       # manual override
    limit: int = 10

class SearchResult(BaseModel):
    id: int
    name: str
    website: Optional[str] = None
    instagram_handle: Optional[str] = None
    country: Optional[str] = None
    category: Optional[List[str]] = None
    price_range: Optional[str] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None
    score: Optional[float] = None        # cosine similarity score
    model_config = {"from_attributes": True}

class UserRegister(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    has_completed_quiz: bool
class ChatMessage(BaseModel):
    role: str          # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []   # previous turns
    user_id: Optional[int] = None               # for personalization (optional)

class ChatResponse(BaseModel):
    reply: str
    brands: Optional[List[SearchResult]] = []   # brands referenced in the reply
