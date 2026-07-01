# AI HomeGuard

AI HomeGuard is a local-first home cyber hygiene app with read-only local checks, questionnaire-guided review, device inventory guidance, passive network awareness, and D3FEND-informed defensive guidance. It is part of the Blanzy Labs AI app family.

Repository: https://github.com/blanzy-labs/ai-homeguard

Release: v0.1.0 - Local Home Security Audit MVP

## What It Does

AI HomeGuard helps home users review common security basics in a calm, local-first workflow:

- Demo Mode with fake sample findings
- Safety-first guided UX and authorization acknowledgements
- Home security questionnaire
- Questionnaire-derived findings
- Read-only Windows local audit foundation
- Read-only macOS local audit foundation
- Read-only Linux local audit foundation
- Unified local device audit with platform auto-detection
- Combined HomeGuard report
- Markdown and JSON export
- D3FEND-informed defensive guidance catalog
- Passive local network awareness foundation
- Manual/demo device inventory helper
- Generic router guidance
- Report review experience with top actions, findings, filters, evidence source labels, limitations, safety notes, and export controls

## Safety Boundaries

AI HomeGuard is a defensive local review tool. It does not exploit, attack, brute-force, packet-sniff, inspect public targets, or change settings.

v0.1.0 does not include:

- Active network discovery
- Nmap
- Ping sweeps
- Port scanning other devices
- Packet capture
- Router login
- Credential collection or credential testing
- Public target scanning
- Automatic remediation or settings changes
- sudo or administrator escalation for baseline behavior
- AI provider calls
- External uploads
- Telemetry
- Database persistence
- Browser persistence of questionnaire answers, device inventory entries, reports, or exports
- Report auto-save
- Hosted SaaS behavior

Reports and exports may include questionnaire answers, manual inventory labels, and local audit evidence. Review exports before sharing.

The frontend may store only a versioned safety acknowledgement in `sessionStorage` for the current browser session so users do not have to accept the same safety terms repeatedly. It does not store questionnaire answers, reports, device inventory entries, secrets, exports, or telemetry.

## Limitations

AI HomeGuard v0.1.0 is not a penetration test, compliance tool, security certification, vulnerability scanner certification, router audit, or guarantee of safety.

Checks are best-effort and platform-dependent. Windows, macOS, and Linux checks only run on matching operating systems. Docker may reflect the Linux container environment rather than the host computer. If Docker is running on a Mac, the backend may correctly report a Linux container runtime; for true host-level macOS checks, run the backend natively with `uv`. Windows and Linux behavior is covered by mocked validation in this development environment and should be further validated on native systems.

Passive network awareness may be incomplete. Manual device inventory depends on user-provided or router app information. v0.1.0 does not actively discover devices on the network. Slice 13 - Safe Private Network Discovery is deferred for a future version with explicit authorization, private-network-only guardrails, user control, timeouts, transparent results, no credential testing, no exploit logic, no packet capture, and no router login. D3FEND-informed guidance is educational and does not represent official D3FEND certification or full D3FEND coverage.

See [docs/disclaimer.md](docs/disclaimer.md) and [docs/security-and-privacy.md](docs/security-and-privacy.md).

## Recommended App Flow

The recommended path is Full HomeGuard Report:

1. Start the guided flow.
2. Review the safety boundaries.
3. Answer the Home Security Questionnaire.
4. Optionally include read-only local checks, passive network awareness, and manual/demo inventory findings.
5. Review top actions, findings, evidence source labels, limitations, and D3FEND-informed guidance.
6. Export Markdown or JSON only when you choose to.

Secondary paths remain available for Demo Mode, Local Device Audit, Home Security Questionnaire, Local Network Awareness, Device Inventory Helper, and Defensive Guidance Catalog.

Advanced/manual routes remain available for Windows Device Audit, macOS Device Audit, and Linux Device Audit.

## Install

Prerequisites:

- git
- uv
- Node.js
- pnpm
- Docker Desktop or Docker Engine with Docker Compose

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

Stop Docker services:

```bash
docker compose down
```

## Expected URLs

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Health: http://localhost:8000/health
- Version: http://localhost:8000/version
- API docs: http://localhost:8000/docs
- Demo report: http://localhost:8000/demo/report
- Questionnaire: http://localhost:8000/questionnaire
- Local device report: http://localhost:8000/reports/local-device
- Runtime context: http://localhost:8000/runtime
- Guidance catalog: http://localhost:8000/knowledge/d3fend-guidance
- Network safety policy: http://localhost:8000/network/safety-policy
- Device inventory demo: http://localhost:8000/inventory/demo
- Router guidance: http://localhost:8000/router/guidance
- Windows local report: http://localhost:8000/reports/windows-local
- macOS local report: http://localhost:8000/reports/macos-local
- Linux local report: http://localhost:8000/reports/linux-local

The `/version` endpoint should return:

```json
{
  "app": "AI HomeGuard",
  "repo": "ai-homeguard",
  "version": "0.1.0",
  "family": "Blanzy Labs"
}
```

## API Summary

Demo and questionnaire:

- `GET /demo/report`
- `GET /questionnaire`
- `POST /questionnaire/evaluate`
- `POST /reports/questionnaire`
- `GET /questionnaire/demo-answers`

Local audit:

- `GET /runtime`
- `GET /reports/local-device`
- `GET /reports/windows-local`
- `GET /reports/macos-local`
- `GET /reports/linux-local`

Combined reports and exports:

- `POST /reports/combined`
- `POST /reports/export/markdown`
- `POST /reports/export/json`

D3FEND-informed guidance:

- `GET /knowledge/d3fend-guidance`
- `GET /knowledge/d3fend-guidance/{guidance_id}`

Network awareness:

- `GET /network/safety-policy`
- `POST /reports/network-awareness`

Device inventory and router guidance:

- `GET /inventory/demo`
- `POST /inventory/analyze`
- `POST /reports/device-inventory`
- `GET /router/guidance`

## Exports

Markdown and JSON exports are user-triggered only. The backend returns export content to the browser or caller; it does not save a copy, upload it, or persist report history.

## Development Commands

Backend tests:

```bash
cd backend
uv run pytest
```

Frontend tests and build:

```bash
cd frontend
pnpm test
pnpm build
```

Docker smoke:

```bash
docker compose build
docker compose up -d
curl http://localhost:8000/health
curl http://localhost:8000/version
curl http://localhost:8000/demo/report
curl http://localhost:8000/questionnaire
curl http://localhost:8000/reports/local-device
curl http://localhost:8000/knowledge/d3fend-guidance
curl http://localhost:8000/network/safety-policy
curl http://localhost:8000/inventory/demo
curl http://localhost:8000/router/guidance
docker compose down
```

## Documentation

- [Architecture](docs/architecture.md)
- [Product Direction](docs/product-direction.md)
- [Local Install](docs/local-install.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Release Checklist](docs/release-checklist.md)
- [Disclaimer](docs/disclaimer.md)
- [Security and Privacy](docs/security-and-privacy.md)
- [Demo Script](docs/demo-script.md)
- [Sample Scenarios](docs/sample-scenarios.md)
- [v0.1.0 Release Notes](docs/release-notes/v0.1.0.md)
- [v0.1.0 Validation](docs/validation/v0.1.0-validation.md)

## License

MIT. See [LICENSE](LICENSE).
