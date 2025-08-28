from unittest.mock import AsyncMock, patch

import pytest
from app.providers.agent_provider import AgentProvider
from app.providers.mock_provider import MockProvider
from app.providers.openai_chat import (STYLE_SYSTEM, OpenAIChatProvider,
                                       _messages)


def test_messages_format():
    """Test that _messages function formats messages correctly"""
    input_text = "Hello world"
    style = "professional"
    messages = _messages(style, input_text)

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == STYLE_SYSTEM["professional"]
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == input_text


def test_messages_unknown_style():
    """Test that _messages uses professional style for unknown styles"""
    messages = _messages("unknown_style", "test")
    assert messages[0]["content"] == STYLE_SYSTEM["professional"]


@pytest.mark.asyncio
async def test_openai_provider_rephrase_full():
    """Test OpenAI provider full response"""
    mock_response = {"choices": [{"message": {"content": " Hello team!"}}]}

    class MockResponse:
        def __init__(self):
            # Use a normal callable for raise_for_status to avoid AsyncMock runtime warning
            def _raise():
                return None

            self.raise_for_status = _raise

        def json(self):
            return mock_response

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=MockResponse()
        )

        provider = OpenAIChatProvider()
        result = await provider.rephrase_full("professional", "Hi team")

        assert result == "Hello team!"
        assert mock_client.return_value.__aenter__.return_value.post.called


@pytest.mark.asyncio
async def test_openai_provider_stream(mocker):
    """Test OpenAI provider streaming response"""

    # Build a mock response object that behaves like httpx streaming response
    class MockResp:
        def __init__(self):
            pass

        async def aiter_lines(self):
            yield 'data: {"choices":[{"delta":{"content":"Hello"}}]}\n'
            yield 'data: {"choices":[{"delta":{"content":" team"}}]}\n'
            yield "data: [DONE]\n"

        def raise_for_status(self):
            return None

    # Async context manager wrapper for the mock response
    class MockStreamCM:
        def __init__(self, resp):
            self.resp = resp

        async def __aenter__(self):
            return self.resp

        async def __aexit__(self, exc_type, exc, tb):
            return False

    mock_resp = MockResp()

    # client.stream should return an async context manager instance
    def mock_stream(*args, **kwargs):
        return MockStreamCM(mock_resp)

    client = AsyncMock()
    client.stream = mock_stream

    with patch("httpx.AsyncClient") as mock_client:
        # When used as 'async with httpx.AsyncClient() as client:' return our client mock
        mock_client.return_value.__aenter__.return_value = client

        provider = OpenAIChatProvider()
        chunks = []
        async for chunk in provider.rephrase_stream("professional", "Hi team"):
            chunks.append(chunk)

        assert chunks == ["Hello", " team"]


@pytest.mark.asyncio
async def test_mock_provider():
    """Test mock provider returns expected responses"""
    provider = MockProvider()

    # Test full response
    result = await provider.rephrase_full("any_style", "any_text")
    assert isinstance(result, str)
    assert len(result) > 0

    # Test streaming
    chunks = []
    async for chunk in provider.rephrase_stream("any_style", "any_text"):
        chunks.append(chunk)
    assert len(chunks) > 0


@pytest.mark.asyncio
async def test_agent_provider():
    """Test agent provider falls back to OpenAI chat when needed"""
    provider = AgentProvider()

    # Test fallback to OpenAI chat
    mock_response = {"choices": [{"message": {"content": " Hello from agent!"}}]}

    class MockResponse:
        def __init__(self):
            def _raise():
                return None

            self.raise_for_status = _raise

        def json(self):
            return mock_response

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=MockResponse()
        )

        result = await provider.rephrase_full("professional", "Hi")
        assert result == "Hello from agent!"
