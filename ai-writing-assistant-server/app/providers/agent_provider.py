import asyncio
from typing import AsyncGenerator

from app.providers.mock_provider import MockProvider
from app.providers.openai_chat import OpenAIChatProvider

from .base import LLMProvider


class AgentProvider(LLMProvider):
    """AgentProvider is a thin wrapper that uses OpenAIChatProvider if available
    (i.e., you configured OPENAI_API_KEY) or falls back to MockProvider. This
    avoids requiring the separate OpenAI Agents SDK while still providing a
    predictable agent-like interface for the server.
    """

    def __init__(self):
        try:
            self._impl = OpenAIChatProvider()
        except Exception:
            # Fallback to mock provider
            self._impl = MockProvider()

    async def rephrase_full(self, style: str, input_text: str) -> str:
        return await self._impl.rephrase_full(style, input_text)

    async def rephrase_stream(
        self, style: str, input_text: str
    ) -> AsyncGenerator[str, None]:
        async for tok in self._impl.rephrase_stream(style, input_text):
            yield tok
