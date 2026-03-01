# 🤖 Drape — AI Features Roadmap (newpass123)

A comprehensive list of all AI features — implemented and planned — for the Drape fashion brand discovery platform.

---

## ✅ Implemented (Phases 1–5)

| Feature | Description | Tech Stack | Status |
|---------|-------------|-----------|--------|
| **Semantic Brand Search** | Natural language query → ranked brand results via vector similarity | pgvector + nomic-embed-text (768-dim) | ✅ Live |
| **LLM Query Parser** | Extracts structured filters (country, price, category) from free-text queries | Ollama llama3.2 | ✅ Live |
| **Swipe Personalization** | Liked brands update user preference vector via running average | pgvector cosine similarity | ✅ Live |
| **Personalized Recommendations** | Brands ranked by cosine similarity to user's taste vector | pgvector `<=>` operator | ✅ Live |
| **Style Quiz Seeding** | 5-question onboarding quiz → embed answers → seed preference vector | nomic-embed-text + pgvector | ✅ Live |
| **AI Brand Enrichment** | Extract style, aesthetic, price tier, tags from brand descriptions | Ollama llama3.2 | ✅ Live (pipeline) |

---

## 🔜 Tier 1 — Quick Wins (Under 1 Hour Each)

### 1. Similar Brands
**What:** "You might also like" section on each brand page — find the 5 most similar brands
**How:** Single SQL query using pgvector nearest neighbor on brand embeddings
```sql
SELECT * FROM brands
ORDER BY embedding <=> (SELECT embedding FROM brands WHERE id = :id)
LIMIT 6 OFFSET 1
```
**New endpoint:** `GET /brands/{id}/similar`
**Effort:** 10 min
**Impact:** Increases time-on-site, improves discovery

---

### 2. Negative Feedback Learning (RLHF-lite)
**What:** Dislikes push the user's preference vector *away* from that brand's style
**How:** Vector subtraction on dislike, weighted update on like
```python
# Like:   preference = 0.7 * preference + 0.3 * brand_embedding
# Dislike: preference = preference - 0.2 * brand_embedding
# Normalize after each update
```
**Files:** Update `create_feedback()` in `app/crud.py`
**Effort:** 30 min
**Impact:** Recommendations get smarter 2x faster

---

### 3. AI Tag Extraction Pipeline
**What:** Auto-generate style tags for brands that have none
**How:** Send brand description to llama3.2 → extract tags array
**Prompt:** `"Extract 5-8 style tags from this brand description. Return only a JSON array of lowercase strings. Description: {desc}"`
**Files:** Add to `pipelines/enrich_brands.py`
**Effort:** 20 min
**Impact:** Better search results, better filtering, better embeddings

---

### 4. AI Category Classification Pipeline
**What:** Auto-classify brands into categories (swimwear, casual, sustainable, etc.)
**How:** llama3.2 reads description → outputs category array
**Files:** Add to `pipelines/enrich_brands.py`
**Effort:** 20 min
**Impact:** Fixes empty `category` fields — makes all filters work correctly

---

### 5. Duplicate Brand Detection
**What:** Before inserting a new brand, check if a near-duplicate already exists
**How:** Check if any existing brand has `embedding <=> new_embedding < 0.1`
**Files:** Update `create_brand()` in `app/crud.py`
**Effort:** 15 min
**Impact:** Keeps brand database clean as it scales to 10,000+ brands

---

## 🚀 Tier 2 — Core AI Features (1–3 Hours Each)

### 6. RAG-Powered AI Stylist Chat
**What:** Conversational AI stylist grounded in real brand data — no hallucinations
**How:**
```
User message
    ↓
Embed message → pgvector search → retrieve top 5 matching brands
    ↓
Inject brand data into llama3.2 system prompt
    ↓
llama3.2 generates response using ONLY retrieved brands
    ↓
Response includes brand names, prices, links, reasoning
```
**New endpoint:** `POST /chat` with conversation history
**New frontend:** Chat UI on Stylist tab
**Effort:** 3 hours
**Impact:** ⭐⭐⭐⭐⭐ — The flagship AI feature, makes Drape feel like a real AI product

