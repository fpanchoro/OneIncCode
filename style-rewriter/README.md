## Makefile usage

From the repository root, you can use the `Makefile` for common Docker Compose tasks:

```
make up        # Start all services (build if needed)
make down      # Stop and remove all containers, networks, and volumes
make restart   # Stop everything, then start again (useful if ports are stuck)
make logs      # Follow logs for all services
make ps        # List running containers and port mappings
```

# Text Rephraser AI - Frontend Demo

Transform your text into different writing styles using a simulated AI interface. Perfect for showcasing professional communication, casual conversations, polite messaging, and social media content formats.

## 🚀 Quick Start

# Text Rephraser - Frontend

Lightweight React frontend for demonstrating text rephrasing across multiple styles.

## Quick Start

Prerequisites:
- Node.js 18+
- npm or bun

Development:

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```
# Style Rewriter (Frontend)

Vite + React frontend for the Style Rewriter demo. The app provides a UI to send text to the backend rephrase/agent endpoints and display styled results.

## What it does

- Simple UI to enter text, choose styles, and view rephrased output.
- Uses streaming and animated text to approximate a live AI experience.
- Intended to be served behind Nginx (the repo includes an nginx config for production builds).

## Requirements

- Node.js 18+ and npm
- Docker & Docker Compose (recommended for running whole stack)

## Quick start (development)

```bash
cd style-rewriter
npm install
npm run dev

# open http://localhost:8081 (Vite default) or check the dev server output
```

## Build for production

```bash
cd style-rewriter
npm install
npm run build

# the production files will be generated in `dist/`
```

## Run with Docker (as part of the full stack)

The repository includes a top-level `docker-compose.yml` that builds both the backend and frontend and runs Nginx to serve the built frontend and proxy API requests.

From the repo root:

```bash
docker compose build
docker compose up --build
```


The frontend will be available at [http://localhost:8090](http://localhost:8090) (see top-level compose for host port mappings).

## Environment / Proxy

- The frontend's Nginx configuration is in `style-rewriter/nginx.conf`. It proxies `/v1/rephrase` or other API paths to the backend service. If running frontend and backend separately, ensure the backend is reachable at the address expected by the nginx config or the frontend.

## Tests

If the frontend includes tests, run them with npm from the `style-rewriter` directory:

```bash
cd style-rewriter
npm install
npm test
```

If no test scripts are present, build and smoke-test the output with `npm run build` and serve the `dist/` folder locally.

## Project structure

- `src/` - React source (components, hooks, pages)
- `public/` - Static assets
- `Dockerfile`, `nginx.conf` - Container + proxy config

## Notes

- All references to previous branding have been removed from meta tags and docs.
- Adjust `CORS` origins on the backend (`ai-writing-assistant-server/.env`) if you run frontend and backend on different origins.

## Contributing

Run the dev server, make changes locally, and open a PR. Follow the same code style and tests where applicable.

---

If you'd like, I can add a simple `npm test` configuration (Jest or Vitest) and a small smoke test for the frontend build.

