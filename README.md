# AI HomeGuard

AI HomeGuard is a local-first Blanzy Labs AI app for defensive home cyber hygiene. It helps home users understand and improve basic cybersecurity posture through safe local checks, plain-English risk explanations, and D3FEND-informed defensive guidance.

Repository: https://github.com/blanzy-labs/ai-homeguard

## Status

Current slice: Slice 9 - Safe Local Network Awareness Foundation.

This baseline includes the repository scaffold, FastAPI health/version endpoints, Pydantic finding/report models, static deterministic demo data, a safety-first React flow, local questionnaire foundation, questionnaire-derived findings, read-only Windows, macOS, and Linux local check foundations, a unified auto-detected local device audit, combined HomeGuard reports, user-triggered Markdown/JSON exports, a local D3FEND-informed defensive guidance catalog, a safe local network awareness foundation, Docker Compose wiring, and project documentation.

The v0.1.0 target is the Local Home Security Audit MVP.

## Safety Boundaries

AI HomeGuard is a local-first defensive cyber hygiene tool. It does not exploit, attack, brute-force, packet-sniff, or scan public targets.

Slice 9 does not include:

- Active network scanning
- Nmap integration
- Ping sweeps
- Port scanning
- Packet capture
- Router login or credential testing
- Public target scanning
- OpenAI or other AI provider calls
- Live MITRE/D3FEND data fetching at runtime
- Telemetry, login, cloud storage, or database persistence
- Remediation or settings changes
- sudo or administrator escalation
- ClamAV file scans
- Packet capture
- Automatic report saving

Windows, macOS, and Linux checks are read-only and only execute when AI HomeGuard is running on the matching operating system. Unsupported platform routes return an informational report without running commands for the wrong platform.

The unified local device audit auto-detects the runtime platform and calls the matching Windows, macOS, or Linux runner. If the backend is running inside Docker, results may reflect the container environment rather than the host computer.

The combined report can merge questionnaire-derived findings with optional read-only local device audit findings. Exports are user-triggered only and are not saved automatically or uploaded.

Local Network Awareness is authorization-gated and passive only. It may summarize local runtime/router context and passive cache counts, but it does not run active discovery, Nmap, ping sweeps, port scanning, packet capture, router login, credential testing, or public target scanning. Authorization is request-level only and is not stored.

The demo dashboard uses fake sample findings only. D3FEND-informed guidance comes from a small local curated educational catalog and explicit finding guidance. It is not official D3FEND coverage, certification, or a guarantee of security. Optional ATT&CK context is educational only.

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

## Defensive Guidance API

Slice 8 adds a local deterministic D3FEND-informed guidance layer:

```bash
curl http://localhost:8000/knowledge/d3fend-guidance
curl http://localhost:8000/knowledge/d3fend-guidance/enable_host_firewall
```

Routes:

- `GET /knowledge/d3fend-guidance`
- `GET /knowledge/d3fend-guidance/{guidance_id}`

The catalog is bundled with the app and is used to enrich demo, questionnaire, local device, combined, Markdown, and JSON reports. It does not fetch live MITRE data, call an AI provider, upload data, persist reports, or claim complete D3FEND coverage.

## Local Network Awareness APIs

Safety policy:

```bash
curl http://localhost:8000/network/safety-policy
```

Network awareness report:

```bash
curl -X POST http://localhost:8000/reports/network-awareness \
  -H "Content-Type: application/json" \
  -d '{"acknowledged":true,"scope":"home_network","statement_version":"v0.1.0-slice-9"}'
```

Routes:

- `GET /network/safety-policy`
- `POST /reports/network-awareness`

Combined reports can also include network awareness by setting `include_network_awareness: true` and passing `network_authorization` with acknowledged `home_network` or `demo` scope.

Network awareness boundaries:

- Authorization required
- Passive/local context only
- No active discovery
- No Nmap
- No ping sweeps
- No port scanning
- No public target scanning
- No router login
- No packet capture
- No persistence or upload
- Full MAC addresses and hostnames are not shown by default

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
- Guidance catalog: http://localhost:8000/knowledge/d3fend-guidance
- Network safety policy: http://localhost:8000/network/safety-policy
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
curl http://localhost:8000/knowledge/d3fend-guidance
curl http://localhost:8000/network/safety-policy
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
- [Slice 8 Validation](docs/validation/slice-8-validation.md)
- [Slice 9 Validation](docs/validation/slice-9-validation.md)

## License

MIT. See [LICENSE](LICENSE).
