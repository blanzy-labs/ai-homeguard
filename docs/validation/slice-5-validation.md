# Slice 5 Validation

Date: 2026-07-01

Local project path: `/Users/robmythadis.com/dev/blanzy-labs/ai-homeguard`

## Scope

Slice 5 adds the macOS and Linux Local Checks Foundation: platform-specific check modules, read-only allowlisted command runners, report aggregators, API routes, mocked tests, frontend local audit options, and documentation.

The developer machine is a Mac Mini. macOS checks may run locally when the backend runs natively. Linux behavior is validated with mocked tests, and `/reports/linux-local` returns unsupported-platform output on the Mac native backend. Docker runs the backend inside a Linux container, so Docker Linux results reflect the container, not the Mac host.

## Pre-Change Repo State

- `pwd`: `/Users/robmythadis.com/dev/blanzy-labs/ai-homeguard`
- Branch: `main`
- Remote: `https://github.com/blanzy-labs/ai-homeguard.git`
- Starting working tree: clean

Baseline validation before Slice 5 changes:

- `cd backend && uv run pytest`: passed, 36 tests passed, 1 upstream `TestClient` deprecation warning
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
curl http://localhost:8000/reports/macos-local
curl http://localhost:8000/reports/linux-local
curl http://localhost:8000/reports/windows-local
docker compose down
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
- Confirm macOS and Linux commands are read-only
- Confirm platform commands run only on matching platforms
- Confirm unsupported routes do not execute platform commands
- Confirm tests do not require real Linux or real PowerShell
- Confirm listening-port output avoids usernames, file paths, command arguments, passwords, tokens, and secrets

Secret review:

```bash
rg -l --hidden --glob '!.git/**' --glob '!frontend/node_modules/**' --glob '!frontend/dist/**' --glob '!backend/.venv/**' 'OPENAI_API_KEY=|GEMINI_API_KEY=|sk-|ghp_|gho_|-----BEGIN .*PRIVATE KEY-----'
```

## Results

- `cd backend && uv run pytest`: passed, 72 tests passed, 1 upstream `TestClient` deprecation warning
- `cd frontend && pnpm build`: passed
- Frontend tests: not run because no frontend test setup exists yet
- `git diff --check`: passed
- Native macOS audit invocation: passed; returned 7 findings from read-only local checks with 4 good, 1 review, 1 fix_soon, and 1 unable-to-check finding on this Mac Mini
- Native macOS audit safety: no sudo, remediation, network scan, upload, AI provider call, or persistence was used
- `docker compose build`: passed
- `docker compose up -d`: passed
- `curl http://localhost:8000/health`: returned `{"status":"ok","app":"AI HomeGuard"}`
- `curl http://localhost:8000/version`: returned app/version metadata for AI HomeGuard
- `curl http://localhost:8000/reports/macos-local`: returned mode `local`, overall status `unable_to_check`, finding `macos-local-audit-unsupported-platform`, and evidence note `No macOS commands were run on this platform.`
- `curl http://localhost:8000/reports/linux-local`: returned mode `local` and Linux findings from the Docker container environment; limited container visibility produced expected `unable_to_check` findings for unavailable tools and disk encryption uncertainty
- `curl http://localhost:8000/reports/windows-local`: returned mode `local`, overall status `unable_to_check`, finding `windows-local-audit-unsupported-platform`, and evidence note `No Windows commands were run on this platform.`
- `docker compose down`: passed; validation containers removed
- Linux check behavior is covered with mocked command output and does not require a real Linux host
- Windows behavior remains covered with mocked command output and does not require real PowerShell on the Mac
- Broad secret scan produced only false positives for `sk-` inside words such as `disk-encryption` plus the documented scan command itself; no real secrets were found
- Safety review passed: no Nmap, packet capture, exploit, credential, brute-force, telemetry, database, OpenAI, remediation, package update/install, sudo, or ClamAV file-scan command usage was found

## Safety Notes

- macOS checks use read-only commands: `socketfilterfw --getglobalstate`, `fdesetup status`, `spctl --status`, `systemsetup -getremotelogin`, `lsof`, `netstat`, and `sw_vers`.
- Linux checks use read-only commands: `ufw status`, `firewall-cmd --state`, `systemctl is-active`, `service ssh status`, `ss -tuln`, `netstat -tuln`, `clamscan --version`, `freshclam --version`, `cat /etc/os-release`, `uname -r`, and `lsblk -f`.
- No commands install software, change settings, start or stop services, update packages, scan files, scan networks, capture packets, upload data, or call an AI provider.
- Linux disk encryption visibility is intentionally cautious. Lack of a visible LUKS marker is reported as `unable_to_check`, not as proof encryption is disabled.
- ClamAV is checked by version command only. No file scan is run.

## Known Warnings and Follow-ups

- FastAPI/Starlette emits an upstream `TestClient` deprecation warning during tests.
- Frontend test infrastructure has not been added yet.
- Real Linux host smoke validation is a future environment-specific task.
- Real Windows host smoke validation remains a future environment-specific task.
- Recommended next slice: Slice 6 - Unified Local Audit Report and Platform Auto-Detection.
