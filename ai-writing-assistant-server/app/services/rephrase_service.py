from typing import AsyncGenerator, Dict, List

from app.providers.base import LLMProvider
from app.schemas import DEFAULT_STYLES


class RephraseService:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def validate_styles(self, styles: List[str]) -> List[str]:
        return styles or DEFAULT_STYLES

    async def rephrase_all_full(self, styles: List[str], text: str) -> Dict[str, str]:
        results: Dict[str, str] = {}
        for s in styles:
            results[s] = await self.provider.rephrase_full(s, text)
        return results

    async def stream_style(self, style: str, text: str) -> AsyncGenerator[str, None]:
        async for tok in self.provider.rephrase_stream(style, text):
            yield tok
