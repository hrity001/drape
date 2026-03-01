import requests, json, re

OLLAMA_URL = "http://localhost:11434"
PARSE_MODEL = "llama3.2"

def parse_query(query: str) -> dict:
    """
    Send natural language query to Ollama llama3.2.
    Returns: { "country": ..., "price_range": ..., "category": ... }
    """
    prompt = f"""Extract fashion search filters from this query and return ONLY a single JSON object, nothing else, no explanation.

Keys required:
- "country": string or null
- "price_range": one of "Budget", "Mid", "Premium" or null  
- "category": string or null

Query: "{query}"

Output only the JSON object:"""

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": PARSE_MODEL, "prompt": prompt, "stream": False},
            timeout=30,
        )
        raw = response.json().get("response", "")

        # Find the FIRST complete JSON object only
        start = raw.find("{")
        if start == -1:
            return {}
        
        # Walk forward to find the matching closing brace
        depth = 0
        for i, ch in enumerate(raw[start:], start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    json_str = raw[start:i+1]
                    return json.loads(json_str)
        return {}
    except Exception:
        return {}
