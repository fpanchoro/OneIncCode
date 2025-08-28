
up:
	docker compose up --build

down:
	docker compose down --volumes --remove-orphans

restart:
	docker compose down --volumes --remove-orphans
	sleep 2
	docker compose up --build

logs:
	docker compose logs -f

ps:
	docker compose psSHELL := /bin/bash
.PHONY: build up down logs test test-docker test-exec test-local frontend-build help

## Build both services using Docker Compose
build:
	docker compose build

## Bring up the full stack (compose)
up:
	docker compose up --build

## Stop and remove containers, networks, volumes
down:
	docker compose down --volumes --remove-orphans

## Follow logs for all services
logs:
	docker compose logs -f

## Run backend tests inside a temporary container (fresh environment)
test-docker:
	docker compose run --rm api pytest -q

## Run backend tests in a running api container (container must be running)
test-exec:
	docker compose exec api pytest -q

## Run backend tests locally without Docker (requires local Python env)
test-local:
	cd ai-writing-assistant-server && pytest -q

## Build frontend production assets
frontend-build:
	cd style-rewriter && npm ci && npm run build

## Default: show help
help:
	@echo "Makefile targets:"
	@echo "  make build           # docker compose build"
	@echo "  make up              # docker compose up --build"
	@echo "  make down            # docker compose down --volumes --remove-orphans"
	@echo "  make logs            # docker compose logs -f"
	@echo "  make test-docker     # run pytest in a fresh api container"
	@echo "  make test-exec       # run pytest in running api container"
	@echo "  make test-local      # run pytest locally (requires Python env)"
	@echo "  make frontend-build  # build frontend assets"
