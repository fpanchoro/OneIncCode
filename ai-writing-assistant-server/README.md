## Makefile usage

From the repository root, you can use the `Makefile` for common Docker Compose tasks:

```
make up        # Start all services (build if needed)
make down      # Stop and remove all containers, networks, and volumes
make restart   # Stop everything, then start again (useful if ports are stuck)
make logs      # Follow logs for all services
make ps        # List running containers and port mappings
```

# AI Writing Assistant - Server

FastAPI server for a text rephrasing / style assistant and agent. This service is intended to run in Docker as part of a monorepo (frontend + backend).

## What it does

- Exposes HTTP and SSE endpoints for text rephrasing and an agent that applies styles.
- Integrates providers (for example OpenAI) via adapters in `app/providers/`.
- Designed to run behind an Nginx proxy (the repo includes configuration for this).

## Requirements

- Docker & Docker Compose (v2)
- Python 3.11+ (only if you want to run without Docker)

## Quick start: run with Docker Compose

It's recommended to run the service with Docker Compose for reproducibility. From the repository root:

```bash
docker compose build
docker compose up --build
```

This will bring up the services defined in `docker-compose.yml` (backend and frontend/proxy depending on the repo).

To follow logs:

```bash
docker compose logs -f
```

To stop and clean up:

```bash
docker compose down --volumes --remove-orphans
```

## Environment variables (.env)

The project uses a `.env` file at `ai-writing-assistant-server/.env`. Do not commit secrets to version control.

Example `.env` (use real values in your environment):

```properties
# API key (keep secret)
OPENAI_API_KEY=sk-...REDACTED...
# Default model
OPENAI_MODEL=gpt-4o-mini
# Allowed CORS origins (e.g. local frontend)
CORS_ORIGINS=http://localhost:8081
# FastAPI host and port
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```


**Frontend URL:**

When running with Docker Compose, the frontend is available at: [http://localhost:8090](http://localhost:8090)

Note: in local development the UI commonly runs at `http://localhost:8081` (Vite). Adjust `CORS_ORIGINS` to match your frontend origin.

## Run locally (without Docker)

1. Create and activate a virtual environment (Mac/Linux):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Export environment variables or create a `.env` file with the required variables.
3. Run the server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Tests

The project uses `pytest` and `pytest-asyncio` for unit and integration tests. Run tests from the `ai-writing-assistant-server` directory:

```bash
pytest -q
```

If running tests inside Docker, run them in a container that has the dependencies installed.

## Main endpoints

- POST /v1/agent
  - JSON: {"input_text":"...","styles":["style1","style2"]}
  - Response: JSON with rephrased results.

- POST /v1/agent/stream
  - Agent streaming (SSE). Use the same payload as `/v1/agent`.

- POST /v1/rephrase
  - Rephrase endpoint (may be proxied from the frontend).

Example with curl (replace host/port as needed):

```bash
curl -s -X POST http://localhost:8081/v1/agent \
  -H "Content-Type: application/json" \
  -d '{"input_text":"Hello world","styles":["professional"]}' | jq
```

For the stream endpoint (SSE) use `curl -N` or an SSE-capable client.

## Development and key structure

- `app/main.py` - FastAPI application entrypoint.
- `app/routes/` - HTTP routes (agent, rephrase, etc.).
- `app/providers/` - provider adapters (OpenAI, mock, etc.).
- `app/services/` - business logic and orchestration.
- `app/utils/` - utilities (cancellation, helpers).
- `tests/` - unit and integration tests.

## Best practices

- Never commit your `OPENAI_API_KEY` or `.env` files with secrets to version control.
- For reproducible CI, run tests inside containers or use a clean virtual environment.
- Use `docker compose logs -f` to debug startup issues and `docker compose exec` to access containers.

## Common issues

- Nginx error: "host not found in upstream" → Ensure runtime DNS resolution is enabled in `nginx.conf` or that Docker Compose services share the same network.
- CORS: Adjust `CORS_ORIGINS` to allow the frontend origin (e.g. `http://localhost:8081`).
- Invalid OpenAI key or quota issues → check `OPENAI_API_KEY`.

## License

This repository does not include an explicit license here; add a `LICENSE` file if you need a clear license (for example MIT).

---

If you want, I can: add an `ai-writing-assistant-server/.env.example` with the minimal variables, add more request examples (SSE, complex payloads), or provide an English/Portuguese translation for other docs.
