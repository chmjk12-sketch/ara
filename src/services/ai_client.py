"""
ARA - AI Client for DeepSeek API
"""
import httpx
import time
import logging
from src.config import settings

logger = logging.getLogger(__name__)

# Shared async client for connection pooling
_http_client: httpx.AsyncClient = None


def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(connect=10.0, read=120.0, write=30.0, pool=10.0),
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
        )
    return _http_client


async def call_deepseek(
    system_prompt: str,
    messages: list,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    retries: int = 1,
) -> str:
    """Call DeepSeek API and return the response content."""
    url = f"{settings.DEEPSEEK_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.DEEPSEEK_MODEL,
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    last_error = None
    for attempt in range(retries + 1):
        try:
            start_time = time.time()
            client = get_http_client()
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            elapsed = time.time() - start_time
            logger.info(f"DeepSeek API call succeeded in {elapsed:.1f}s (attempt {attempt + 1})")
            return data["choices"][0]["message"]["content"]
        except httpx.TimeoutException as e:
            last_error = e
            logger.warning(f"DeepSeek API timeout (attempt {attempt + 1}/{retries + 1}): {e}")
        except httpx.HTTPStatusError as e:
            last_error = e
            logger.error(f"DeepSeek API HTTP error {e.response.status_code}: {e.response.text[:200]}")
            # Don't retry on auth errors
            if e.response.status_code in (401, 403):
                raise ValueError(f"DeepSeek API Key 无效或已过期 (HTTP {e.response.status_code})") from e
        except Exception as e:
            last_error = e
            logger.error(f"DeepSeek API error (attempt {attempt + 1}/{retries + 1}): {e}")

    raise ConnectionError(f"DeepSeek API 调用失败，已重试 {retries} 次: {last_error}")
