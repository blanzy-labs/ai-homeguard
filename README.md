# AI HomeGuard

AI HomeGuard is a local-first Blanzy Labs AI app for defensive home cyber hygiene. It helps home users understand and improve basic cybersecurity posture through safe local checks, plain-English risk explanations, and D3FEND-informed defensive guidance.

Repository: https://github.com/blanzy-labs/ai-homeguard

## Status

Current slice: Slice 5 - macOS and Linux Local Checks Foundation.

This baseline includes the repository scaffold, FastAPI health/version endpoints, Pydantic finding/report models, static deterministic demo data, a safety-first React flow, local questionnaire foundation, questionnaire-derived findings, read-only Windows, macOS, and Linux local check foundations, Docker Compose wiring, and project documentation.

The v0.1.0 target is the Local Home Security Audit MVP.

## Safety Boundaries

AI HomeGuard is a local-first defensive cyber hygiene tool. It does not exploit, attack, brute-force, packet-sniff, or scan public targets.

Slice 5 does not include:

- Network scanning
- Nmap integration
- OpenAI or other AI provider calls
- Live D3FEND mapping logic
- Telemetry, login, cloud storage, or database persistence
- Remediation or settings changes
- sudo or administrator escalation
- ClamAV file scans
- Packet capture

Windows, macOS, and Linux checks are read-only and only execute when AI HomeGuard is running on the matching operating system. Unsupported platform routes return an informational report without running commands for the wrong platform.

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

Slice 5 provides platform-specific local audit report endpoints:

```bash
curl http://localhost:8000/reports/windows-local
curl http://localhost:8000/reports/macos-local
curl http://localhost:8000/reports/linux-local
```

Additional route:

- `GET /checks/windows`

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
curl http://localhost:8000/reports/windows-local
curl http://localhost:8000/reports/macos-local
curl http://localhost:8000/reports/linux-local
docker compose down
```

Docker note: the backend runs inside a Linux container. In Docker, `/reports/macos-local` returns unsupported-platform output, and `/reports/linux-local` reflects the container environment rather than the Mac host. Run the backend natively for true host macOS checks.

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

## License

MIT. See [LICENSE](LICENSE).
