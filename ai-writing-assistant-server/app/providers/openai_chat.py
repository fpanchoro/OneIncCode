import json
import os
import time
from typing import AsyncGenerator, Optional

import httpx
from app.config import OPENAI_API_KEY, OPENAI_MODEL

# Allow temperature to be set via environment variable, default 0.7
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
from app.utils.logging import logger
from ratelimit import limits, sleep_and_retry
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import LLMProvider

OPENAI_URL = "https://api.openai.com/v1/chat/completions"
MAX_RETRIES = 3
CALLS_PER_MINUTE = 60  # Adjust based on your API tier

STYLE_SYSTEM = {
    "professional": (
        "You are an expert English writer. Rewrite the following text in a professional, clear, and concise manner. "
        "Always respond in English, regardless of the input language. Do not translate, but rewrite in a professional tone. "
        "Do not include explanations or preambles. Only output the rewritten text."
    ),
    "casual": (
        "You are an expert English writer. Rewrite the following text in a friendly, casual, and approachable tone. "
        "Always respond in English, regardless of the input language. Do not translate, but rewrite in a casual tone. "
        "Do not include explanations or preambles. Only output the rewritten text."
    ),
    "polite": (
        "You are an expert English writer. Rewrite the following text in a courteous, respectful, and polite tone. "
        "Always respond in English, regardless of the input language. Do not translate, but rewrite in a polite tone. "
        "Do not include explanations or preambles. Only output the rewritten text."
    ),
    "social-media": (
        "You are an expert English copywriter for social media. Rewrite the following text to be catchy, brief, and engaging for social media audiences. "
        "Always respond in English, regardless of the input language. Do not translate, but rewrite for social media. "
        "Do not include explanations or preambles. Only output the rewritten text."
    ),
}

HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json",
}


def _messages(style: str, input_text: str):
    sys = STYLE_SYSTEM.get(style, STYLE_SYSTEM["professional"])
    return [
        {"role": "system", "content": sys},
        {"role": "user", "content": input_text},
    ]


class OpenAIChatProvider(LLMProvider):
    async def rephrase_full(self, style: str, input_text: str) -> str:
        async with httpx.AsyncClient(timeout=60) as client:
            payload = {
                "model": OPENAI_MODEL,
                "messages": _messages(style, input_text),
                "temperature": OPENAI_TEMPERATURE,
                "stream": False,
            }
            r = await client.post(OPENAI_URL, headers=HEADERS, json=payload)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"].strip()

    async def rephrase_stream(
        self, style: str, input_text: str
    ) -> AsyncGenerator[str, None]:
        async with httpx.AsyncClient(timeout=None) as client:
            payload = {
                "model": OPENAI_MODEL,
                "messages": _messages(style, input_text),
                "temperature": OPENAI_TEMPERATURE,
                "stream": True,
            }
            async with client.stream(
                "POST", OPENAI_URL, headers=HEADERS, json=payload
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    data = line[6:]
                    if data.strip() == "[DONE]":
                        break
                    try:
                        obj = json.loads(data)
                        delta = obj["choices"][0]["delta"].get("content", "")
                        if delta:
                            yield delta
                    except Exception:
                        continue
