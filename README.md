# AI HomeGuard

AI HomeGuard is a local-first Blanzy Labs AI app for defensive home cyber hygiene. It helps home users understand and improve basic cybersecurity posture through safe local checks, plain-English risk explanations, and D3FEND-informed defensive guidance.

Repository: https://github.com/blanzy-labs/ai-homeguard

## Status

Current slice: Slice 2 - Finding Model, Report Model, and Demo Data.

This baseline includes the repository scaffold, FastAPI health/version endpoints, Pydantic finding/report models, static deterministic demo data, a React/Vite TypeScript demo dashboard, Docker Compose wiring, and project documentation. It does not include real audit checks yet.

The v0.1.0 target is the Local Home Security Audit MVP.

## Safety Boundaries

AI HomeGuard is a local-first defensive cyber hygiene tool. It does not exploit, attack, brute-force, packet-sniff, or scan public targets.

Slice 2 does not include:

- Network scanning
- Nmap integration
- Windows, macOS, or Linux security check logic
- OpenAI or other AI provider calls
- Live D3FEND mapping logic
- Telemetry, login, cloud storage, or database persistence

The demo dashboard uses fake sample findings only. D3FEND-informed guidance is currently static demo content, and optional ATT&CK context is educational only.

See [docs/disclaimer.md](docs/disclaimer.md) and [docs/security-and-privacy.md](docs/security-and-privacy.md).

## Demo API

Slice 2 adds a deterministic demo report endpoint:

```bash
curl http://localhost:8000/demo/report
```

Additional aliases:

- `GET /demo/findings`
- `GET /reports/demo`

These endpoints return static fake data. They do not run local commands, inspect the device, scan the network, call an AI provider, or persist data.

## Local Install

Prerequisites:

- git
- uv
- Node.js
- pnpm
- Docker Desktop with Docker Compose

Clone:

```bash
git clone https://github.com/blanzy-labs/ai-homeguard.git
cd ai-homeguard
```

Backend:

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
pnpm install
pnpm dev
```

Docker:

```bash
docker compose build
docker compose up -d
```

Expected URLs:

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Health: http://localhost:8000/health
- Version: http://localhost:8000/version
- Demo report: http://localhost:8000/demo/report
- API docs: http://localhost:8000/docs

## Development Commands

Backend tests:

```bash
cd backend
uv run pytest
```

Frontend build:

```bash
cd frontend
pnpm build
```

Docker smoke test:

```bash
docker compose up -d
curl http://localhost:8000/health
curl http://localhost:8000/version
curl http://localhost:8000/demo/report
docker compose down
```

## Documentation

- [Architecture](docs/architecture.md)
- [Local Install](docs/local-install.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Release Checklist](docs/release-checklist.md)
- [Disclaimer](docs/disclaimer.md)
- [Security and Privacy](docs/security-and-privacy.md)
- [Slice 1 Prerequisite Validation](docs/validation/slice-1-prerequisites.md)
- [Slice 2 Validation](docs/validation/slice-2-validation.md)

## License

MIT. See [LICENSE](LICENSE).
