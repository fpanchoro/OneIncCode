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
    """Fixture para obtener la app con el mock provider"""
    app = real_app
    from app.routes import agent, rephrase

    def get_rephrase_service_override():
        return RephraseService(MockProvider())

    rephrase.get_service = get_rephrase_service_override

    def get_agent_service_override():
        return RephraseService(MockProvider())

    agent.get_service = get_agent_service_override

    return app


@pytest.mark.asyncio
async def test_healthz(app: FastAPI):
    """Test health check endpoint"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/healthz")
        assert r.status_code == 200
        data = r.json()
        assert data["ok"] is True


@pytest.mark.asyncio
async def test_rephrase_full_multiple_styles(app: FastAPI):
    """Test rephrase endpoint with multiple styles"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "input_text": "Hello team",
            "styles": ["professional", "casual", "polite"],
        }
        r = await ac.post("/v1/rephrase", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert "results" in data
        assert len(data["results"]) == len(payload["styles"])
        for style in payload["styles"]:
            assert style in data["results"]
            assert isinstance(data["results"][style], str)


@pytest.mark.asyncio
async def test_rephrase_full_validation(app: FastAPI):
    """Test input validation for rephrase endpoint"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Test empty input
        r = await ac.post(
            "/v1/rephrase", json={"input_text": "", "styles": ["professional"]}
        )
        assert r.status_code == 422

        # Test missing required field
        r = await ac.post("/v1/rephrase", json={"styles": ["professional"]})
        assert r.status_code == 422

        # Test invalid style
        r = await ac.post(
            "/v1/rephrase", json={"input_text": "test", "styles": ["invalid_style"]}
        )
        assert r.status_code == 200  # Should work with fallback to professional


@pytest.mark.asyncio
async def test_rephrase_stream_format(app: FastAPI):
    """Test SSE streaming format for rephrase endpoint"""

    async def test_stream():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            r = await ac.post(
                "/v1/rephrase/stream",
                json={"input_text": "Hi", "styles": ["professional"]},
            )
            assert r.status_code == 200
            assert r.headers.get("content-type", "").startswith("text/event-stream")

            # Parse SSE events
            events = []
            for line in r.content.decode().split("\n"):
                if line.startswith("data:"):
                    events.append(line[5:].strip())

            return events

    events = await test_stream()
    assert len(events) > 0
    assert any("delta" in event for event in events)


@pytest.mark.asyncio
async def test_agent_endpoint(app: FastAPI):
    """Test agent endpoint"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {"input_text": "Hello AI", "styles": ["professional"]}
        r = await ac.post("/v1/agent", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert "request_id" in data
        assert "results" in data
        assert isinstance(data["results"], dict)
        assert "professional" in data["results"]


@pytest.mark.asyncio
async def test_agent_stream(app: FastAPI):
    """Test agent streaming endpoint"""
    # sse_starlette uses an event bound to a loop; ensure it's re-bound to current loop
    try:
        import asyncio

        from sse_starlette.sse import AppStatus

        AppStatus.should_exit_event = asyncio.Event()
    except Exception:
        pass

    async def test_stream():
        transport = ASGITransport(app=app)
        ac = AsyncClient(transport=transport, base_url="http://test")
        try:
            payload = {"input_text": "Hello AI", "styles": ["professional"]}
            r = await ac.post("/v1/agent/stream", json=payload)
            # Basic SSE validation
            assert r.status_code == 200
            assert "text/event-stream" in r.headers["content-type"]
            return r.status_code
        finally:
            await ac.aclose()

    status = await test_stream()
    assert status == 200
