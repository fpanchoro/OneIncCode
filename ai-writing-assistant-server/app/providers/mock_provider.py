import asyncio
from typing import AsyncGenerator

from .base import LLMProvider


class MockProvider(LLMProvider):
    async def rephrase_full(self, style: str, input_text: str) -> str:
        return f"[{style.upper()}] {input_text}"

    async def rephrase_stream(
        self, style: str, input_text: str
    ) -> AsyncGenerator[str, None]:
        out = f"[{style.upper()}] {input_text}"
        for ch in out:
            await asyncio.sleep(0.001)
            yield ch
