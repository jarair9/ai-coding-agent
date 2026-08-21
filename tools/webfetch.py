

import httpx
import asyncio
from urllib.parse import urlparse


async def webfetch(url: str,timeout=120):
    parsed = urlparse(url)
    if not parsed.scheme or parsed.scheme not in ("http", "https"):
        return {"type": "error", "error": f"Url must be http:// or https://"}
    try:

        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout),follow_redirects=True,) as client:
            response = await client.get(url)
            response.raise_for_status()
            text = response.text
            


    except httpx.HTTPStatusError as e:
            return f"HTTP {e.response.status_code}: {e.response.reason_phrase}",
            
    except Exception as e:
        return {"type": "error", "error": f"Request failed: {e}" }
    
     
    if len(text) > 100 * 1024:
        text = text[: 100 * 1024] + "\n... [content truncated]"

    return {
        
        "content": text,
        "status_code": response.status_code,
        "contnet Lenght": len(response.content) 
    }
