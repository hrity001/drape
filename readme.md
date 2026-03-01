# 👗 AI Fashion Stylist — Brand Discovery Engine

A niche fashion brand discovery platform powered by AI. Helps users find homegrown, indie, and curated fashion brands based on their style preferences — with a swipe-based personalization engine and an AI stylist chat interface.

---

## 🎯 Project Vision

> "Find the perfect brand, not just the perfect product."

This platform aggregates hundreds of niche fashion brands (starting with India), enriches them with AI-generated metadata, and surfaces them to users through semantic search, swipe-based feedback, and a conversational AI stylist.

---

## 🗺️ Roadmap Overview

| Phase | Focus | Timeline |
|-------|-------|----------|
| Phase 0 | Scope & Niche Definition | Pre-work |
| Phase 1 | Database & Backend Setup | Week 1 |
| Phase 2 | Brand Acquisition Pipelines | Week 2–4 |
| Phase 3 | Deduplication & AI Enrichment | Week 3–5 |
| Phase 4 | AI Stylist & Discovery Engine | Week 5–6 |
| Phase 5 | Frontend MVP | Week 6–7 |
| Phase 6 | Monetization & Launch | Week 8 |

---

## 🏗️ Step-by-Step Build Plan

### Phase 0 — Define Scope & Focus

- **Target Niche:** India · Women · Swimwear / Casual / Sustainable
- **MVP Brand Seed Size:** ~300–500 brands
- **Monetization Model:** Affiliate links + Featured brand placement

---

### Phase 1 — Database & Backend Setup *(Week 1)*

#### Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11+ |
| Framework | FastAPI (async) |
| Database | PostgreSQL |
| ORM | SQLAlchemy (async) |
| Semantic Search | pgvector (1536-dim embeddings) |
| Deployment | Vercel / Heroku + Managed Postgres |

#### Database Schema

```
brands              — Approved, live brands
brand_leads         — Raw leads from discovery pipelines
brand_submissions   — Submitted by brands via public form
users               — Registered users
feedback            — Swipe likes/dislikes per user
```

#### Project Structure

```
ai-stylist/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # Async DB engine & session
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── crud.py              # Reusable DB operations
│   └── routes/
│       ├── brands.py        # Brand CRUD endpoints
│       ├── submissions.py   # Brand submission portal endpoints
│       └── users.py         # User & feedback endpoints
├── requirements.txt
└── readme.md
```

---

### Phase 2 — Brand Acquisition Pipelines *(Week 2–4)*

Four parallel pipelines feed into the `brand_leads` table:

#### A. Shopify Store Discovery
- Tools: BuiltWith / StoreLeads / Wappalyzer APIs
- Filter: `Shopify + Fashion + India`
- Extract: brand name, Instagram handle, website

#### B. Google Search Scraping
- Queries:
  - `site:instagram.com "homegrown brand" "India"`
  - `site:instagram.com "sustainable swimwear"`
- Extract Instagram handles & websites → deduplicate

#### C. Meta Ads Library Mining
- Filter: Country = India, Category = Fashion/Clothing
- Extract: advertiser name, website

#### D. Brand Submission Portal
- Public `/submit-brand` form
- Fields: brand name, website, Instagram, category, country, price range, description, images
- Flow: `brand_submissions` → admin review → `brands`

---

### Phase 3 — Deduplication & Enrichment *(Week 3–5)*

1. Normalize Instagram handles & domains
2. Remove duplicates across all pipeline sources
3. AI enrichment on brand descriptions:
   - Extract: style, target audience, aesthetic keywords, sustainability tier, price tier
4. Generate 1536-dim embeddings (OpenAI) → store in `brands.embedding` via `pgvector`

---

### Phase 4 — AI Stylist & Brand Discovery Engine *(Week 5–6)*

#### Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /brands/` | List all approved brands |
| `POST /brands/` | Add a new brand (admin) |
| `POST /search-brands` | AI-powered semantic brand search |
| `POST /search-products` | Product-level search |

#### AI Query Flow

```
User Input (natural language)
        ↓
GPT → Structured Query (filters: country, price, category, style)
        ↓
pgvector Semantic Search + SQL Filters
        ↓
Top 10–20 Brand Results
```

#### Swipe Personalization

- User swipes → `feedback` table updated
- Liked brands → update user preference vector
- Future results ranked by cosine similarity to user vector

---

### Phase 5 — Frontend MVP *(Week 6–7)*

- **Mobile-first** web app
- **Tabs:**
  - 🔍 Discover Brands
  - 🤖 AI Stylist
  - 📝 Submit Brand
- **Brand Card:** Logo, images, Instagram link, website, price range, tags
- **Search:** Simple bar + AI natural language query input
- **Swipe Interface:** Tinder-style for personalization

---

### Phase 6 — Monetization & Launch *(Week 8)*

- ✅ Affiliate links on brand/product cards
- ✅ Featured brand placement (paid)
- ✅ Deploy: Vercel (frontend) + Heroku/Railway (backend + Postgres)
- ✅ Analytics: user interactions, brand popularity, swipe patterns

---

## ⚙️ Local Development Setup

### Prerequisites

- Python 3.11+
- PostgreSQL with `pgvector` extension
- `asyncpg` driver

### Installation

```bash
# Clone the repo
git clone https://github.com/your-username/ai-stylist.git
cd ai-stylist

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Database Configuration

Update the connection string in `app/database.py`:

```python
DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/ai_stylist"
```

Enable pgvector in your Postgres instance:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Run the Server

```bash
uvicorn app.main:app --reload
```

API docs available at: `http://localhost:8000/docs`

---

## 🧩 Key Models

### `Brand`

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `name` | String | Brand name |
| `instagram_handle` | String | Unique IG handle |
| `website` | String | Brand website URL |
| `country` | String | Target country |
| `category` | Array[String] | Fashion categories |
| `price_range` | String | Budget / Mid / Premium |
| `description` | Text | Brand description |
| `tags` | Array[String] | Style/aesthetic tags |
| `embedding` | Vector(1536) | Semantic search vector |
| `is_featured` | Boolean | Paid featured placement |
| `created_at` | Timestamp | Auto-set on creation |

---

## 📡 API Reference

### Brands

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/brands/` | Create a new brand |
| `GET` | `/brands/` | List all brands |

---

## 🔮 Future Enhancements

- [ ] Instagram scraper for brand discovery
- [ ] Admin dashboard (brand approval workflow)
- [ ] User authentication (JWT)
- [ ] Swipe feedback → personalized recommendations
- [ ] AI stylist chat (GPT-4 powered)
- [ ] Affiliate link tracking & analytics
- [ ] Mobile app (React Native)

---

## 📄 License

MIT License — feel free to fork and build on top of this.