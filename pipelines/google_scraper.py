"""
Pipeline B: Google Search Scraper
----------------------------------
Searches Google for Indian fashion brand Instagram handles using
predefined queries, extracts brand name + Instagram handle + website,
and posts each result to the /leads/ API endpoint.

Usage:
    python -m pipelines.google_scraper

Requirements:
    pip install googlesearch-python requests
"""

import re
import time
import json
import requests
from googlesearch import search

# ── Config ────────────────────────────────────────────────────────────────────

API_BASE_URL = "http://localhost:8000"  # Change to deployed URL in production

SEARCH_QUERIES = [
    'site:instagram.com "homegrown brand" "India" fashion',
    'site:instagram.com "sustainable fashion" India women',
    'site:instagram.com "indie brand" India clothing',
    'site:instagram.com "swimwear" India brand',
    'site:instagram.com "ethnic wear" India homegrown',
    'site:instagram.com "slow fashion" India women',
    'site:instagram.com "handmade clothing" India brand',
]

# Seconds to wait between Google requests to avoid rate limiting
SEARCH_DELAY = 2.0

# Max results per query
RESULTS_PER_QUERY = 10

# ── Helpers ───────────────────────────────────────────────────────────────────

INSTAGRAM_URL_RE = re.compile(
    r"instagram\.com/([A-Za-z0-9_.]+)/?", re.IGNORECASE
)


def extract_instagram_handle(url: str) -> str | None:
    """Extract @handle from an Instagram URL."""
    match = INSTAGRAM_URL_RE.search(url)
    if match:
        handle = match.group(1)
        # Skip generic Instagram pages
        if handle.lower() in {"p", "reel", "stories", "explore", "accounts"}:
            return None
        return handle
    return None


def infer_brand_name(handle: str) -> str:
    """Convert an Instagram handle to a human-readable brand name."""
    # Replace dots/underscores with spaces and title-case
    return handle.replace(".", " ").replace("_", " ").title()


def post_lead(name: str, instagram_handle: str, source_url: str) -> bool:
    """POST a single lead to the /leads/ API. Returns True on success."""
    payload = {
        "name": name,
        "instagram_handle": instagram_handle,
        "website": None,
        "country": "India",
        "source": "google",
        "raw_data": json.dumps({"source_url": source_url}),
    }
    try:
        response = requests.post(f"{API_BASE_URL}/leads/", json=payload, timeout=10)
        if response.status_code == 200:
            print(f"  ✅ Saved: @{instagram_handle} ({name})")
            return True
        else:
            print(f"  ⚠️  API error {response.status_code} for @{instagram_handle}: {response.text}")
            return False
    except requests.RequestException as e:
        print(f"  ❌ Request failed for @{instagram_handle}: {e}")
        return False


# ── Main Pipeline ─────────────────────────────────────────────────────────────

def run():
    seen_handles: set[str] = set()
    total_saved = 0

    for query in SEARCH_QUERIES:
        print(f"\n🔍 Query: {query}")
        try:
            results = list(search(query, num_results=RESULTS_PER_QUERY, lang="en"))
        except Exception as e:
            print(f"  ❌ Search failed: {e}")
            time.sleep(SEARCH_DELAY * 3)
            continue

        print(f"  📦 Got {len(results)} results:")
        for url in results:
            print(f"     → {url}")
            handle = extract_instagram_handle(url)
            if not handle:
                print(f"       (no Instagram handle found)")
                continue
            if handle.lower() in seen_handles:
                print(f"  ⏭️  Duplicate, skipping: @{handle}")
                continue

            seen_handles.add(handle.lower())
            name = infer_brand_name(handle)
            success = post_lead(name, handle, url)
            if success:
                total_saved += 1

            time.sleep(0.3)  # Small delay between API calls

        time.sleep(SEARCH_DELAY)  # Delay between Google queries

    print(f"\n✅ Done. Total leads saved: {total_saved}")


if __name__ == "__main__":
    run()

