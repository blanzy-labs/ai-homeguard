# AI HomeGuard

AI HomeGuard is a local-first Blanzy Labs AI app for defensive home cyber hygiene. It helps home users understand and improve basic cybersecurity posture through safe local checks, plain-English risk explanations, and D3FEND-informed defensive guidance.

Repository: https://github.com/blanzy-labs/ai-homeguard

## Status

Current slice: Slice 7 - Combined HomeGuard Report and Export Foundation.

This baseline includes the repository scaffold, FastAPI health/version endpoints, Pydantic finding/report models, static deterministic demo data, a safety-first React flow, local questionnaire foundation, questionnaire-derived findings, read-only Windows, macOS, and Linux local check foundations, a unified auto-detected local device audit, combined HomeGuard reports, user-triggered Markdown/JSON exports, Docker Compose wiring, and project documentation.

The v0.1.0 target is the Local Home Security Audit MVP.

## Safety Boundaries

AI HomeGuard is a local-first defensive cyber hygiene tool. It does not exploit, attack, brute-force, packet-sniff, or scan public targets.

Slice 7 does not include:

- Network scanning
- Nmap integration
- OpenAI or other AI provider calls
- Live D3FEND mapping logic
- Telemetry, login, cloud storage, or database persistence
- Remediation or settings changes
- sudo or administrator escalation
- ClamAV file scans
- Packet capture
- Automatic report saving

Windows, macOS, and Linux checks are read-only and only execute when AI HomeGuard is running on the matching operating system. Unsupported platform routes return an informational report without running commands for the wrong platform.

The unified local device audit auto-detects the runtime platform and calls the matching Windows, macOS, or Linux runner. If the backend is running inside Docker, results may reflect the container environment rather than the host computer.

The combined report can merge questionnaire-derived findings with optional read-only local device audit findings. Exports are user-triggered only and are not saved automatically or uploaded.

The demo dashboard uses fake sample findings only. D3FEND-informed guidance is currently static demo content, and optional ATT&CK context is educational only.

See [docs/disclaimer.md](docs/disclaimer.md) and [docs/security-and-privacy.md](docs/security-and-privacy.md).

## Demo and Questionnaire API

Deterministic demo report:

```bash
curl http://localhost:8000/demo/report
```

Questionnaire routes:

```bash
curl http://localhost:8000/questionnaire
```

- `GET /questionnaire`
- `POST /questionnaire/evaluate`
- `POST /reports/questionnaire`
- `GET /questionnaire/demo-answers`

Demo aliases:

- `GET /demo/findings`
- `GET /reports/demo`

These endpoints return static questions, fake demo data, or questionnaire-derived findings. They do not run local commands, inspect the device, scan the network, call an AI provider, upload data, or persist questionnaire answers.

## Local Audit APIs

Slice 6 provides one primary auto-detected local device audit endpoint plus platform-specific manual endpoints:

```bash
curl http://localhost:8000/reports/local-device
curl http://localhost:8000/reports/windows-local
curl http://localhost:8000/reports/macos-local
curl http://localhost:8000/reports/linux-local
curl http://localhost:8000/runtime
```

Additional route:

- `GET /checks/windows`

Unified route behavior:

- `GET /reports/local-device` detects the runtime platform and calls the matching Windows, macOS, or Linux runner
- Unknown platforms return a safe `unable_to_check` report without running platform commands
- Docker/container runtime adds a limitation note that checks may reflect the container rather than the host
- `GET /runtime` returns privacy-safe runtime context without hostname strings, usernames, personal paths, environment variables, or secrets

Windows check scope:

- Microsoft Defender status
- Windows Firewall profile status
- BitLocker or device encryption status
- Remote Desktop status
- Local listening ports summary
- Local Administrators group summary
- Light Windows version/update visibility

macOS check scope:

- Application Firewall status
- FileVault status
- Gatekeeper status
- Remote Login status
- Local listening TCP port summary
- Light macOS version/update visibility

Linux check scope:

- Common firewall status from UFW/firewalld visibility
- SSH service status
- Local listening port summary
- ClamAV presence via version commands only
- Light Linux distribution/kernel and update visibility
- Cautious disk encryption visibility from limited `lsblk -f` output

Safety boundaries:

- Read-only checks only
- No settings changed
- No remediation attempted
- No network scans
- No AI calls
- No persistence
- No sudo/admin escalation
- No ClamAV file scans
- No local administrator usernames exposed in user-facing output
- No usernames, file paths, process command arguments, passwords, tokens, or secrets collected from listening-port checks

When a platform route is called from the wrong operating system, AI HomeGuard returns an unsupported-platform report with `unable_to_check` findings and does not execute that platform's commands.

## Combined Report and Export APIs

Combined report:

```bash
curl -X POST http://localhost:8000/reports/combined
```

Export routes:

- `POST /reports/export/markdown`
- `POST /reports/export/json`

Combined reports can include:

- Questionnaire-derived findings
- Optional local device audit findings after authorization acknowledgement
- Existing safety notes, runtime context, D3FEND-informed guidance, and top actions

Exports:

- Are user-triggered only
- Are returned as Markdown or JSON
- Are not saved automatically by the backend
- Are not uploaded to any external service
- May include questionnaire answers and local audit evidence, so review before sharing

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
- Questionnaire: http://localhost:8000/questionnaire
- Local device report: http://localhost:8000/reports/local-device
- Runtime context: http://localhost:8000/runtime
- Windows local report: http://localhost:8000/reports/windows-local
- macOS local report: http://localhost:8000/reports/macos-local
- Linux local report: http://localhost:8000/reports/linux-local
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
curl http://localhost:8000/questionnaire
curl http://localhost:8000/demo/report
curl http://localhost:8000/runtime
curl http://localhost:8000/reports/local-device
curl http://localhost:8000/reports/windows-local
curl http://localhost:8000/reports/macos-local
curl http://localhost:8000/reports/linux-local
docker compose down
```

Docker note: the backend runs inside a Linux container. In Docker, `/reports/local-device` and `/reports/linux-local` reflect the container environment rather than the Mac host, and `/reports/macos-local` returns unsupported-platform output. Run the backend natively for true host macOS checks.

## Documentation

- [Architecture](docs/architecture.md)
- [Local Install](docs/local-install.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Release Checklist](docs/release-checklist.md)
- [Disclaimer](docs/disclaimer.md)
- [Security and Privacy](docs/security-and-privacy.md)
- [Slice 1 Prerequisite Validation](docs/validation/slice-1-prerequisites.md)
- [Slice 2 Validation](docs/validation/slice-2-validation.md)
- [Slice 3 Validation](docs/validation/slice-3-validation.md)
- [Slice 4 Validation](docs/validation/slice-4-validation.md)
- [Slice 5 Validation](docs/validation/slice-5-validation.md)
- [Slice 6 Validation](docs/validation/slice-6-validation.md)
- [Slice 7 Validation](docs/validation/slice-7-validation.md)

## License

MIT. See [LICENSE](LICENSE).
