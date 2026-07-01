# Slice 13 Validation - Dashboard-First HomeGuard Experience

Date: 2026-07-01

## Scope

Slice 13 moves AI HomeGuard toward a dashboard-first experience for non-technical home users:

```text
Run HomeGuard Check -> dashboard -> top actions -> export
```

This slice is frontend/product UX work. It does not add backend check behavior, active discovery, Nmap, AI calls, persistence, telemetry, authentication, router login, remediation, or new platform checks.

## Pre-Checks

- Working repo: `/Users/robmythadis.com/dev/blanzy-labs/ai-homeguard`
- Branch: `main`
- Remote: `https://github.com/blanzy-labs/ai-homeguard.git`
- GitHub repo: `blanzy-labs/ai-homeguard`, default branch `main`
- `git tag --list`: no tags present
- `gh release list --repo blanzy-labs/ai-homeguard`: no releases listed
- Baseline before Slice 13 edits:
  - `cd backend && uv run pytest`: 162 passed, 1 known Starlette/TestClient deprecation warning
  - `cd frontend && pnpm build`: passed
  - `cd frontend && pnpm test`: 9 passed
  - `docker compose build`: passed

## Dashboard-First Validation

Static/frontend validation confirms:

- Home page has one clear primary CTA: `Run HomeGuard Check`
- Secondary actions are `Try Demo`, `View Last Result in This Session` when applicable, and `Advanced Options`
- Backend status remains in the compact status panel instead of dominating the home page
- Guided setup defaults include This Device and quick questions
- Passive network awareness remains optional and separately acknowledged
- Device inventory is optional and requires user-provided/demo inventory before inclusion
- Quick questions can be skipped while still running selected checks
- Combined report renders as a HomeGuard Dashboard
- Demo Mode renders through the same dashboard component and labels demo data clearly
- Dashboard shows overall status, Things to Do First, status counts, coverage, grouped findings, More Detail, limitations, safety notes, and export controls
- Findings are grouped by plain categories: This Device, Router & Wi-Fi, Accounts, Backups, Smart Devices, Network Awareness, Other
- Advanced/manual platform checks remain available but visually de-emphasized

## Automated Validation

Backend:

```bash
cd backend
uv run pytest
```

Result: passed, 162 tests, 1 known Starlette/TestClient deprecation warning.

Frontend build:

```bash
cd frontend
pnpm build
```

Result: passed TypeScript check and Vite production build.

Frontend tests:

```bash
cd frontend
pnpm test
```

Result: passed, 9 Node tests.

Git whitespace check:

```bash
git diff --check
```

Result: passed with no output.

## Docker Validation

Build:

```bash
docker compose build
```

Result: passed for backend and frontend images.

Smoke:

```bash
docker compose up -d
curl http://localhost:8000/health
curl http://localhost:8000/version
curl http://localhost:8000/demo/report
curl http://localhost:8000/reports/local-device
curl http://localhost:8000/knowledge/d3fend-guidance
curl -I http://localhost:5173
docker compose down
docker compose ps
```

Result:

- `/health`: `{"status":"ok","app":"AI HomeGuard"}`
- `/version`: app `AI HomeGuard`, repo `ai-homeguard`, version `0.1.0`, family `Blanzy Labs`
- `/demo/report`: returned report with overall status `fix_soon` and 8 findings
- `/reports/local-device`: returned report with overall status `review` and 8 findings in Docker
- `/knowledge/d3fend-guidance`: returned 12 guidance entries
- Frontend: `HTTP/1.1 200 OK`
- `docker compose ps` after shutdown: no running services

## Manual UI Smoke Notes

In-app browser automation was attempted using the Browser plugin. The browser runtime reported:

```text
Browser is not available: iab
```

`agent.browsers.list()` returned an empty list, so browser-based manual UI automation could not be completed in this session. Per the browser tooling instructions, no unrelated browser fallback was used.

Manual owner smoke is still recommended for:

- Home page loads and Run HomeGuard Check is obvious
- Demo Mode shows the dashboard
- Advanced Options are secondary but available
- Safety acknowledgement is not repeated unnecessarily
- Full report flow produces a dashboard
- Dashboard shows overall status, top 3 actions, coverage, grouped findings, More Detail, limitations, and export controls
- Docker/container limitation reads as a limitation, not a failure
- Mobile-ish width remains usable
- No router password fields or scan-public-target UI are visible

## Copy Review

Frontend tests and source review confirm:

- No user-facing `slice` language in primary UI
- `More Detail` replaces technical-detail wording in finding cards
- `Could Not Check` replaces the primary unsupported-platform label
- No `auto-fix`, `hacked`, `certified secure`, `guaranteed`, `pen test`, or `deep scan` copy in frontend source
- D3FEND wording remains educational/informed and does not claim official certification
- Demo data is labeled: `Demo data - no checks were run.`

## Secret and Safety Review

Secret scan:

```bash
rg -n --hidden --glob '!.git/*' --glob '!backend/.venv/*' --glob '!frontend/node_modules/*' --glob '!frontend/dist/*' --glob '!**/.pytest_cache/*' --glob '!**/__pycache__/*' "(AKIA[0-9A-Z]{16}|OPENAI_API_KEY\s*=|sk-[A-Za-z0-9_-]{20,}|-----BEGIN (RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----|api[_-]?key\s*[:=]\s*['\"][^'\"]+|secret\s*[:=]\s*['\"][^'\"]+|token\s*[:=]\s*['\"][^'\"]+)"
```

Result: no real secrets found. Hits were existing validation-doc command examples and a non-secret finding ID containing `encryption-unable-to-check`.

Safety scan:

```bash
rg -n --glob 'backend/app/**' --glob 'frontend/src/**' "(nmap|ping sweep|arp scan|port scan|packet capture|router login|credential|OpenAI|telemetry|localStorage|indexedDB|document\.cookie|auto-fix|hacked|certified secure|guaranteed|pen test|deep scan)"
```

Result: expected safety-boundary and disclaimer strings only. No new active scanning, Nmap execution path, router login flow, credential collection, OpenAI/API provider calls, telemetry, persistence, auto-fix button, scan-public-target UI, or remediation path was added.

Browser storage review:

- `sessionStorage` is used only for low-risk UI state:
  - `ai-homeguard-safety-ack-v0.1.0`
  - `ai-homeguard-advanced-options-open-v0.1.0`
- Questionnaire answers, reports, device inventory entries, host details, network details, exports, secrets, and telemetry are not persisted.

## Documentation Updates

Updated:

- `README.md`
- `docs/architecture.md`
- `docs/security-and-privacy.md`
- `docs/troubleshooting.md`
- `docs/release-checklist.md`
- `docs/product-direction.md`
- `docs/demo-script.md`
- `docs/sample-scenarios.md`
- `docs/release-notes/v0.1.0.md`

## Backend Changes

No backend code changes were made. Existing backend report routes, check behavior, exports, safety boundaries, and tests remain in place.

## Known Follow-Ups

- Owner manual UI smoke is still required because in-app browser automation was unavailable in this session.
- Native Windows and Linux validation should still be performed on real systems before broad distribution.
- Owner review should approve the dashboard-first UX before creating the final v0.1.0 release tag.
- Future safe private network discovery remains out of scope for v0.1.0 and must stay explicit-authorization, private-network-only, user-controlled, and free of credential testing, exploit logic, packet capture, router login, public target scanning, telemetry, or persistence.
