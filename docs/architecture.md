# Architecture

AI HomeGuard uses a simple local-first web app structure.

## Current Slice 6 Components

- Backend: FastAPI app with `/health` and `/version`
- Models: Pydantic evidence, guidance, finding, summary, and report models
- Demo data: deterministic static `HomeGuardReport` returned by `/demo/report`
- Questionnaire: static friendly questions, local answer submission, and deterministic finding mapper
- Windows, macOS, and Linux local checks: read-only platform-guarded check modules and report aggregators
- Unified local device audit: runtime context, auto-detection, and dispatch to one matching platform runner
- Frontend: React, Vite, and TypeScript safety-first flow, questionnaire, platform audit panels, results, and demo dashboard UI
- Docker: Docker Compose services for backend and frontend
- Docs: safety, privacy, install, troubleshooting, release, and validation notes

Slice 6 adds a unified local audit flow on top of the Windows, macOS, and Linux foundations. It does not include new deep checks, remediation, network scanning, OpenAI calls, AI provider integrations, persistence, sudo/admin escalation, package installation, ClamAV file scans, or live D3FEND mapping logic.

## Finding and Report Model

Findings are designed to support both home-user explanations and technical evidence. A finding includes:

- Status, severity, confidence, platform, and category
- Plain-English title, summary, impact explanation, and recommended action
- Evidence entries with source, method, observed value, expected value, and notes
- D3FEND-informed defensive guidance with home action, rationale, difficulty, and estimated time
- Optional ATT&CK context marked educational only

Reports wrap findings with a summary, top actions, platform scope, disclaimer, safety notes, and optional privacy-safe runtime context.

## Demo Data Flow

```text
frontend dashboard -> GET /demo/report -> static HomeGuardReport
```

The backend route returns deterministic in-process demo data from `backend/app/demo/demo_report.py`. The route does not run local commands, call external services, scan networks, or persist data.

Future real checks should generate findings using the same model so the frontend can display local results without changing the user-facing report shape.

## Questionnaire Flow

```text
welcome -> safety acknowledgement -> choose mode -> questionnaire -> questionnaire report
```

The frontend keeps acknowledgement state and questionnaire answers in browser memory only. Answers are sent to the local FastAPI backend when the user submits the questionnaire, and the backend returns a `HomeGuardReport` built from questionnaire-derived findings. The backend does not write answers to disk or send them to any external service.

Questionnaire routes:

- `GET /questionnaire`: returns static sections and questions
- `POST /questionnaire/evaluate`: returns `QuestionnaireResult`
- `POST /reports/questionnaire`: returns a `HomeGuardReport`
- `GET /questionnaire/demo-answers`: returns deterministic sample answers for local testing

## Questionnaire-to-Finding Mapper

The mapper in `backend/app/questionnaire/report_builder.py` converts selected answers into the existing `Finding` model. It uses questionnaire evidence, confidence based on answer certainty, non-alarmist statuses, and static D3FEND-informed guidance.

Future real checks should use the same finding/report model so questionnaire findings and local check findings can be merged into one report.

## Platform Check Architecture

Platform checks use a guarded command runner and explicit platform detection:

- `backend/app/core/platform.py`: detects `windows`, `macos`, `linux`, or `unknown`
- `backend/app/models/runtime.py`: privacy-safe runtime context model with platform, runtime environment, architecture, hostname-present boolean, notes, and limitations
- `backend/app/core/command_runner.py`: runs allowlisted commands with timeouts and captured output
- `backend/app/checks/local_runner.py`: unified local device audit dispatcher
- `backend/app/checks/windows/base.py`: Windows check context, allowlist, parsing helpers, and finding helpers
- `backend/app/checks/macos/base.py`: macOS check context, allowlist, parsing helpers, and finding helpers
- `backend/app/checks/linux/base.py`: Linux check context, allowlist, parsing helpers, and finding helpers
- `backend/app/checks/<platform>/*.py`: individual read-only check modules
- `backend/app/checks/<platform>/runner.py`: platform audit aggregators that return `HomeGuardReport`

Platform checks only run when the current platform matches the route. Unsupported platform routes return informational `unable_to_check` reports and do not invoke commands for the wrong operating system.

Unified local audit flow:

```text
frontend -> GET /reports/local-device -> local_runner -> platform-specific runner -> HomeGuardReport
```

The unified runner reads privacy-safe runtime context, calls exactly one matching platform runner, attaches runtime context to the report, recomputes summary counts, and appends safety notes. In Docker, it adds a container limitation note because the backend sees the container operating system rather than the host.

Runtime context route:

- `GET /runtime`: returns detected platform, runtime environment, optional architecture, hostname-present boolean, notes, and limitations
- Does not return hostname strings, usernames, personal paths, environment variables, or secrets

Future merge path:

- `backend/app/reports/merge.py` provides a minimal deterministic helper for combining reports later
- The helper preserves findings, recomputes summary counts, combines safety notes, and keeps all work in memory
- Future slices can combine questionnaire, local-device, and explicitly authorized network findings using this report shape

## Windows Check Modules

Slice 4 includes read-only modules for:

- Microsoft Defender status
- Windows Firewall profile status
- BitLocker or device encryption status
- Remote Desktop status
- Local listening ports summary
- Local Administrators group count/category summary
- Light Windows version/update visibility

The local administrator check intentionally summarizes counts and categories instead of exposing full account names in user-facing output.

## macOS Check Modules

Slice 5 includes read-only modules for:

- Application Firewall status via `socketfilterfw --getglobalstate`
- FileVault status via `fdesetup status`
- Gatekeeper status via `spctl --status`
- Remote Login status via `systemsetup -getremotelogin`
- Local listening TCP port summary via `lsof` with `netstat` fallback
- Light macOS version and update visibility via `sw_vers`

The listening-port check reports unique ports and generic service hints only. It does not report usernames, file paths, process command arguments, or remote scan results.

## Linux Check Modules

Slice 5 includes read-only modules for:

- Common firewall visibility via `ufw`, `firewall-cmd`, and `systemctl is-active firewalld`
- SSH service visibility via `systemctl` and `service`
- Local listening port summary via `ss` with `netstat` fallback
- ClamAV presence via `clamscan --version` or `freshclam --version`
- Light distribution, kernel, and update visibility via `/etc/os-release` and `uname -r`
- Cautious disk encryption visibility via `lsblk -f`

The ClamAV check never scans files. The disk encryption check reports `unable_to_check` when limited `lsblk` output cannot confirm encryption, rather than asserting encryption is off.

## Mocked Test Strategy

Development currently happens on a Mac Mini. Windows and Linux behavior is validated with fake command results and monkeypatched platform detection. macOS mapping is also covered by mocked outputs so tests do not depend on the developer machine's exact settings. Unified local audit tests monkeypatch runtime context and platform runners to verify dispatch without running real platform commands. Tests verify unsupported behavior, mocked output mapping, D3FEND guidance presence, command safety, and privacy-safe summaries without requiring Windows, Linux host access, real PowerShell, sudo, package updates, or file scans.

## Planned Modules

- `checks`: safe local checks for future audit slices
- `knowledge/D3FEND`: D3FEND-informed defensive guidance references
- `reports`: plain-English local report generation and future report merging
- `questionnaire`: beginner-friendly user inputs and context
- `platform adapters`: future router and network-aware implementations

Future slices may combine questionnaire and local-device reports or add explicitly authorized network-aware checks. Those checks should stay defensive, local-first, and explicit about user authorization.
