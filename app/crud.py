from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Brand, BrandLead, BrandSubmission, User, Feedback
from sqlalchemy import text

# --- Brands ---
async def create_brand(db: AsyncSession, data: dict):
    brand = Brand(**data)
    db.add(brand)
    await db.commit()
    await db.refresh(brand)
    return brand

async def get_brands(db: AsyncSession):
    result = await db.execute(select(Brand))
    return result.scalars().all()

async def get_brand(db: AsyncSession, brand_id: int):
    result = await db.execute(select(Brand).where(Brand.id == brand_id))
    return result.scalar_one_or_none()

async def update_brand_embedding(db: AsyncSession, brand_id: int, embedding: list):
    result = await db.execute(select(Brand).where(Brand.id == brand_id))
    brand = result.scalar_one_or_none()
    if brand:
        brand.embedding = embedding
        await db.commit()
        await db.refresh(brand)
    return brand


# --- Brand Leads ---
async def create_brand_lead(db: AsyncSession, data: dict):
    lead = BrandLead(**data)
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    return lead

async def get_brand_leads(db: AsyncSession):
    result = await db.execute(select(BrandLead))
    return result.scalars().all()

async def promote_lead_to_brand(db: AsyncSession, lead_id: int):
    result = await db.execute(select(BrandLead).where(BrandLead.id == lead_id))
    lead = result.scalar_one_or_none()
    if lead:
        lead.is_processed = True
        brand = Brand(
            name=lead.name,
            instagram_handle=lead.instagram_handle,
            website=lead.website,
            country=lead.country,
        )
        db.add(brand)
        await db.commit()
        await db.refresh(brand)
        return brand
    return None


# --- Submissions ---
async def create_submission(db: AsyncSession, data: dict):
    submission = BrandSubmission(**data)
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    return submission

async def get_submissions(db: AsyncSession):
    result = await db.execute(select(BrandSubmission))
    return result.scalars().all()

async def approve_submission(db: AsyncSession, submission_id: int):
    result = await db.execute(select(BrandSubmission).where(BrandSubmission.id == submission_id))
    submission = result.scalar_one_or_none()
    if submission:
        submission.is_approved = True
        brand = Brand(
            name=submission.name,
            instagram_handle=submission.instagram_handle,
            website=submission.website,
            country=submission.country,
            category=submission.category,
            price_range=submission.price_range,
            description=submission.description,
        )
        db.add(brand)
        await db.commit()
        await db.refresh(brand)
        return brand
    return None


# --- Users ---
async def create_user(db: AsyncSession, data: dict):
    user = User(**data)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# --- Feedback ---
async def create_feedback(db: AsyncSession, data: dict):
    feedback = Feedback(**data)
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)

    # If liked, update user preference vector
    if data.get("liked"):
        brand = await get_brand(db, data["brand_id"])
        user_result = await db.execute(select(User).where(User.id == data["user_id"]))
        user = user_result.scalar_one_or_none()

        if brand and brand.embedding is not None and user:
            b_vec = brand.embedding
            if user.preference_vector is None:
                user.preference_vector = b_vec
            else:
                # Running average
                p = user.preference_vector
                user.preference_vector = [(p[i] + b_vec[i]) / 2 for i in range(len(p))]
            await db.commit()

    return feedback


async def semantic_search_brands(
    db: AsyncSession,
    query_vector: list,
    country: str = None,
    price_range: str = None,
    category: str = None,
    limit: int = 10,
    max_distance: float = None,
):
    vec_literal = "[" + ",".join(str(x) for x in query_vector) + "]"

    filter_clauses = ["embedding IS NOT NULL"]
    params = {"limit": limit}

    if country:
        filter_clauses.append("country ILIKE :country")
        params["country"] = f"%{country}%"
    if price_range:
        filter_clauses.append("price_range ILIKE :price_range")
        params["price_range"] = f"%{price_range}%"
    if category:
        filter_clauses.append("EXISTS (SELECT 1 FROM unnest(category) AS c WHERE c ILIKE :category)")
        params["category"] = f"%{category}%"

    # FIXED: Only add distance threshold if it's actually provided
    if max_distance is not None:
        filter_clauses.append(f"(embedding <=> '{vec_literal}'::vector) < {max_distance}")

    where_clause = " AND ".join(filter_clauses)

    sql = text(f"""
        SELECT id, name, website, instagram_handle, country, category,
               price_range, tags, description,
               (embedding <=> '{vec_literal}'::vector) AS score
        FROM brands
        WHERE {where_clause}
        ORDER BY embedding <=> '{vec_literal}'::vector
        LIMIT :limit
    """)

    result = await db.execute(sql, params)
    return [dict(row) for row in result.mappings().all()]



async def hybrid_search_brands(
    db: AsyncSession,
    query_text: str,
    query_vector: list,
    country: str = None,
    price_range: str = None,
    category: str = None,
    limit: int = 10,
):
    """
    Hybrid search: Combines exact/partial text matching with semantic search
    """
    # Build base query for text search
    text_query = select(Brand).where(
        Brand.embedding.isnot(None)  # Only brands with embeddings
    )
    
    # Add text matching (name, description, tags)
    text_query = text_query.where(
        (Brand.name.ilike(f"%{query_text}%")) |
        (Brand.description.ilike(f"%{query_text}%"))
    )
    
    # Add filters
    if country:
        text_query = text_query.where(Brand.country.ilike(f"%{country}%"))
    if price_range:
        text_query = text_query.where(Brand.price_range.ilike(f"%{price_range}%"))
    
    # Execute text search
    result = await db.execute(text_query.limit(limit))
    text_matches = result.scalars().all()
    
    # If we have text matches, return them
    if text_matches:
        return [
            {
                "id": b.id,
                "name": b.name,
                "website": b.website,
                "instagram_handle": b.instagram_handle,
                "country": b.country,
                "category": b.category,
                "price_range": b.price_range,
                "tags": b.tags,
                "description": b.description,
                "score": 0.0  # Text match
            }
            for b in text_matches
        ]
    
    # Otherwise, fall back to semantic search (no distance limit)
    return await semantic_search_brands(
        db, query_vector, country, price_range, category, limit,
        max_distance=None  # No distance limit for fallback
    )


async def get_similar_brands(
    db: AsyncSession,
    brand_id: int,
    limit: int = 5,
):
    """Find brands with similar embeddings to the given brand."""
    # First get the target brand's embedding
    brand = await get_brand(db, brand_id)
    if not brand or brand.embedding is None:
        return []
    
    # Format vector as pgvector literal
    vec_literal = "[" + ",".join(str(x) for x in brand.embedding) + "]"
    
    sql = text(f"""
        SELECT id, name, website, instagram_handle, country, category,
               price_range, tags, description,
               (embedding <=> '{vec_literal}'::vector) AS score
        FROM brands
        WHERE id != :brand_id AND embedding IS NOT NULL
        ORDER BY embedding <=> '{vec_literal}'::vector
        LIMIT :limit
    """)
    
    result = await db.execute(sql, {"brand_id": brand_id, "limit": limit})
    return [dict(row) for row in result.mappings().all()]


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def update_user_preference_vector(db: AsyncSession, user_id: int, vector: list):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        user.preference_vector = vector
        user.has_completed_quiz = True
        await db.commit()
    return user