---

### 7. AI Style Profile Summary
**What:** Generate a natural language summary of the user's taste from their swipe history
**How:** Fetch user's liked brands → send names/tags to llama3.2 → generate summary
**Example output:** *"Your style is minimalist and sustainable. You prefer indie Indian brands in the ₹1K–3K range with an earthy, handcrafted aesthetic."*
**New endpoint:** `GET /users/{id}/style-summary`
**Effort:** 1 hour
**Impact:** Makes the AI feel personal — great for retention and sharing

---

### 8. Collaborative Filtering
**What:** "Users like you also liked..." — find users with similar taste, recommend their liked brands
**How:**
```
Step 1: Find top 10 users with closest preference_vector to yours
Step 2: Get brands they liked that you haven't seen
Step 3: Rank by how many similar users liked each brand
```
**New endpoint:** `GET /users/{id}/collaborative-recommendations`
**Effort:** 2 hours
**Impact:** Gets dramatically better with more users — classic Netflix-style recommendations

---

### 9. Contextual Bandits for Ranking
**What:** Balance exploration (new brands) vs exploitation (brands you'll definitely like)
**How:**
```python
score = cosine_similarity + exploration_bonus
exploration_bonus = 1 / (1 + times_shown_to_user)
```
**Files:** Update `semantic_search_brands()` in `app/crud.py`
**Effort:** 2 hours
**Impact:** Prevents filter bubble — users discover more diverse brands

---

### 10. Outfit Builder AI
**What:** User describes an occasion → AI suggests brands for each clothing piece
**Example:** "Beach vacation in Goa" → swimwear brand X + cover-up brand Y + accessories brand Z
**How:** llama3.2 breaks occasion into clothing categories → pgvector search per category → combine results
**New endpoint:** `POST /outfit-builder`
**Effort:** 2 hours
**Impact:** Unique feature — no competitor in India has this

---

## 🔬 Tier 3 — Advanced AI (3–6 Hours Each)

### 11. Multi-Modal Image Embeddings (CLIP)
**What:** Embed brand product images using CLIP — combine text + image vectors for richer search
**How:**
```python
from transformers import CLIPModel, CLIPProcessor

image_embedding = clip_model.encode_image(brand_image)  # 512-dim
text_embedding = ollama_embed(brand_description)         # 768-dim
# Combine: final = 0.6 * text + 0.4 * image (after dimension alignment)
```
**New DB column:** `brands.image_embedding` (Vector(512))
**Effort:** 4 hours
**Impact:** ⭐⭐⭐⭐⭐ — Visual search, much better aesthetic matching

---

### 12. Visual Style Transfer Search
**What:** User uploads a photo of an outfit → AI finds brands with matching aesthetic
**How:**
- User uploads image → CLIP embeds it → pgvector search on brand image embeddings
- Returns brands with similar visual style
**New endpoint:** `POST /search/by-image` (multipart file upload)
**Effort:** 5 hours
**Impact:** Premium feature — "Search by photo" is a major differentiator

---

### 13. Taste Drift Detection
**What:** Detect when a user's style preferences are changing over time
**How:**
- Store last 3 preference vectors with timestamps
- If cosine distance between current and 30-day-old vector > 0.3 → taste is drifting
- Show more diverse results + notify user: "Your style seems to be evolving"
**New DB column:** `users.preference_vector_history` (JSONB)
**Effort:** 3 hours
**Impact:** Adapts to seasonal changes, life events — much better long-term retention

---

### 14. Semantic Brand Clustering
**What:** Automatically cluster all brands into style niches using k-means on embeddings
**How:**
```python
from sklearn.cluster import KMeans
kmeans = KMeans(n_clusters=20)
labels = kmeans.fit_predict(all_brand_embeddings)
# Each cluster = a style niche: "sustainable swimwear", "bold streetwear", etc.
```
**New DB column:** `brands.cluster_id`
**New pipeline:** `pipelines/cluster_brands.py`
**Effort:** 2 hours
**Impact:** Auto-generates "Collections" feature — no manual curation needed

---

### 15. Trend Detection from Swipe Data
**What:** Identify which styles/aesthetics are trending based on aggregate swipe patterns
**How:**
- Aggregate all liked brand embeddings from the last 7 days
- Find the centroid → this is the "trending style vector"
- Brands closest to this centroid are "trending this week"
**New endpoint:** `GET /trending`
**Effort:** 2 hours
**Impact:** "Trending Now" section — drives engagement and repeat visits

---

### 16. Personalized Price Sensitivity Model
**What:** Learn each user's price sensitivity from their swipe history
**How:**
- Track price ranges of liked vs disliked brands per user
- Build a price preference score: `budget_score = avg_price_of_liked_brands`
- Boost brands in the user's preferred price range in search results
**Files:** Add `price_preference` field to User model
**Effort:** 2 hours
**Impact:** More relevant results — users stop seeing brands they can't afford

---

## 🌐 Tier 4 — Future / Research-Level

| Feature | Description | Tech | Effort |
|---------|-------------|------|--------|
| **Fine-tuned Fashion LLM** | Fine-tune llama3.2 on Indian fashion data for better query understanding | LoRA fine-tuning | 2 weeks |
| **Brand Sentiment Analysis** | Analyze Instagram comments/reviews to score brand reputation | Ollama + web scraping | 1 week |
| **Trend Forecasting** | Predict which styles will be popular next season using historical data | Time-series + embeddings | 2 weeks |
| **Personalized Email Digest** | Weekly AI-generated email: "New brands matching your style this week" | LLM + email service | 3 days |
| **Voice Search** | "Hey Drape, find me sustainable swimwear" | Whisper (speech-to-text) + existing search | 1 week |
| **AR Try-On** | Virtual try-on using brand product images | MediaPipe + CLIP | 1 month |

---

## 🤖 Tier 5 — Agentic AI & Orchestration Frameworks

These are modern AI engineering patterns that go beyond single LLM calls. They make Drape's AI smarter, more reliable, and more capable of complex multi-step reasoning.

---

### 17. LangGraph — Multi-Step AI Agent

**What:** Replace the single-shot RAG chat with a stateful graph-based agent that can reason, retry, and use multiple tools in sequence.

**Why it matters for Drape:** A single LLM call can't handle complex requests like *"I need a full beach wedding outfit under ₹5000 — top, bottom, and accessories from different brands."* LangGraph can.

**How it works:**
```
User: "Beach wedding outfit in Goa under ₹5000"
                ↓
    Node 1: Intent Classifier
        → intent = outfit_builder
        → occasion = beach_wedding
        → budget = 5000
                ↓
    Node 2: Category Planner
        → categories = [swimwear, cover-up, accessories]
                ↓
    Node 3: Parallel pgvector Search (one per category)
                ↓
    Node 4: Budget Filter + Ranker
                ↓
    Node 5: Quality Check — enough results?
        → if No: retry with broader query (loop back)
        → if Yes: continue
                ↓
    Node 6: Response Generator (llama3.2)
        → outfit recommendation with brand names, prices, links
```

**New files:**
- `app/agents/stylist_agent.py` — LangGraph graph definition
- `app/routes/chat.py` — `POST /chat` endpoint using the agent

**Upgrade path:**
1. Build simple RAG chat first (single LLM call, 2 hours)
2. Upgrade to LangGraph agent (adds retry, multi-step, 4 hours)

**Dependencies:** `pip install langgraph langchain-core`

**Effort:** 4–6 hours (after basic RAG chat exists)

**Impact:** ⭐⭐⭐⭐⭐ — Handles complex outfit requests, never hallucinates brands, retries on poor results

---

### 18. MCP Server — Drape as an AI Tool

**What:** Model Context Protocol (MCP) is Anthropic's standard for exposing your app's capabilities as tools that any LLM (Claude, GPT-4, etc.) can call natively.

**Why it matters for Drape:** You can expose Drape's search and recommendations as MCP tools, so:
- Claude.ai users can ask "find me sustainable Indian brands" and Claude calls your actual database
- Cursor/Windsurf can use Drape as a tool during development
- Any MCP-compatible client gets access to Drape's brand intelligence

**Tools you'd expose:**
```python
@mcp_tool
def search_brands(query: str, category: str = None, price_range: str = None) -> list[Brand]:
    """Search Drape's brand database using natural language"""

@mcp_tool
def get_similar_brands(brand_id: int) -> list[Brand]:
    """Find brands similar to a given brand"""

@mcp_tool
def get_recommendations(user_id: int) -> list[Brand]:
    """Get personalized brand recommendations for a user"""

@mcp_tool
def get_brand_details(brand_id: int) -> Brand:
    """Get full details for a specific brand"""
```

**New files:**
- `mcp_server/server.py` — MCP server definition
- `mcp_server/tools.py` — Tool implementations calling existing CRUD functions

**Dependencies:** `pip install mcp`

**Effort:** 2–3 hours (mostly boilerplate, reuses existing crud.py)

**Impact:** ⭐⭐⭐ — Developer-facing now, but positions Drape as an AI-native platform

---

### 19. Structured Outputs with Instructor

**What:** Force LLMs to always return valid, typed JSON — no more brace-depth walkers or JSON parsing hacks.

**Why it matters for Drape:** Your current [`query_parser.py`](pipelines/query_parser.py) uses a manual brace-depth walker to extract JSON from llama3.2 because the model sometimes returns extra text. Instructor eliminates this entirely.

**How it works:**
```python
import instructor
from pydantic import BaseModel

class ParsedQuery(BaseModel):
    search_query: str
    country: str | None
    price_range: str | None
    category: str | None

client = instructor.from_openai(ollama_client, mode=instructor.Mode.JSON)
result = client.chat.completions.create(
    model="llama3.2",
    response_model=ParsedQuery,
    messages=[{"role": "user", "content": user_query}]
)
# result is always a valid ParsedQuery — no parsing needed
```

**Files to update:** `pipelines/query_parser.py`

**Dependencies:** `pip install instructor`

**Effort:** 30 minutes

**Impact:** ⭐⭐⭐ — Eliminates all JSON parsing bugs, makes LLM outputs reliable

---

### 20. Semantic Caching with Redis

**What:** Cache LLM responses and embedding lookups by semantic similarity — not just exact string match.

**Why it matters for Drape:** If 100 users search "sustainable Indian brands", you don't need to call Ollama 100 times. Semantic caching detects that "eco-friendly Indian fashion" and "sustainable Indian brands" mean the same thing and returns the cached result.

**How it works:**
```
User query → embed query → check Redis for similar cached query
    → if cache hit (cosine similarity > 0.95): return cached result
    → if cache miss: run full search → cache result → return
```

**Dependencies:** `pip install redis semantic-cache` or use `GPTCache`

**Effort:** 2 hours

**Impact:** ⭐⭐⭐⭐ — 10x faster responses for popular queries, saves Ollama compute

---

### 21. LlamaIndex — Document + Brand Knowledge Base

**What:** LlamaIndex is a data framework for building RAG pipelines over structured and unstructured data. More powerful than raw pgvector for complex retrieval.

**Why it matters for Drape:** As you add brand blog posts, lookbooks, style guides, and Instagram captions, LlamaIndex can index all of it and make it searchable — not just brand descriptions.

**Use cases:**
- Index brand Instagram captions → search by vibe/aesthetic
- Index style blog posts → AI stylist can cite articles
- Index user-submitted reviews → sentiment-aware recommendations

**Effort:** 4–6 hours to set up, then incremental

**Impact:** ⭐⭐⭐ — More powerful RAG, better for content-heavy future

---

### 22. Guardrails AI — Safe LLM Outputs

**What:** Validate and sanitize LLM outputs before sending to users — prevent hallucinated brand names, toxic content, or off-topic responses.

**Why it matters for Drape:** Your AI stylist should only recommend brands that actually exist in your database. Guardrails can enforce this.

**How it works:**
```python
from guardrails import Guard
from guardrails.hub import ValidBrandName

guard = Guard().use(ValidBrandName, brands_in_db=all_brand_names)
result = guard(llama3.2_response)
# Raises if LLM hallucinated a brand name not in your database
```

**Effort:** 2 hours

**Impact:** ⭐⭐⭐ — Critical for production — prevents AI from recommending fake brands

---

### 23. Mem0 — Persistent AI Memory

**What:** Give the AI stylist long-term memory about each user — remembers past conversations, stated preferences, and style evolution across sessions.

**Why it matters for Drape:** Right now, every chat session starts fresh. With Mem0, the AI remembers: *"Last time you said you hate fast fashion. You liked Bunaai and Verb. You're shopping for a wedding in March."*

**How it works:**
```python
from mem0 import Memory

memory = Memory()
memory.add("User prefers sustainable brands under ₹3000", user_id=user_id)
memory.add("User liked Bunaai, Verb, and The Summer House", user_id=user_id)

# On next session:
relevant_memories = memory.search("beach outfit", user_id=user_id)
# → inject into LLM system prompt
```

**New DB:** Mem0 can use your existing PostgreSQL as its memory store

**Effort:** 2–3 hours

**Impact:** ⭐⭐⭐⭐⭐ — Makes the AI feel like a real personal stylist that knows you

---

## 🗺️ Recommended Implementation Order

```
Phase A — This Week (Quick Wins, ~2 hours total)
  ✅ Semantic Search (done)
  ✅ Swipe Personalization (done)
  → Similar Brands endpoint
  → Negative Feedback Learning
  → AI Tag + Category Extraction pipeline
  → Instructor for reliable LLM JSON (replaces brace-depth walker)

Phase B — Next Week (Core AI, ~8 hours total)
  → Simple RAG-Powered AI Stylist Chat (single LLM call)
  → Upgrade chat to LangGraph agent (multi-step, retry, outfit builder)
  → AI Style Profile Summary
  → Mem0 persistent memory for chat

Phase C — Month 2 (Advanced, ~15 hours total)
  → Multi-Modal Image Embeddings (CLIP)
  → Contextual Bandits Ranking
  → Semantic Brand Clustering
  → Trend Detection
  → Semantic Caching with Redis
  → Guardrails AI for safe outputs

Phase D — Month 3+ (Research-level + Platform)
  → MCP Server (expose Drape as AI tool)
  → LlamaIndex for brand content indexing
  → Visual Style Transfer Search
  → Taste Drift Detection
  → Fine-tuned Fashion LLM
  → Collaborative Filtering (needs 100+ users first)
```

---

## 🛠️ Tech Stack Summary

| Layer | Tool | Purpose |
|-------|------|---------|
| **Embeddings** | Ollama nomic-embed-text (768-dim) | Text → vector |
| **Image Embeddings** | CLIP (512-dim) | Image → vector |
| **Vector DB** | pgvector (PostgreSQL) | Similarity search |
| **LLM** | Ollama llama3.2 | Query parsing, chat, summaries |
| **Agent Orchestration** | LangGraph | Multi-step AI agents with state + retry |
| **LLM Tool Protocol** | MCP (Model Context Protocol) | Expose Drape as AI tools for Claude/GPT |
| **Structured Outputs** | Instructor | Force LLMs to return valid typed JSON |
| **AI Memory** | Mem0 | Persistent user memory across chat sessions |
| **RAG Framework** | LlamaIndex | Index brand content for richer retrieval |
| **Output Safety** | Guardrails AI | Prevent hallucinated brand names |
| **Semantic Cache** | Redis + GPTCache | Cache LLM responses by semantic similarity |
| **Clustering** | scikit-learn KMeans | Brand clustering |
| **Speech** | OpenAI Whisper | Voice search (future) |
| **Production LLM** | OpenAI GPT-4o-mini | Replace Ollama in production |