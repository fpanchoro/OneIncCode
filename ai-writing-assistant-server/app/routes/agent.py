import asyncio
import json

from app.providers.agent_provider import AgentProvider
from app.providers.mock_provider import MockProvider
from app.providers.openai_chat import OpenAIChatProvider
from app.schemas import RephraseRequest
from app.services.rephrase_service import RephraseService
from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse

router = APIRouter(prefix="/v1/agent", tags=["agent"])


def get_agent_service() -> RephraseService:
    # Try to use the full AgentProvider (requires OpenAI Agents SDK).
    try:
        provider = AgentProvider()
        return RephraseService(provider)
    except RuntimeError:
        # Fallback: prefer the OpenAIChatProvider if available (requires OPENAI_API_KEY), else MockProvider
        try:
            provider = OpenAIChatProvider()
            return RephraseService(provider)
        except Exception:
            provider = MockProvider()
            return RephraseService(provider)


@router.post("", response_model=dict)
async def run_agent(
    req: RephraseRequest, svc: RephraseService = Depends(get_agent_service)
):
    """Run a simple agent-style rephrase; if the AgentProvider (OpenAI Agents SDK)
    is not installed we fallback to a simpler orchestration using the chat provider or mock provider.
    """
    styles = svc.validate_styles(req.styles)
    rid = req.ensure_request_id()
    results = {}
    try:
        for s in styles:
            # provider.rephrase_full returns the final rephrase for each style
            results[s] = await svc.provider.rephrase_full(s, req.input_text)
        return {"request_id": rid, "results": results}
    except RuntimeError as re:
        raise HTTPException(status_code=501, detail=str(re))
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/stream")
async def run_agent_stream(
    req: RephraseRequest,
    svc: RephraseService = Depends(get_agent_service),
    example_format: bool = True,
):
    """Stream agent rephrases as SSE. By default `example_format=True` to emit staged
    '[wait]' messages and incremental fragments similar to the example you provided.
    """
    styles = svc.validate_styles(req.styles)
    rid = req.ensure_request_id()

    async def gen():
        try:
            yield {"event": "meta", "data": json.dumps({"request_id": rid})}
            for style in styles:
                label = style.capitalize()
                # get final sentence (may raise RuntimeError if provider is AgentProvider without SDK)
                try:
                    final = await svc.provider.rephrase_full(style, req.input_text)
                except RuntimeError as re:
                    yield {"event": "error", "data": json.dumps({"detail": str(re)})}
                    continue

                if example_format:
                    # Emit the initial wait label then incremental fragments
                    yield {
                        "event": "delta",
                        "data": json.dumps(
                            {"style": label, "delta": f"[wait] {label}:"}
                        ),
                    }
                    acc = []
                    for w in final.split():
                        acc.append(w)
                        await asyncio.sleep(0.02)
                        yield {
                            "event": "delta",
                            "data": json.dumps(
                                {
                                    "style": label,
                                    "delta": f"[wait] {label}: {' '.join(acc)}",
                                }
                            ),
                        }
                    yield {
                        "event": "style_end",
                        "data": json.dumps({"style": label, "final": final}),
                    }
                else:
                    # simple full emit
                    yield {
                        "event": "delta",
                        "data": json.dumps({"style": label, "delta": final}),
                    }
                    yield {
                        "event": "style_end",
                        "data": json.dumps({"style": label, "final": final}),
                    }

            yield {"event": "done", "data": "[DONE]"}
        finally:
            # nothing to cleanup for now
            return

    return EventSourceResponse(gen())
