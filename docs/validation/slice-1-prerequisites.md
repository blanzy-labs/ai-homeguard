# Slice 1 Prerequisites Validation

Date: 2026-07-01

Local project path: `/Users/robmythadis.com/dev/blanzy-labs/ai-homeguard`

## Tool Report

| Tool | Required | Detected version/status | Action taken | Remaining manual action |
| --- | --- | --- | --- | --- |
| macOS | Yes | macOS 26.5.1, build 25F80 | Confirmed | None |
| Architecture | Yes | arm64 | Confirmed | None |
| git | Yes | git version 2.54.0 | Confirmed | None |
| gh | Yes | gh version 2.94.0 | Confirmed | None |
| Docker / Docker Desktop | Yes | Docker CLI 29.5.3; daemon 29.5.3 running | Confirmed after Docker Desktop was started | None |
| docker compose | Yes | Docker Compose v5.1.4 | Confirmed | None |
| uv | Yes | uv 0.11.24 | Confirmed | None |
| Python through uv | Yes | cpython 3.13.14 and 3.14.4 available locally; backend pinned to 3.13 | Confirmed | None |
| node | Yes | v24.18.0 | Confirmed | None |
| pnpm | Yes | 11.9.0 | Confirmed | None |
| npm | Yes | 11.16.0 | Confirmed | None |
| curl | Yes | curl 8.7.1 | Confirmed | None |
| jq | Yes | jq-1.7.1-apple | Confirmed | None |
| nmap | Optional | Not installed | Deferred | Optional future install only if needed |
| clamav / clamscan | Optional | Not installed | Deferred | Optional future install only if needed |
| pwsh / PowerShell | Optional | Not installed | Deferred | Optional future install only if needed |
| shellcheck | Optional | Not installed | Deferred | Optional future install only if needed |

No prerequisite tools were installed during Slice 1.

## GitHub Auth Status

GitHub CLI is authenticated to `github.com` as `blanzy-labs` with repo access. The target owner path matches the authenticated account. The repository operation succeeded at `https://github.com/blanzy-labs/ai-homeguard`.

## Repository Status

- Target repository did not exist before Slice 1.
- Created repository: `blanzy-labs/ai-homeguard`
- Visibility: public
- Local path: `/Users/robmythadis.com/dev/blanzy-labs/ai-homeguard`
- Remote: `https://github.com/blanzy-labs/ai-homeguard.git`
- Local default branch prepared as `main`
- Topics requested: `blanzy-labs`, `ai`, `llm`, `local-first`, `fastapi`, `react`, `vite`, `docker`, `home-security`, `cybersecurity`, `d3fend`

## Validation Commands

Backend:

```bash
cd backend
uv sync
uv run pytest
```

Frontend:

```bash
cd frontend
pnpm install
pnpm build
```

Docker:

```bash
docker compose build
docker compose up -d
curl http://localhost:8000/health
curl http://localhost:8000/version
docker compose down
```

Repository hygiene:

```bash
git diff --check
```

Secret review:

```bash
rg -l --hidden --glob '!.git/**' --glob '!frontend/node_modules/**' --glob '!frontend/dist/**' --glob '!backend/.venv/**' '<known API key prefixes or private key markers>'
```

## Validation Results

- `uv sync`: passed using CPython 3.13.14; generated `backend/uv.lock`
- `uv run pytest`: passed, 2 tests collected, 2 passed; one upstream Starlette/FastAPI `TestClient` deprecation warning observed
- `pnpm install`: passed using pnpm 11.9.0; generated `frontend/pnpm-lock.yaml`
- `pnpm build`: passed; TypeScript no-emit check and Vite production build completed
- `docker compose build`: passed
- `docker compose up -d`: passed
- `curl http://localhost:8000/health`: returned `{"status":"ok","app":"AI HomeGuard"}`
- `curl http://localhost:8000/version`: returned `{"app":"AI HomeGuard","repo":"ai-homeguard","version":"0.1.0-dev","family":"Blanzy Labs"}`
- `docker compose down`: passed
- `git diff --check`: passed
- Secret review: passed after checking known API key prefixes and private key markers; no real secrets found

Docker note: the first Docker image pull attempt stalled through the default Docker credential path. Public base images were pulled successfully with a temporary empty `DOCKER_CONFIG`, and plain `docker compose build` passed after the base images were cached.

## Manual Follow-ups

- Optional: review the local Docker credential helper if future uncached pulls stall in the same way.
