import asyncio
import json

from app.providers.mock_provider import MockProvider
from app.providers.openai_chat import OpenAIChatProvider
from app.schemas import CancelResponse, RephraseRequest, RephraseResponse
from app.services.rephrase_service import RephraseService
from app.utils.cancel import cancel_registry
from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse

router = APIRouter(prefix="/v1/rephrase", tags=["rephrase"])


def get_service() -> RephraseService:
    provider = OpenAIChatProvider()
    return RephraseService(provider)


@router.post("", response_model=RephraseResponse)
async def rephrase(req: RephraseRequest, svc: RephraseService = Depends(get_service)):
    styles = svc.validate_styles(req.styles)
    rid = req.ensure_request_id()
    try:
        results = await svc.rephrase_all_full(styles, req.input_text)
        return RephraseResponse(request_id=rid, results=results)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/stream")
async def rephrase_stream(
    req: RephraseRequest,
    svc: RephraseService = Depends(get_service),
    example_format: bool = False,
):
    """Stream rephrases. If example_format=True the server will emit staged '[wait]' messages
    and incremental sentence fragments to match the example format requested by the client.
    """
    styles = svc.validate_styles(req.styles)
    rid = req.ensure_request_id()
    cancel_ev = cancel_registry.create(rid)

    async def gen_example():
        # Produce the example-style staged output for each style
        try:
            yield {"event": "meta", "data": json.dumps({"request_id": rid})}
            for style in styles:
                if cancel_ev.is_set():
                    break
                # label capitalized for human-friendly display
                label = style.capitalize()
                # sample final sentence generation using the provider full call if available
                try:
                    final = await svc.provider.rephrase_full(style, req.input_text)
                except Exception:
                    final = f"{label}: {req.input_text}"

                # Break final into words and progressively emit
                words = final.split()
                # initial waits
                yield {
                    "event": "delta",
                    "data": json.dumps({"style": label, "delta": f"[wait] {label}:"}),
                }
                # progressively reveal sentence
                acc = []
                for w in words:
                    if cancel_ev.is_set():
                        break
                    acc.append(w)
                    # small pause to simulate streaming
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
                # final emit for style
                yield {
                    "event": "style_end",
                    "data": json.dumps({"style": label, "final": final}),
                }
            yield {"event": "done", "data": "[DONE]"}
        finally:
            cancel_registry.clear(rid)

    async def gen_default():
        # Existing behavior: stream raw deltas from provider
        try:
            yield {"event": "meta", "data": json.dumps({"request_id": rid})}
            for style in styles:
                if cancel_ev.is_set():
                    break
                yield {"event": "style_start", "data": style}
                async for delta in svc.stream_style(style, req.input_text):
                    if cancel_ev.is_set():
                        break
                    yield {
                        "event": "delta",
                        "data": json.dumps({"style": style, "delta": delta}),
                    }
                yield {"event": "style_end", "data": style}
            yield {"event": "done", "data": "[DONE]"}
        finally:
            cancel_registry.clear(rid)

    if example_format:
        return EventSourceResponse(gen_example())
    return EventSourceResponse(gen_default())


@router.post("/{request_id}/cancel", response_model=CancelResponse)
async def cancel(request_id: str):
    ok = cancel_registry.cancel(request_id)
    return CancelResponse(request_id=request_id, cancelled=ok)
