## Project Structure and Home Task Mapping

This repository implements all requirements of the [AI-enabled Software Engineer] Home Task: AI Writing Assistant. Below is a mapping of each requirement to the relevant code and folder:

| Requirement | Where Implemented |
|-------------|-------------------|
| **Frontend: React SPA** | `style-rewriter/` (Vite + React + TypeScript) |
| **Backend: FastAPI (Python)** | `ai-writing-assistant-server/` |
| **User enters text, clicks Process** | `style-rewriter/src/components/TextRephraser.tsx` |
| **LLM API call (OpenAI)** | `ai-writing-assistant-server/app/providers/openai_chat.py` |
| **Rephrased output in 4 styles** | `ai-writing-assistant-server/app/providers/openai_chat.py` (prompt logic), `style-rewriter/src/components/StyleOutput.tsx` |
| **Disable input while processing** | `style-rewriter/src/components/TextRephraser.tsx` |
| **Cancel button** | `style-rewriter/src/components/TextRephraser.tsx`, backend supports cancellation |
| **Streaming output** | Backend: `rephrase_stream` in `openai_chat.py`, Frontend: `RealtimeChat.tsx` |
| **Each style in its own area** | `StyleOutput.tsx` |
| **Clean, enterprise UI** | `style-rewriter/` (UI components, Tailwind, shadcn/ui) |
| **Modern framework features** | React hooks, TypeScript, async/await, FastAPI, etc. |
| **Modular backend/frontend** | Providers, services, routes, components, hooks |
| **Unit/integration tests** | `ai-writing-assistant-server/tests/` |
| **Backend containerized** | `ai-writing-assistant-server/Dockerfile`, `docker-compose.yml` |
| **Frontend containerized** | `style-rewriter/Dockerfile`, `docker-compose.yml` |
| **README and setup instructions** | This file, plus `ai-writing-assistant-server/README.md` and `style-rewriter/README.md` |

**All requirements and recommended features are fully implemented and documented.**
## Makefile usage

You can use the included `Makefile` for common tasks:

```
make up        # Start all services (build if needed)
make down      # Stop and remove all containers, networks, and volumes
make restart   # Stop everything, then start again (useful if ports are stuck)
make logs      # Follow logs for all services
make ps        # List running containers and port mappings
```

# OneInc — Full Stack (AI Writing Assistant + Style Rewriter)

This repository contains two main services:

- `ai-writing-assistant-server/` — FastAPI backend that provides text rephrasing, an agent, and provider adapters (OpenAI, mock, etc.).
- `style-rewriter/` — Vite + React frontend that serves the UI and proxies rephrase requests to the backend.


## Code Quality, Security, and Best Practices

This project is standardized for code quality and security:

- **Python backend**:
  - Auto-formatting with `black` and import sorting with `isort`.
  - Linting and style checks with `flake8`.
  - Security scanning with `bandit`.
  - All dependencies are pinned in `requirements.txt` and checked for vulnerabilities.
- **Frontend (React/TypeScript)**:
  - Linting and code style enforced with ESLint (modern config in `eslint.config.js`).
  - Auto-formatting with Prettier.
  - All dependencies are checked with `npm audit`.

To run all code quality and security checks:

**Backend:**
```bash
cd ai-writing-assistant-server
source .venv/bin/activate
black . && isort .
flake8 .
bandit -r .
```

**Frontend:**
```bash
cd style-rewriter
npm install
npx eslint src --fix
npx prettier --write src
npm audit --audit-level=high
```

All code is formatted, linted, and scanned for security issues. Please review and address any warnings, especially those flagged by `bandit` as medium/high severity.

---

The rest of this README explains how to run both services together (recommended) and how to run them individually for development and testing.

## Checklist (what this README covers)

- Run both services together using Docker Compose.
- Run backend and frontend individually for development.
- Run unit tests for the backend and guidance for frontend tests.
- Common troubleshooting notes and next steps.

## Run both services (recommended)

From the repository root, use Docker Compose to build and start both services in containers:

```bash
docker compose build
docker compose up --build
```

This will start the services defined in the top-level `docker-compose.yml`. Use `docker compose logs -f` to follow logs and `docker compose down --volumes --remove-orphans` to stop and clean up.


**Frontend URL:**

