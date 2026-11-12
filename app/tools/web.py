import re
import httpx
from atlas.app import llm

_TAG_RE = re.compile(r"<[^>]+>")

def _strip_html(html):
    text = _TAG_RE.sub(" ", html)
    return re.sub(r"\s+", " ", text).strip()

async def search(query, max_results=5):
    if llm.is_demo():
        return [
            {"title": f"Mock result {i+1} for '{query}'", "url": f"https://example.com/{i+1}", "snippet": "Simulated search snippet."}
            for i in range(max_results)
        ]
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://html.duckduckgo.com/html/", params={"q": query}, timeout=10)
    return [{"title": "DuckDuckGo result", "url": "https://duckduckgo.com", "snippet": _strip_html(resp.text)[:200]}]

async def fetch_page(url, max_chars=3500):
    if llm.is_demo():
        return f"[DEMO] Mock page content for {url}"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10)
        return _strip_html(resp.text)[:max_chars]
    except Exception as e:
        return f"Error fetching page: {e}"
