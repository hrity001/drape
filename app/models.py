from sqlalchemy import Column, Integer, String, Boolean, Text, ARRAY, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class Brand(Base):
    __tablename__ = "brands"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    instagram_handle = Column(String, unique=True)
    website = Column(String, unique=True)
    country = Column(String)
    category = Column(ARRAY(String))
    price_range = Column(String)
    description = Column(Text)
    tags = Column(ARRAY(String))
    embedding = Column(Vector(768), nullable=True)  # nomic-embed-text via Ollama (768-dim)
    is_featured = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


class BrandLead(Base):
    __tablename__ = "brand_leads"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    instagram_handle = Column(String)
    website = Column(String)
    country = Column(String)
    source = Column(String)  # e.g. "shopify", "google", "meta_ads"
    raw_data = Column(Text)
    is_processed = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


class BrandSubmission(Base):
    __tablename__ = "brand_submissions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    instagram_handle = Column(String)
    website = Column(String)
    country = Column(String)
    category = Column(ARRAY(String))
    price_range = Column(String)
    description = Column(Text)
    images = Column(ARRAY(String))
    is_approved = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    preference_vector = Column(Vector(768), nullable=True)  # user taste vector (768-dim)
    created_at = Column(TIMESTAMP, server_default=func.now())
    hashed_password = Column(String, nullable=True)
    has_completed_quiz = Column(Boolean, default=False)



class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    brand_id = Column(Integer, nullable=False)
    liked = Column(Boolean, nullable=False)  # True = like, False = dislike
    created_at = Column(TIMESTAMP, server_default=func.now())
