# Local Install

## Prerequisites

- macOS, Linux, or Windows with a supported development shell
- git
- uv
- Python available through uv
- Node.js
- pnpm
- Docker Desktop or Docker Engine with Docker Compose

## Clone

```bash
git clone https://github.com/blanzy-labs/ai-homeguard.git
cd ai-homeguard
```

## Backend

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

Backend URLs:

- http://localhost:8000
- http://localhost:8000/health
- http://localhost:8000/version
- http://localhost:8000/docs

## Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

Frontend URL:

- http://localhost:5173

## Docker

```bash
docker compose build
docker compose up -d
```

Expected URLs:

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Health: http://localhost:8000/health
- Version: http://localhost:8000/version
- Runtime context: http://localhost:8000/runtime
- Guidance catalog: http://localhost:8000/knowledge/d3fend-guidance
- Local device report: http://localhost:8000/reports/local-device
- Combined report: http://localhost:8000/reports/combined
- Markdown export: http://localhost:8000/reports/export/markdown
- JSON export: http://localhost:8000/reports/export/json
- Windows local report: http://localhost:8000/reports/windows-local
- macOS local report: http://localhost:8000/reports/macos-local
- Linux local report: http://localhost:8000/reports/linux-local
- API docs: http://localhost:8000/docs

Docker note: Docker runs the backend inside a Linux container. `/reports/local-device` reflects the backend runtime, so Docker results may describe the container instead of the host. For true host macOS checks, run the backend directly with uv instead of Docker.

Stop Docker services:

```bash
docker compose down
```
