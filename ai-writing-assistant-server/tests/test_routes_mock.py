import pytest
import pytest_asyncio
from app.main import app as real_app
from app.providers.mock_provider import MockProvider
from app.services.rephrase_service import RephraseService
from fastapi import FastAPI
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport


@pytest_asyncio.fixture
async def app():
    app = real_app
    from app.routes import rephrase as mod

    def get_service_override():
        return RephraseService(MockProvider())

    mod.get_service = get_service_override
    return app


@pytest.mark.asyncio
async def test_rephrase_full(app: FastAPI):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {"input_text": "Hello team", "styles": ["professional", "casual"]}
        r = await ac.post("/v1/rephrase", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert "results" in data


@pytest.mark.asyncio
async def test_stream_agent_chat(app: FastAPI):
    """Test agent chat streaming endpoint"""

    async def test_sse():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            # Rebind sse event to current loop used by tests
            try:
                import asyncio

                from sse_starlette.sse import AppStatus

                AppStatus.should_exit_event = asyncio.Event()
            except Exception:
                pass

            # Agent stream expects RephraseRequest shape (input_text + styles)
            r = await ac.post(
                "/v1/agent/stream",
                json={"input_text": "Hi", "styles": ["professional"]},
            )
            assert r.status_code == 200
            assert "text/event-stream" in r.headers["content-type"]
            return r.status_code

    status = await test_sse()
    assert status == 200
