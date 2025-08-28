PROJECT DESCRIPTION — OneInc (AI Writing Assistant + Style Rewriter)

Summary

This document consolidates, in detail and outside the project folders, all changes, additions, and validations performed in the repository during the session. It also includes run instructions, verification steps, and the current status of code and tests.

Original goals

- Review and ensure the server (`ai-writing-assistant-server`) runs correctly and the agent executes as expected.
- Ensure everything can run in Docker (frontend + backend stack).
- Add and document unit/integration tests and verify they pass.
- Clean the frontend (`style-rewriter`) by removing branding references and update documentation.
- Provide clear READMEs (backend, frontend, and root) and supporting files for publishing to GitHub.

Detailed actions performed

1) Documentation (README)
- Created or updated the following READMEs in English for clarity and consistency:
  - `README.md` (root) — instructions for running both services via Docker Compose, per-service development instructions, Docker test commands, healthcheck examples, and troubleshooting notes.
  - `ai-writing-assistant-server/README.md` — full backend guide: environment variables, run with Docker or locally, endpoints (`/v1/agent`, `/v1/agent/stream`, `/v1/rephrase`), and tests.
  - `style-rewriter/README.md` — frontend guide: development (Vite), build, Docker usage, and proxy/CORS notes.

  Purpose: allow any developer to clone the repo and start the stack or run services individually.

2) Repository hygiene for GitHub
- `.gitignore` (root) — added to ignore common artifacts (node_modules, dist, .env, venv, .pyc, logs, etc.) and frontend-specific entries.
- `LICENSE` (root) — added MIT license.
- `ai-writing-assistant-server/.env.example` — example environment variables to guide creating a real `.env`.

  Purpose: prepare the repo for public hosting and prevent secrets from being committed.

3) Continuous Integration
- `.github/workflows/ci.yml` — GitHub Actions workflow with two jobs:
  - `backend-tests`: installs Python deps and runs `pytest -q` in `ai-writing-assistant-server` (uses `OPENAI_API_KEY` from secrets if required).
  - `frontend-build`: sets up Node and builds the frontend using `npm ci` and `npm run build`.

  Purpose: automatically validate tests and build on push/PR.

4) Makefile and convenience commands
- `Makefile` (root) — added targets:
  - `make build`, `make up`, `make down`, `make logs`
  - `make test-docker` (runs `docker compose run --rm api pytest -q`)
  - `make test-exec` (runs `docker compose exec api pytest -q`)
  - `make test-local` (runs `pytest -q` locally from the backend)
  - `make frontend-build` (builds frontend assets)

  Purpose: standardize common commands and simplify local development and CI.

5) Tests and validation
- Backend tests were executed inside Docker:

  - Example command used:

    ```bash
    docker compose run --rm api pytest -q
    ```

  - Result: 18 passed (all tests in `ai-writing-assistant-server/tests/` passed successfully).

  Purpose: confirm that backend unit and integration tests pass in a container environment.

6) Frontend: cleanup and build
- `style-rewriter/index.html` and related files were reviewed to remove branding references, and `style-rewriter/README.md` was updated.
- `style-rewriter/nginx.conf` was adjusted to use runtime DNS resolution to avoid Nginx errors like "host not found in upstream" when Docker Compose manages services.

  Purpose: remove unwanted branding and ensure Nginx can resolve the backend when deployed with Docker Compose.

7) Docker Compose and architecture
- The top-level `docker-compose.yml` defines at least two services:
  - `api` (built from `./ai-writing-assistant-server`) exposing the backend on container port 8000 and mapped to `8081:8000` on the host.
  - `web` (built from `./style-rewriter`) serving the frontend build via Nginx and mapped to `8080:80` on the host.
- A healthcheck for `api` is implemented (endpoint `/healthz`).

  Purpose: run the full stack (frontend + backend + proxy) reproducibly.

8) Minor code changes
- The provider/service/test structure was preserved; no disruptive changes were made to the agent logic in this phase — the focus was documentation, CI, and packaging.

## Technical Architecture Details

### Backend Architecture (`ai-writing-assistant-server`)

