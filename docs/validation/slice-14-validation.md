# Slice 14 Validation - Safe Private Network Discovery

Date: 2026-07-01

## Scope

Slice 14 adds authorization-gated Safe Private Network Discovery for AI HomeGuard.

Allowed in this slice:

- Explicit user authorization
- Detected private RFC1918 IPv4 local ranges only
- Passive cache device hints
- Bounded ping-only private device discovery when explicitly enabled
- Masked MAC hints
- Hostnames hidden by default
- Local in-memory HomeGuard reports and user-triggered exports

Still out of scope:

- Public targets
- Hostname/domain targets
- Arbitrary target inputs in the primary UI
- Port scanning
- Nmap
- Service fingerprinting
- Vulnerability checks
- Exploit logic
- Packet capture
- Router login
- Router credentials
- Credential testing
- AI/OpenAI calls
- Telemetry
- Database/persistence
- Report auto-save
- Remediation/settings changes
- sudo/admin requirement for baseline behavior

## Pre-Checks

- Working repo: `/Users/robmythadis.com/dev/blanzy-labs/ai-homeguard`
- Branch: `main`
- Remote: `https://github.com/blanzy-labs/ai-homeguard.git`
- GitHub repo: `blanzy-labs/ai-homeguard`, default branch `main`
- `git tag --list`: no tags present
- `gh release list --repo blanzy-labs/ai-homeguard`: no releases listed
- Working tree before changes: clean

Baseline before Slice 14 edits:

- `cd backend && uv run pytest`: 162 passed, 1 known Starlette/TestClient deprecation warning
- `cd frontend && pnpm build`: passed
- `cd frontend && pnpm test`: 9 passed
- `docker compose build`: passed

## Backend Validation

New backend coverage includes:

- Discovery policy route
- Authorization required
- Private-network-only acknowledgement required
- RFC1918 private IPv4 validation
- Public IP rejection
- Hostname/domain rejection
- Loopback/link-local/IPv6 active-discovery rejection
- Large subnet host limit
- Mocked passive discovery
- Mocked active private ping discovery
- Ping calls only against private IPs
- No Nmap or port arguments in mocked ping calls
- Docker/container limitation finding
- Masked MAC output
- Hostnames hidden by default
- Discovery result maps to HomeGuard findings
- Combined report includes discovery findings when authorized

Command:

```bash
cd backend
uv run pytest
```

Result: 180 passed, 1 known Starlette/TestClient deprecation warning.

## Frontend Validation

New frontend/static coverage includes:

- Network Devices dashboard tile
- Discovery authorization copy
- Private-network-only acknowledgement
- No public-target input field
- No router password field
- Discovery progress copy
- Device count/review/Docker/could-not-check dashboard states
- Network Discovery source label
- Combined report request includes `include_network_discovery` and `network_discovery_request`
- Forbidden overclaiming/remediation language remains absent

Commands:

```bash
cd frontend
pnpm build
pnpm test
```

Result: build passed; 10 frontend tests passed.

## Docker Validation

Commands:

```bash
docker compose build
docker compose up -d
curl http://localhost:8000/health
curl http://localhost:8000/version
curl http://localhost:8000/network/discovery-policy
curl http://localhost:8000/network/discovery/demo
curl -X POST http://localhost:8000/reports/network-discovery \
  -H 'Content-Type: application/json' \
  -d '{"authorization":{"acknowledged":false,"scope":"home_network","statement_version":"v0.1.0-slice-14","include_active_discovery":false,"user_understands_private_network_only":true},"method":"passive_cache"}'
curl -X POST http://localhost:8000/reports/network-discovery \
  -H 'Content-Type: application/json' \
  -d '{"authorization":{"acknowledged":true,"scope":"home_network","statement_version":"v0.1.0-slice-14","include_active_discovery":false,"user_understands_private_network_only":true},"method":"passive_cache"}'
docker compose down
docker compose ps
```

Result:

- `docker compose build`: passed
- Health endpoint returned `{"status":"ok","app":"AI HomeGuard"}`
- Version endpoint returned `{"app":"AI HomeGuard","repo":"ai-homeguard","version":"0.1.0","family":"Blanzy Labs"}`
- Discovery policy returned active discovery support with private-only safety boundaries including `No ports are scanned.`
- Discovery demo returned 3 fake devices and masked MAC hints such as `aa:bb:cc:xx:xx:xx`
- Unauthorized discovery returned 400 with `Network discovery requires authorization acknowledgement.`
- Authorized passive discovery returned a `network_discovery` report with review status and 3 discovered devices in Docker
- Frontend responded with HTTP 200
- `docker compose down` completed and `docker compose ps` showed no services running
- Docker discovery may reflect the container network rather than the host's home network

## Native Mac Validation

Native backend passive smoke was run on macOS:

```bash
cd backend
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/network/discovery-policy
curl -X POST http://127.0.0.1:8000/reports/network-discovery \
  -H 'Content-Type: application/json' \
  -d '{"authorization":{"acknowledged":true,"scope":"home_network","statement_version":"v0.1.0-slice-14","include_active_discovery":false,"user_understands_private_network_only":true},"method":"passive_cache"}'
```

Result:

- Native backend started successfully on `127.0.0.1:8000`
- Health endpoint returned 200
- Discovery policy endpoint returned 200
- Authorized passive discovery returned 200
- Backend was stopped after validation
- Follow-up manual UI validation on native Mac remains recommended before final release approval

Recommended owner/native smoke:

- Run backend natively with `uv run uvicorn app.main:app --host 127.0.0.1 --port 8000`
- Run frontend with `pnpm dev`
- Open the app
- Run HomeGuard Check
- Select Find devices on my home network
- Confirm both acknowledgements
- Confirm device count, review count, gateway/Docker limitation if present, and export controls
- Confirm no public target fields, no port checks, no router login, no credential request, and no packet capture language

## Manual UI Smoke Notes

In-app browser automation was unavailable during Slice 13 validation. If the same browser tooling remains unavailable, owner manual UI smoke should cover:

- Home page loads
- Run HomeGuard Check remains obvious
- Find devices on my home network appears as an optional guided choice
- Discovery cannot continue without both acknowledgements
- Discovery loading state says `Finding devices on your home network...`
- Dashboard shows Network Devices tile
- Unknown devices are review-level, not panic-level
- Docker limitation is clear if Docker is used
- Export buttons still work
- Mobile-ish width remains usable

## Secret and Safety Review

Safety properties to confirm during final review:

- No Nmap execution path
- No port scanning
- No TCP/UDP service scanning
- No packet capture
- No router login
- No credential collection
- No public IP scanning
- No hostname/domain discovery targets
- No arbitrary target input in primary UI
- No AI/OpenAI calls
- No telemetry
- No database/persistence
- No report auto-save
- No remediation/settings changes
- No sudo/admin requirement
- MAC hints masked
- Hostnames hidden by default
- Discovery authorization required
- Docker limitation documented
- User-facing wording stays calm and simple

Secret scan should exclude virtualenv, node modules, build output, caches, and `.git`. Any real secret finding should stop release work and report file path only.

## Known Limitations

- Discovery can be incomplete when ping replies are blocked.
- Docker can show the container network.
- VPNs can change route visibility.
- Guest Wi-Fi/client isolation can hide devices.
- Router apps may show more complete device names, offline leases, or historical entries.
- Unknown devices are review items and require user/router-app confirmation.
