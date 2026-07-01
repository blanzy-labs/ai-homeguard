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
- API docs: http://localhost:8000/docs

Stop Docker services:

```bash
docker compose down
```
