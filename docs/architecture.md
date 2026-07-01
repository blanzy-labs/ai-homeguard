# Architecture

AI HomeGuard uses a simple local-first web app structure.

## Current Slice 2 Components

- Backend: FastAPI app with `/health` and `/version`
- Models: Pydantic evidence, guidance, finding, summary, and report models
- Demo data: deterministic static `HomeGuardReport` returned by `/demo/report`
- Frontend: React, Vite, and TypeScript demo dashboard UI
- Docker: Docker Compose services for backend and frontend
- Docs: safety, privacy, install, troubleshooting, release, and validation notes

Slice 2 shapes the report and finding user experience with fake sample findings only. It does not include audit checks, platform security checks, network scanning, OpenAI calls, AI provider integrations, or live D3FEND mapping logic.

## Finding and Report Model

Findings are designed to support both home-user explanations and technical evidence. A finding includes:

- Status, severity, confidence, platform, and category
- Plain-English title, summary, impact explanation, and recommended action
- Evidence entries with source, method, observed value, expected value, and notes
- D3FEND-informed defensive guidance with home action, rationale, difficulty, and estimated time
- Optional ATT&CK context marked educational only

Reports wrap findings with a summary, top actions, platform scope, disclaimer, and safety notes.

## Demo Data Flow

```text
frontend dashboard -> GET /demo/report -> static HomeGuardReport
```

The backend route returns deterministic in-process demo data from `backend/app/demo/demo_report.py`. The route does not run local commands, call external services, scan networks, or persist data.

Future real checks should generate findings using the same model so the frontend can display local results without changing the user-facing report shape.

## Planned Modules

- `checks`: safe local checks for future audit slices
- `knowledge/D3FEND`: D3FEND-informed defensive guidance references
- `reports`: plain-English local report generation
- `questionnaire`: beginner-friendly user inputs and context
- `platform adapters`: Windows, macOS, and Linux check implementations

Future slices may add Windows, macOS, and Linux security checks. Those checks should stay defensive, local-first, and explicit about user authorization.
