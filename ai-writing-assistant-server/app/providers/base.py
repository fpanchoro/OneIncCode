from typing import AsyncGenerator


class LLMProvider:
    async def rephrase_full(self, style: str, input_text: str) -> str:
        raise NotImplementedError

    async def rephrase_stream(
        self, style: str, input_text: str
    ) -> AsyncGenerator[str, None]:
        raise NotImplementedError
