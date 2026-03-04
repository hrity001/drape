import httpx
import logging
from bs4 import BeautifulSoup
import re

async def fetch_website_text(url: str, max_chars=5000):
    """Fetch and extract relevant text from website"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove unwanted elements
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            
            # Prioritize important sections
            important_sections = []
            
            # Look for About/Story sections
            for selector in [
                'div[class*="about"]', 'section[class*="about"]',
                'div[class*="story"]', 'section[class*="story"]',
                'div[id*="about"]', 'section[id*="about"]'
            ]:
                sections = soup.select(selector)
                important_sections.extend([s.get_text(strip=True) for s in sections])
            
            # Get meta description
            meta_desc = soup.find("meta", {"name": "description"})
            if meta_desc:
                important_sections.insert(0, meta_desc.get("content", ""))
            
            # Get main content
            main_content = soup.find("main") or soup.find("body")
            if main_content:
                important_sections.append(main_content.get_text(strip=True)[:2000])
            
            # Combine and clean
            text = " ".join(important_sections)
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text[:max_chars]
            
    except Exception as e:
        logging.error(f"Error fetching {url}: {e}")
        return ""
