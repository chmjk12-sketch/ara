"""
ARA - AI Client for DeepSeek API
"""
import httpx
import time
from src.config import settings


async def call_deepseek(
    system_prompt: str,
    messages: list,
    temperature: float = 0.7,
    max_tokens: int = 4096,
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

    start_time = time.time()

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    elapsed = time.time() - start_time

    # Extract content
    content = data["choices"][0]["message"]["content"]

    return content