1. Core Components

- **Entry Point**: `app/main.py`
  - FastAPI application setup
  - CORS middleware configuration
  - Health check endpoints (`/health`, `/healthz`)
  - Route registration

- **Routes** (`app/routes/`)
  - `agent.py`: Agent endpoints for full responses and streaming
    - POST `/v1/agent`: Run agent with style rephrasing
    - POST `/v1/agent/stream`: SSE streaming endpoint
  - `rephrase.py`: Core rephrasing endpoints
    - POST `/v1/rephrase`: Basic text rephrasing

2. Provider Architecture (`app/providers/`)

- **Base Provider** (`base.py`)
  - Abstract base class `LLMProvider` defining the provider interface
  - Methods: `rephrase_full()`, `rephrase_stream()`

- **Provider Implementations**:
  - `openai_chat.py`: OpenAI Chat API implementation
    - Handles message formatting and API calls
    - Supports both full responses and streaming
  - `mock_provider.py`: Mock implementation for testing
    - Returns predefined responses
    - Useful for development without API keys
  - `agent_provider.py`: Smart provider with fallback
    - Primary: tries OpenAI Agents SDK
    - Fallback: uses OpenAIChatProvider or MockProvider

3. Services (`app/services/`)

- **Rephrase Service** (`rephrase_service.py`)
  - Orchestrates provider calls
  - Handles style validation
  - Manages response formatting

4. Data Models (`app/schemas.py`)

- Request/Response Pydantic models
- Input validation
- Response formatting

5. Configuration (`app/config.py`)

- Environment variable handling
- CORS configuration
- API settings

6. Testing Architecture (`tests/`)

- **Integration Tests**:
  - `test_routes_integration.py`: Full API endpoint testing
  - `test_routes_mock.py`: Route testing with mock provider

- **Unit Tests**:
  - `test_providers.py`: Provider implementation tests
  - `test_services.py`: Service layer logic tests
  - `test_prompts.py`: Prompt formatting tests

### Frontend Architecture (`style-rewriter`)

1. Core Application

- **Entry Point**: `src/main.tsx`
  - React application setup
  - Global styles and providers

- **Main App**: `src/App.tsx`
  - Layout and routing
  - Theme provider setup

2. Component Structure (`src/components/`)

- **Main Components**:
  - `RealtimeChat.tsx`: SSE streaming interface
  - `StyleOutput.tsx`: Styled output display
  - `TextRephraser.tsx`: Text input and style selection

- **UI Components** (`components/ui/`):
  - Shadcn UI components (buttons, inputs, etc.)
  - Custom styled components

3. State and API (`src/lib/`)

- **API Client** (`api.ts`):
  - Backend API integration
  - Request/response handling

- **Real-time Client** (`realtime-client.ts`):
  - SSE connection management
  - Stream processing

4. Routing and Pages (`src/pages/`)

- `Index.tsx`: Main application page
- `RealtimePage.tsx`: Streaming interface
- `NotFound.tsx`: 404 handler

5. Custom Hooks (`src/hooks/`)

- `use-mobile.tsx`: Responsive design utilities
- `use-toast.ts`: Toast notification system

### Docker and Deployment Architecture

1. Backend Container

- Base: Python 3.11 slim
- Exposed port: 8000
- Environment:
  - OPENAI_API_KEY
  - OPENAI_MODEL
  - CORS_ORIGINS
  - SERVER_HOST/PORT

2. Frontend Container

- Build stage: Node 18
- Runtime: Nginx Alpine
- Configuration:
  - Runtime DNS resolution
  - API proxy setup
  - Static file serving

3. Docker Compose Stack

- Services:
  - `api`: Backend FastAPI service
  - `web`: Frontend + Nginx proxy
- Features:
  - Health checks
  - Service dependencies
  - Volume management

### API Flow and Data Model

1. Request Flow

```
Client → Nginx → FastAPI → Provider → OpenAI/Mock → Response
```

2. Key Data Structures

- Rephrase Request:
  ```json
  {
    "input_text": "text to rephrase",
    "styles": ["professional", "casual"]
  }
  ```