After running `docker compose up`, the frontend will be available at: [http://localhost:8090](http://localhost:8090)

Note: Port mappings and other runtime settings are defined in `docker-compose.yml`. If you need to confirm which host ports are used, inspect the compose file or run:

```bash
docker compose ps
```

## Makefile (convenience)

This repo includes a `Makefile` with shortcuts for common tasks. From the repo root you can run:

```bash
make build         # docker compose build
make up            # docker compose up --build
make down          # docker compose down --volumes --remove-orphans
make logs          # follow logs
make test-docker   # run backend tests in a temporary api container
make test-exec     # run backend tests inside a running api container
make frontend-build# build frontend assets
```

Using `make` simplifies CI scripts and local development.

## CI badge (optional)

We added a GitHub Actions workflow at `.github/workflows/ci.yml`. To display a CI status badge in this README, add the following Markdown and replace `OWNER` and `REPO` with the GitHub owner and repository name:

```markdown
[![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/ci.yml)
```

Also ensure `OPENAI_API_KEY` (and any other secrets) are configured in the repository's GitHub Settings → Secrets so the backend tests can run in CI.

## Run services individually

Backend (FastAPI)

```bash
cd ai-writing-assistant-server
# (optional) create .env or copy .env.example if present
# run in Docker (recommended):
# docker compose up --build (from repo root)

# or run locally without Docker:
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Frontend (Vite + React)

```bash
cd style-rewriter
npm install
# run development server:
npm run dev
# build for production:
npm run build
# serve the built site locally (optional):
# npx serve dist
```

If the frontend proxies API calls to the backend (via Nginx), make sure the backend is reachable at the address expected by the frontend (check `style-rewriter/nginx.conf` or the frontend config).

## Run tests

Backend tests (pytest)

The backend includes unit and integration tests. Run them from the backend directory:

```bash
cd ai-writing-assistant-server
pytest -q
```

You can also run the backend test suite inside Docker using the `api` service defined in the top-level `docker-compose.yml` (this is useful for CI or to match the runtime environment).

- If the compose stack is already running, run the tests inside the running container:

```bash
docker compose exec api pytest -q
```

- If the stack is not running (or you prefer a fresh container), run:

```bash
docker compose run --rm api pytest -q
```

Both commands execute the `pytest` command inside the `api` service container (the backend). The `exec` form requires a running container; the `run` form starts a temporary container and removes it after tests finish.

This runs the test suite that exercises providers, services, and routes. If you are running tests inside CI or want reproducibility, run the tests inside a container or in a clean virtual environment.

Frontend tests

If the `style-rewriter` contains any test scripts, you can run them with npm. From the frontend directory:

```bash
cd style-rewriter
npm install
# if a test script exists in package.json
npm test
```

If no test script is present, you can run build and smoke-test the output with `npm run build` and serve the build locally.

## Quick health checks (examples)

After starting the stack via Docker Compose you can sanity-check the services with curl. Replace host/port according to your `docker-compose.yml` mappings.

```bash

# Example: check frontend root
curl -sS -D - http://localhost:8090/ | sed -n '1,20p'

# Example: call a backend endpoint (adjust port if needed)
curl -s -X POST http://localhost:8081/v1/agent \
  -H "Content-Type: application/json" \
  -d '{"input_text":"Hello from curl","styles":["professional"]}' | jq
```

## Environment variables and secrets

- The backend expects a `.env` file inside `ai-writing-assistant-server/` with variables like `OPENAI_API_KEY`, `OPENAI_MODEL`, `CORS_ORIGINS`, `SERVER_HOST`, `SERVER_PORT`.
- Never commit secret keys to version control. Use `.env.example` and .gitignore to avoid exposing secrets.

## Troubleshooting

- Nginx "host not found in upstream" — ensure runtime DNS resolution is enabled in `style-rewriter/nginx.conf` or confirm service names/networks in `docker-compose.yml`.
- CORS errors — update `CORS_ORIGINS` in `ai-writing-assistant-server/.env` to include your frontend origin (e.g. `http://localhost:8081`).
- OpenAI auth errors — verify `OPENAI_API_KEY` and quota/permissions.

## Next steps / Enhancements

- Add `ai-writing-assistant-server/.env.example` with minimal variables.
- Add CI configuration to run `pytest` and frontend tests on each push.
- Add more detailed API docs or example Postman collection.

---

If you want, I can now create a `.env.example` for the backend and add a short `Makefile` with common commands (build, up, test). Which would you prefer next?
