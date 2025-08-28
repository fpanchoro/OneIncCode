from typing import AsyncGenerator

import pytest
from app.providers.mock_provider import MockProvider
from app.services.rephrase_service import RephraseService


def create_test_provider(
    full_response: str = "Test response", stream_chunks: list[str] = None
):
    """Create a test provider with controlled responses"""
    stream_chunks = stream_chunks or ["Hello", " world"]

    class TestProvider:
        """Provider de prueba con respuestas controladas"""

        async def rephrase_full(self, style: str, input_text: str) -> str:
            return f"{style}: {full_response}"

        async def rephrase_stream(
            self, style: str, input_text: str
        ) -> AsyncGenerator[str, None]:
            for chunk in stream_chunks:
                yield chunk

    return TestProvider()


@pytest.mark.asyncio
async def test_rephrase_service_full():
    """Test respuesta completa del servicio"""
    expected = "test response"
    provider = create_test_provider(full_response=expected)
    service = RephraseService(provider)

    result = await service.rephrase_all_full(["professional", "casual"], "Hi")
    assert isinstance(result, dict)
    assert "professional" in result
    assert "casual" in result
    assert result["professional"] == f"professional: {expected}"
    assert result["casual"] == f"casual: {expected}"


@pytest.mark.asyncio
async def test_rephrase_service_stream():
    """Test respuesta streaming del servicio"""
    chunks = ["Hello", " Team", "!"]
    provider = create_test_provider(stream_chunks=chunks)
    service = RephraseService(provider)

    collected = []
    async for chunk in service.stream_style("professional", "Hi"):
        collected.append(chunk)

    assert collected == chunks


@pytest.mark.asyncio
async def test_rephrase_service_with_mock_provider():
    """Test el servicio con el MockProvider real"""
    service = RephraseService(MockProvider())

    # Test respuesta completa
    result = await service.rephrase_all_full(["professional"], "Test input")
    assert isinstance(result, dict)
    assert "professional" in result
    assert isinstance(result["professional"], str)

    # Test streaming
    chunks = []
    async for chunk in service.stream_style("professional", "Test input"):
        assert isinstance(chunk, str)
        chunks.append(chunk)
    assert len(chunks) > 0