- Response Format:
  ```json
  {
    "request_id": "uuid",
    "results": {
      "professional": "rephrased text",
      "casual": "rephrased text"
    }
  }
  ```

3. Streaming Format (SSE)

- Event stream with chunked responses
- Each chunk contains partial completion
- Supports multiple simultaneous styles

### Development Workflow

1. Local Development

- Backend:
  ```bash
  cd ai-writing-assistant-server
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  uvicorn app.main:app --reload
  ```

- Frontend:
  ```bash
  cd style-rewriter
  npm install
  npm run dev
  ```

2. Testing Flow

- Backend tests:
  ```bash
  make test-docker  # fresh container
  make test-exec    # running container
  ```

- Frontend build verification:
  ```bash
  make frontend-build
  ```

3. CI/CD Pipeline

- On push/PR:
  1. Run backend tests
  2. Build frontend
  3. Check build artifacts
  4. Verify Docker builds

### Security Considerations

1. API Security
- CORS configuration
- Environment variable protection
- No secrets in version control

2. Docker Security
- Multi-stage builds
- Minimal base images
- Non-root users

3. Development Security
- `.env.example` templates
- `.gitignore` patterns
- CI secret management

### Monitoring and Health Checks

1. Health Endpoints
- `/health` - Basic API health
- `/healthz` - Docker health check

2. Docker Health Checks
- API service checked every 10s
- 5 retries before marking unhealthy

3. Logging
- Docker compose logs
- Application-level logging
- Build and test logs

Files added / modified (summary with purpose)

- `README.md` (root) — run instructions, Makefile usage, CI badge guide.
- `ai-writing-assistant-server/README.md` — backend docs, env vars, endpoints.
- `style-rewriter/README.md` — frontend docs.
- `.gitignore` — ignore local artifacts and dependencies.
- `LICENSE` — MIT license.
- `ai-writing-assistant-server/.env.example` — example env variables.
- `.github/workflows/ci.yml` — CI workflow (backend pytest + frontend build).
- `Makefile` — convenience commands.

How to run and validate (quick summary)

1) Start the full stack with Docker Compose (from repo root):

```bash
make build
make up
# or
# docker compose build
# docker compose up --build
```

Frontend: open http://localhost:8090
Backend: API available at http://localhost:8081 (per compose mappings)

2) Run backend tests in Docker (recommended):

```bash
# from repo root
make test-docker
# or directly
docker compose run --rm api pytest -q
```

3) Run tests in an already-running container:

```bash
docker compose up --build -d
docker compose exec api pytest -q
```

4) Run backend locally without Docker (requires Python installed):

```bash
cd ai-writing-assistant-server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q   # run tests
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload  # start server
```

Security notes and GitHub publishing

- Do not commit `ai-writing-assistant-server/.env` or the `OPENAI_API_KEY` to GitHub. Add `OPENAI_API_KEY` to the repository's Secrets in GitHub Settings for CI.
- The root `.gitignore` includes entries to prevent committing `node_modules`, build artifacts, and `.env` files.
- The CI workflow references `${{ secrets.OPENAI_API_KEY }}` where needed; ensure required secrets are added before enabling CI for PRs.

Recommendations and next steps (prioritized)

1. Add the CI badge in the root README to show build/test status.
2. Add a `CONTRIBUTING.md` with code style, testing, and branching guidelines.
3. Add frontend tests (Vitest/Jest) and enable them in CI.
4. Review `nginx.conf` in `style-rewriter` if additional proxy tweaks are needed for SSE/streaming.
5. (Optional) Add a Postman/HTTPie collection with example requests and expected responses.

Validation log

- Backend tests (Docker): `docker compose run --rm api pytest -q` → `18 passed` in ~12s.
- Build: `docker compose build` and `docker compose up --build` used to validate that the stack starts (logs showed api and web started and healthcheck OK).

Contact / assistance

If you'd like, I can:
- Add the CI badge to `README.md` if you provide the repository owner/name (OWNER/REPO).
- Add `CONTRIBUTING.md` and PR/Issue templates.
- Add frontend tests and configure CI to run them.

