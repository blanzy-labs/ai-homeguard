# Slice 4 Validation

Date: 2026-07-01

Local project path: `/Users/robmythadis.com/dev/blanzy-labs/ai-homeguard`

## Scope

Slice 4 adds the Windows Local Checks Foundation: platform detection, safe command runner, read-only Windows check modules, Windows local audit report route, mocked tests, and frontend support for a Windows Device Audit mode.

The developer machine is a Mac Mini, so validation confirms unsupported-platform behavior locally and uses mocked command output for Windows-specific mapping tests.

## Pre-Change Repo State

- `pwd`: `/Users/robmythadis.com/dev/blanzy-labs/ai-homeguard`
- Branch: `main`
- Remote: `https://github.com/blanzy-labs/ai-homeguard.git`
- Starting working tree: clean
- Existing Docker stack was stopped before Slice 4 implementation validation

Baseline validation before Slice 4 changes:

- `cd backend && uv run pytest`: passed, 18 tests passed, 1 upstream `TestClient` deprecation warning
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
curl http://localhost:8000/reports/windows-local
docker compose down
```

Repository hygiene:

```bash
git diff --check
```

Safety review:

- Confirm no network scanning code
- Confirm no scanner integrations
- Confirm no ClamAV calls
- Confirm no OpenAI calls
- Confirm no telemetry
- Confirm no database or persistence
- Confirm no remediation/settings-change commands
- Confirm no packet capture
- Confirm Windows commands are read-only
- Confirm Windows commands only run on Windows
- Confirm tests do not run real PowerShell
- Confirm user-facing output does not expose full local admin usernames

Secret review:

```bash
rg -l --hidden --glob '!.git/**' --glob '!frontend/node_modules/**' --glob '!frontend/dist/**' --glob '!backend/.venv/**' '<known API key prefixes or private key markers>'
```

## Results

- `cd backend && uv run pytest`: passed, 36 tests passed, 1 upstream `TestClient` deprecation warning
- `cd frontend && pnpm build`: passed
- Frontend tests: not run because no frontend test setup exists yet
- `docker compose build`: passed
- `docker compose up -d`: passed
- `curl http://localhost:8000/health`: returned `{"status":"ok","app":"AI HomeGuard"}`
- `curl http://localhost:8000/version`: returned app/version metadata for AI HomeGuard
- `curl http://localhost:8000/reports/windows-local`: returned mode `local`, overall status `unable_to_check`, finding `windows-local-audit-unsupported-platform`, and evidence note `No Windows commands were run on this platform.`
- `docker compose down`: passed; validation containers removed
- `git diff --check`: passed
- Secret review: passed; no paths found for obvious API key prefixes or private key markers
- Safety review: passed; no scanner integrations, ClamAV calls, OpenAI calls, telemetry implementation, database implementation, persistence, packet capture, or remediation/settings-change commands found
- Command runner review: `subprocess.run` appears only in `backend/app/core/command_runner.py`, uses `shell=False`, command allowlisting, timeout support, captured output, and platform guarding
- Windows command review: Windows command strings are read-only status/selection commands; no `Set-*`, `Enable-*`, `Disable-*`, `Remove-*`, service start/stop/restart, or BitLocker enable/disable command strings found
- Test review: Windows tests use mocked command output and do not run real PowerShell
- Privacy review: local administrator tests verify full names are not exposed in user-facing output

## Known Warnings and Follow-ups

- FastAPI/Starlette emits an upstream `TestClient` deprecation warning during tests.
- Frontend test infrastructure has not been added yet.
- Windows command behavior is validated with mocked command output on this Mac. Real Windows smoke validation is a future environment-specific task.
