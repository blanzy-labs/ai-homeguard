# Architecture

AI HomeGuard uses a simple local-first web app structure.

## Current Slice 1 Components

- Backend: FastAPI app with `/health` and `/version`
- Frontend: React, Vite, and TypeScript baseline UI
- Docker: Docker Compose services for backend and frontend
- Docs: safety, privacy, install, troubleshooting, release, and validation notes

Slice 1 is only the baseline scaffold. It does not include audit checks, platform security checks, network scanning, OpenAI calls, AI provider integrations, or D3FEND mapping logic.

## Planned Modules

- `checks`: safe local checks for future audit slices
- `knowledge/D3FEND`: D3FEND-informed defensive guidance references
- `reports`: plain-English local report generation
- `questionnaire`: beginner-friendly user inputs and context
- `platform adapters`: Windows, macOS, and Linux check implementations

Future slices may add Windows, macOS, and Linux security checks. Those checks should stay defensive, local-first, and explicit about user authorization.
