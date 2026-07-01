# Slice 6 Validation

Date: 2026-07-01

Local project path: `/Users/robmythadis.com/dev/blanzy-labs/ai-homeguard`

## Scope

Slice 6 adds Unified Local Audit Report and Platform Auto-Detection: a privacy-safe runtime context model, runtime detection helpers, `/runtime`, `/reports/local-device`, a unified local runner that dispatches to one matching platform runner, frontend primary Local Device Audit flow, and docs.

This slice does not add new deep security checks. It reuses the existing Windows, macOS, and Linux local audit foundations.

## Pre-Change Repo State

- `pwd`: `/Users/robmythadis.com/dev/blanzy-labs/ai-homeguard`
- Branch: `main`
- Remote: `https://github.com/blanzy-labs/ai-homeguard.git`
- Starting working tree: clean

Baseline validation before Slice 6 changes:

- `cd backend && uv run pytest`: passed, 72 tests passed, 1 upstream `TestClient` deprecation warning
- `cd frontend && pnpm build`: passed
- `docker compose build`: passed

## Validation Commands

Backend:

```bash
cd backend
uv run pytest
```

Frontend:

```bash
cd frontend
pnpm build
```

Docker:

```bash
docker compose build
docker compose up -d
curl http://localhost:8000/health
curl http://localhost:8000/version
curl http://localhost:8000/runtime
curl http://localhost:8000/reports/local-device
curl http://localhost:8000/reports/macos-local
curl http://localhost:8000/reports/linux-local
curl http://localhost:8000/reports/windows-local
docker compose down
```

Native Mac Mini spot checks:

```bash
cd backend
uv run python -c 'from app.core.platform import get_runtime_context; print(get_runtime_context().model_dump_json())'
uv run python -c 'from app.checks.local_runner import run_local_device_audit; r=run_local_device_audit(); print(r.summary.model_dump_json()); print(r.runtime_context.model_dump_json() if r.runtime_context else None)'
```

Repository hygiene:

```bash
git diff --check
```

Safety review:

- Confirm no network scanning code
- Confirm no Nmap integration
- Confirm no ClamAV file scan calls
- Confirm no OpenAI or AI provider calls
- Confirm no telemetry
- Confirm no database or persistence
- Confirm no remediation/settings-change commands
- Confirm no packet capture
- Confirm no sudo/admin escalation commands
- Confirm runtime context avoids usernames, hostname strings, personal paths, environment variables, and secrets
- Confirm unified runner calls only one matching platform runner
- Confirm Docker limitation is included and documented

Secret review:

```bash
rg -l --hidden --glob '!.git/**' --glob '!frontend/node_modules/**' --glob '!frontend/dist/**' --glob '!backend/.venv/**' 'OPENAI_API_KEY=|GEMINI_API_KEY=|sk-|ghp_|gho_|-----BEGIN .*PRIVATE KEY-----'
```

## Results

- `cd backend && uv run pytest`: passed, 86 tests passed, 1 upstream `TestClient` deprecation warning
- `cd frontend && pnpm build`: passed
- Frontend tests: not run because no frontend test setup exists yet
- `git diff --check`: passed
- Native runtime context check: passed; detected `macos` / `native`, architecture `arm64`, `hostname_present: true`, and did not expose the hostname string
- Native unified local audit invocation: passed; returned a macOS local report with 4 good, 1 review, 1 fix_soon, and 1 unable-to-check finding on this Mac Mini
- `docker compose build`: passed
- `docker compose up -d`: passed
- `curl http://localhost:8000/health`: returned `{"status":"ok","app":"AI HomeGuard"}`
- `curl http://localhost:8000/version`: returned app/version metadata for AI HomeGuard
- `curl http://localhost:8000/runtime`: returned `linux` / `docker`, architecture `aarch64`, `hostname_present: true`, and a container limitation note without exposing a hostname string
- `curl http://localhost:8000/reports/local-device`: returned mode `local`, Linux container findings, runtime context, and the container limitation note
- `curl http://localhost:8000/reports/macos-local`: returned unsupported-platform output because the Docker backend runtime is Linux
- `curl http://localhost:8000/reports/linux-local`: returned Linux findings from the Docker container environment
- `curl http://localhost:8000/reports/windows-local`: returned unsupported-platform output because the Docker backend runtime is Linux
- `docker compose down`: passed; validation containers removed
- Linux check behavior remains covered with mocked command output and does not require a real Linux host
- Windows behavior remains covered with mocked command output and does not require real PowerShell on the Mac
- Broad secret scan produced only false positives for `sk-` inside words such as `disk-encryption` plus documented scan commands; no real secrets were found
- Safety review passed: no Nmap, packet capture, exploit, credential, brute-force, telemetry, database, OpenAI, remediation, package update/install, sudo, or ClamAV file-scan command usage was found
- Runtime privacy review passed: runtime context returns hostname presence as a boolean and does not expose hostname strings, usernames, personal paths, environment variables, or secrets

## Safety Notes

- The unified runner dispatches to the matching Windows, macOS, or Linux runner only.
- Unknown platforms return `unable_to_check` without running platform-specific commands.
- No commands install software, change settings, start or stop services, update packages, scan files, scan networks, capture packets, upload data, or call an AI provider.
- Runtime context reports hostname presence as a boolean only and does not expose the hostname string.

## Known Warnings and Follow-ups

- FastAPI/Starlette emits an upstream `TestClient` deprecation warning during tests.
- Frontend test infrastructure has not been added yet.
- Real Windows and real Linux host smoke validation remain future environment-specific tasks.
- Recommended next slice: Slice 7 - Combined HomeGuard Report and Export Foundation.
