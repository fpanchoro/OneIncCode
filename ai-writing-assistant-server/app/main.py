from app.config import CORS_ORIGINS
from app.routes.agent import router as agent_router
from app.routes.rephrase import router as rephrase_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Writing Assistant Server (FastAPI)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if CORS_ORIGINS == ["*"] else CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/healthz")
def healthz():
    # compatibility endpoint for docker healthchecks
    return {"ok": True}


app.include_router(rephrase_router)
app.include_router(agent_router)
