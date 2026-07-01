# Architecture

AI HomeGuard uses a simple local-first web app structure.

## Current Slice 4 Components

- Backend: FastAPI app with `/health` and `/version`
- Models: Pydantic evidence, guidance, finding, summary, and report models
- Demo data: deterministic static `HomeGuardReport` returned by `/demo/report`
- Questionnaire: static friendly questions, local answer submission, and deterministic finding mapper
- Windows local checks: read-only platform-guarded check modules and report aggregator
- Frontend: React, Vite, and TypeScript safety-first flow, questionnaire, Windows audit panel, results, and demo dashboard UI
- Docker: Docker Compose services for backend and frontend
- Docs: safety, privacy, install, troubleshooting, release, and validation notes

Slice 4 adds the first real platform-check foundation for Windows. It does not include remediation, network scanning, OpenAI calls, AI provider integrations, persistence, or live D3FEND mapping logic.

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
- `backend/app/core/command_runner.py`: runs allowlisted commands with timeouts and captured output
- `backend/app/checks/windows/base.py`: Windows check context, allowlist, parsing helpers, and finding helpers
- `backend/app/checks/windows/*.py`: individual read-only check modules
- `backend/app/checks/windows/runner.py`: Windows audit aggregator that returns `HomeGuardReport`

Windows checks only run when the current platform is Windows. On macOS or Linux, `/reports/windows-local` returns an unsupported-platform report and does not invoke Windows commands.

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

## Mocked Test Strategy

Development currently happens on a Mac Mini, so Windows tests use fake command results and monkeypatched platform detection. Tests verify non-Windows unsupported behavior, mocked Windows output mapping, D3FEND guidance presence, timeout handling, and privacy-safe local administrator summaries without requiring a Windows machine or running PowerShell.

## Planned Modules

- `checks`: safe local checks for future audit slices
- `knowledge/D3FEND`: D3FEND-informed defensive guidance references
- `reports`: plain-English local report generation
- `questionnaire`: beginner-friendly user inputs and context
- `platform adapters`: Windows, macOS, and Linux check implementations

Future slices may add Windows, macOS, and Linux security checks. Those checks should stay defensive, local-first, and explicit about user authorization.
