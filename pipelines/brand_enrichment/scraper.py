import httpx
import logging
from bs4 import BeautifulSoup

async def fetch_website_text(url: str, max_length: int = 5000):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; BrandEnricher/1.0)"
        }
        
        async with httpx.AsyncClient(
            timeout=20, 
            follow_redirects=True,
            headers=headers
        ) as client:
            response = await client.get(url)
        
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove unwanted tags
        for tag in soup(["script", "style", "noscript", "iframe", "nav", "footer"]):
            tag.decompose()
        
        # Prioritize main content
        main_content = soup.find("main") or soup.find("article") or soup
        text = main_content.get_text(separator=" ", strip=True)
        
        # Clean whitespace
        text = " ".join(text.split())
        
        return text[:max_length]
        
    except httpx.HTTPStatusError as e:
        logging.warning(f"HTTP {e.response.status_code} for {url}")
        return ""
    except Exception as e:
        logging.error(f"Failed to fetch {url}: {type(e).__name__}: {e}")
        return ""
