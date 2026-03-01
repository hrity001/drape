# 🚀 Drape — Production Deployment Checklist

Use this checklist before going live. Check off each item as you complete it.

---

## 🔴 Phase 1 — Critical Security Fixes (Do Before Anything Else)

### Backend Security
- [ ] **Generate a strong SECRET_KEY**
  ```bash
  openssl rand -hex 32
  ```
  Add to `.env`: `SECRET_KEY=<generated-value>`

- [ ] **Set `echo=False` in `app/database.py`**
  ```python
  engine = create_async_engine(DATABASE_URL, echo=False)
  ```

- [ ] **Update CORS to production domain in `app/main.py`**
  ```python
  allow_origins=["https://yourapp.vercel.app", "https://drape.in"]
  ```

- [ ] **Add rate limiting to search endpoint**
  ```bash
  pip install slowapi
  ```
  Add 30 req/min limit on `POST /search/brands`

- [ ] **Add try/except around all Ollama calls in `app/routes/search.py`**
  Return HTTP 503 if Ollama/embedding service is unavailable

- [ ] **Protect admin endpoints** (`POST /brands/`, `DELETE`) with API key header

- [ ] **Add input validation** — max length 500 chars on `SearchQuery.query`

### Frontend Security
- [ ] **Move API URL to environment variable**
  Create `frontend/.env.local`:
  ```
  NEXT_PUBLIC_API_URL=http://localhost:8000
  ```
  Create `frontend/.env.production`:
  ```
  NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app
  ```

- [ ] **Never commit `.env` files** — confirm `.env` is in `.gitignore`

---

## 🟡 Phase 2 — Backend Production Readiness

### Code Quality
- [ ] **Add `GET /health` endpoint** in `app/main.py`
  ```python
  @app.get("/health")
  async def health():
      return {"status": "ok", "version": "1.0.0"}
  ```

- [ ] **Add pagination to `GET /brands/`**
  Add `?limit=20&offset=0` query params to avoid returning all brands at once

- [ ] **Move pipeline import to module level** in `app/routes/search.py`
  ```python
  # Move this to top of file (not inside the function):
  from pipelines.query_parser import parse_query
  ```

- [ ] **Add DB connection pool settings** in `app/database.py`
  ```python
  engine = create_async_engine(
      DATABASE_URL,
      echo=False,
      pool_size=10,
      max_overflow=20,
      pool_pre_ping=True,
  )
  ```

- [ ] **Add structured logging** — replace `print()` statements with `logging.info()`

- [ ] **Add graceful shutdown** — add lifespan handler to FastAPI app

### Database
- [ ] **Run `alembic upgrade head`** as part of deploy script
- [ ] **Enable pgvector extension** on production Postgres:
  ```sql
  CREATE EXTENSION IF NOT EXISTS vector;
  ```
- [ ] **Create DB indexes** for common queries:
  ```sql
  CREATE INDEX ON brands (country);
  CREATE INDEX ON brands (price_range);
  CREATE INDEX ON brands USING ivfflat (embedding vector_cosine_ops);
  ```

---

## 🟢 Phase 3 — Infrastructure Setup

### Backend — Deploy to Railway

- [ ] **Create Railway account** at [railway.app](https://railway.app)
- [ ] **Create new project** → Add PostgreSQL service
- [ ] **Enable pgvector** on the Railway Postgres instance
- [ ] **Deploy backend** — connect GitHub repo, set root directory to `ai-stylist/`
- [ ] **Create `Procfile`** in `ai-stylist/`:
  ```
  web: alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```
- [ ] **Set environment variables** in Railway dashboard:
  ```
  DATABASE_URL=postgresql+asyncpg://<railway-postgres-url>
  SECRET_KEY=<your-generated-secret>
  OLLAMA_URL=<hosted-ollama-url-or-openai>
  ```
- [ ] **Note your Railway backend URL** (e.g. `https://drape-backend.railway.app`)

### Embedding Service — Production Decision
- [ ] **Option A (Recommended): Switch to OpenAI embeddings**
  - Replace Ollama `nomic-embed-text` with `text-embedding-3-small` (1536-dim)
  - Update `Vector(768)` → `Vector(1536)` in models + new Alembic migration
  - Add `OPENAI_API_KEY` to env vars
  - Cost: ~$0.02 per 1M tokens (very cheap)
- [ ] **Option B: Host Ollama on a GPU server** (RunPod, Modal, Replicate)

### Frontend — Deploy to Vercel

- [ ] **Create Vercel account** at [vercel.com](https://vercel.com)
- [ ] **Import GitHub repo** → set root directory to `ai-stylist/frontend`
- [ ] **Set environment variable** in Vercel dashboard:
  ```
  NEXT_PUBLIC_API_URL=https://drape-backend.railway.app
  ```
- [ ] **Deploy** → note your Vercel URL (e.g. `https://drape.vercel.app`)
- [ ] **Update CORS** in backend with the Vercel URL
- [ ] **Redeploy backend** with updated CORS

---

## 🔵 Phase 4 — Monitoring & Observability

- [ ] **Add Sentry** for error tracking
  ```bash
  pip install sentry-sdk[fastapi]
  npm install @sentry/nextjs
  ```
  Add `SENTRY_DSN` to env vars

- [ ] **Add uptime monitoring** — UptimeRobot (free) pinging `GET /health` every 5 min

- [ ] **Add analytics** — PostHog or Mixpanel for user behavior tracking
  ```bash
  npm install posthog-js
  ```

- [ ] **Set up log aggregation** — Railway provides basic logs; for more use Papertrail or Logtail

---

## 🌐 Phase 5 — Domain & DNS

- [ ] **Buy domain** — `drape.in` or `getdrape.com` (check on Namecheap/GoDaddy)
- [ ] **Point domain to Vercel** — add CNAME record in DNS settings
- [ ] **Add custom domain to Vercel** dashboard
- [ ] **Update CORS** in backend with the custom domain
- [ ] **Update `NEXT_PUBLIC_API_URL`** if backend also gets a custom domain
- [ ] **SSL certificate** — auto-provisioned by Vercel and Railway

---

## 📋 Pre-Launch Final Checks

- [ ] Test register → quiz → discover flow end-to-end on production URL
- [ ] Test `POST /search/brands` with a real query
- [ ] Test swipe feedback updates preference vector
- [ ] Test `GET /users/{id}/recommendations`
- [ ] Test brand submission form
- [ ] Verify all 27+ brands are visible on Discover page
- [ ] Check mobile layout on iPhone/Android
- [ ] Verify no `localhost` URLs appear anywhere in the production frontend
- [ ] Check browser console for errors on all 3 tabs
- [ ] Verify HTTPS is working (padlock in browser)

---

## 🔑 Environment Variables Reference

### Backend `.env`
```
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/drape
SECRET_KEY=<64-char-hex-string>
OLLAMA_URL=http://localhost:11434
OPENAI_API_KEY=<optional-if-switching-to-openai>
FRONTEND_URL=https://drape.vercel.app
```

### Frontend `.env.production`
```
NEXT_PUBLIC_API_URL=https://drape-backend.railway.app
```

---

## 📊 Post-Launch Monitoring

Check these metrics weekly after launch:

| Metric | Tool | Target |
|--------|------|--------|
| Uptime | UptimeRobot | 99.9% |
| Error rate | Sentry | < 1% |
| API response time | Railway logs | < 2s avg |
| Active users | PostHog | Growing week-over-week |
| Search queries | DB logs | Track top queries |
| Featured brand revenue | Manual | ₹5L MRR by Month 6 |