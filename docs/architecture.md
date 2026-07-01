# Architecture

AI HomeGuard uses a simple local-first web app structure.

## Current v0.1.0 Components

- Backend: FastAPI app with `/health` and `/version`
- Models: Pydantic evidence, guidance, finding, summary, and report models
- Demo data: deterministic static `HomeGuardReport` returned by `/demo/report`
- Questionnaire: static friendly questions, local answer submission, and deterministic finding mapper
- Windows, macOS, and Linux local checks: read-only platform-guarded check modules and report aggregators
- Unified local device audit: runtime context, auto-detection, and dispatch to one matching platform runner
- Combined report and export layer: report merge service, combined report route, Markdown export, and JSON export
- Knowledge layer: local D3FEND-informed guidance catalog, enrichment service, and knowledge API routes
- Network awareness and discovery foundation: authorization models, private-network guardrails, passive local context service, safe private device discovery, network report runners, and safety policy routes
- Device inventory foundation: manual/demo inventory models, deterministic fake inventory, analyzer, report route, combined integration, and generic router guidance
- Frontend: React, Vite, and TypeScript dashboard-first Run HomeGuard Check flow, de-emphasized Advanced Options, questionnaire, platform audit panels, network awareness, device inventory helper, shared report/dashboard components, results, and demo dashboard UI
- Frontend tests: dependency-free Node tests covering navigation, report review contracts, source badges, guidance labels, safety copy, and forbidden overclaiming language
- Docker: Docker Compose services for backend and frontend
- Docs: safety, privacy, install, troubleshooting, release, and validation notes

The v0.1.0 MVP includes frontend UX, copy, accessibility, responsive layout, report review polish, and authorization-gated Safe Private Network Discovery. Discovery is limited to detected RFC1918 private IPv4 local ranges, passive cache information, and bounded ping-only checks when explicitly authorized. It does not include Nmap, ping sweeps across arbitrary ranges, ARP scanning, port scanning, packet capture, device fingerprinting, router login, router credential collection, credential testing, public target scanning, remediation, OpenAI calls, AI provider integrations, persistence, sudo/admin escalation, package installation, ClamAV file scans, live MITRE/D3FEND fetching, or full D3FEND ontology parsing.

## Finding and Report Model

Findings are designed to support both home-user explanations and technical evidence. A finding includes:

- Status, severity, confidence, platform, and category
- Plain-English title, summary, impact explanation, and recommended action
- Evidence entries with source, method, observed value, expected value, and notes
- D3FEND-informed defensive guidance with home action, rationale, difficulty, and estimated time
- Optional catalog metadata such as guidance ID, likely admin requirement, and educational-only flag
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
welcome -> safety acknowledgement -> Run HomeGuard Check -> quick questions -> dashboard
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

## Combined Report Flow

```text
frontend -> questionnaire answers + optional local audit / network / discovery authorization
frontend -> POST /reports/combined
/reports/combined -> questionnaire report builder + optional local_runner + optional network awareness runner + optional private network discovery runner + optional device inventory report
merge_homeguard_reports -> combined HomeGuardReport
frontend -> POST /reports/export/markdown or /reports/export/json when user clicks export
```

The combined route works in memory only. It does not persist questionnaire answers, local audit results, network awareness results, network discovery results, device inventory submissions, or exports. Local device audit findings are included only when the request explicitly asks for them and includes authorization acknowledgement. Network awareness findings are included only when the request includes acknowledged `home_network` or `demo` authorization. Network discovery findings are included only when the request includes `include_network_discovery` and a `NetworkDiscoveryRequest` with acknowledgement, `home_network` scope, private-network-only acknowledgement, and explicit active-discovery consent if bounded ping discovery is enabled. Device inventory findings are included only when the request includes manual/demo device inventory data.

The merge service in `backend/app/reports/merge.py` preserves findings, enriches D3FEND-informed guidance, preserves educational ATT&CK context, recomputes summary counts, combines safety notes, and generates prioritized top actions. Future explicitly authorized network findings can be merged into this same report shape.

The export layer:

- `backend/app/reports/markdown.py`: renders a calm Markdown report for user-triggered download
- `backend/app/reports/json_export.py`: validates and returns a serializable report dictionary
- Both export paths enrich guidance in memory before rendering/serialization
- Does not write files to disk, call external services, or upload data

Later slices may add AI-assisted summaries generated from the same report model after explicit user consent.

## Frontend Dashboard and Report Review Flow

v0.1.0 consolidates report rendering around reusable frontend components and a dashboard-first combined-report surface:

- `HomeGuardDashboard`: primary report surface for the guided Run HomeGuard Check flow and Demo Mode, with overall status, top three actions, coverage, simple next steps, grouped findings, More Detail, and export
- `Network Devices` dashboard tile: summarizes authorized private network discovery with device count, review count, gateway visibility, Docker limitation, and simple safety boundaries
- `ReportReviewPanel`: shared report shell for demo, questionnaire, combined, local device, network awareness, and device inventory reports
- `ReportSummaryCard`: calm overall posture label, score, disclaimer, and report context
- `StatusCounts`: Good, Review, Fix Soon, Needs Attention, and Unable to Check counts
- `TopActionsList`: first five recommended actions by default
- `FindingFilters`: status, platform, evidence source, sort, and show/hide good findings controls
- `FindingCard`: user-facing finding summary with collapsed technical details and evidence
- `EvidenceSourceBadge`: normalized source label for each finding
- `DefensiveGuidancePanel`: D3FEND-informed educational guidance with difficulty, time, and admin context
- `LimitationsPanel`, `SafetyNotesPanel`, `ExportPanel`, `EmptyState`, `ErrorState`, and `LoadingState`: shared supporting states and review/export controls

The frontend navigation is organized as:

```text
welcome -> Run HomeGuard Check
Run HomeGuard Check -> safety acknowledgement -> guided setup -> quick questions or selected local checks
dashboard -> top actions -> grouped findings -> user-triggered Markdown/JSON export
welcome or primary nav -> Advanced Options -> secondary single-source paths
Advanced Options -> visually de-emphasized advanced/manual platform paths
```

The dashboard keeps evidence collapsed behind More Detail, shows what was checked and what still needs user input, keeps safety notes and limitations near export, and provides Start Over and Clear Current Report actions. These actions clear in-memory report/form state only; they do not delete files, call cleanup commands, reset the versioned safety acknowledgement, or change local settings.

## Dashboard-First Direction

Manual review after Slice 12A identified dashboard-first UX as the Slice 13 product direction. Non-technical home users should not need to understand or choose between technical modules before getting value. Slice 13 implements a primary `Run HomeGuard Check` flow and presents Demo Mode, Local Device Audit, Questionnaire, Local Network Awareness, and Device Inventory Helper as parts of one product experience.

The dashboard prioritizes overall status, top actions, what was checked, what still needs user input, what could not be checked, and simple next steps. Advanced/manual platform checks remain available but visually de-emphasized. The app stays local web-based for UI consistency across platforms, while the backend remains responsible for platform-specific checks.

Follow-up dashboard work is documented in [Product Direction](product-direction.md). This direction does not add active scanning or new v0.1.0 product scope.

## Evidence Source Labels

v0.1.0 normalizes user-facing evidence labels in `frontend/src/components/reportLabels.ts` so the UI does not imply manual or questionnaire findings were automatically detected.

Current labels include:

- `questionnaire`: Questionnaire
- `local_device` and local check evidence: Local Device Check
- `demo`: Demo Data
- `unsupported_platform`: Could Not Check
- `runtime_context`: Runtime Context
- `manual_inventory`: Manual Device Inventory
- `demo_inventory`: Demo Device Inventory
- `network_awareness`: Passive Network Awareness
- `network_discovery`: Network Discovery

The backend evidence sources remain deterministic and privacy-safe. The frontend derives labels from existing evidence and tags without adding backend check behavior.

## Frontend State and Persistence

The React app keeps questionnaire answers, selected combined-report options, device inventory entries, current reports, and export status in memory only. It does not use `localStorage`, IndexedDB, cookies, a database, or telemetry for answers, reports, inventory entries, exports, scan data, or secrets. Refreshing the browser clears in-memory answers and reports.

The only browser storage used by v0.1.0 is low-risk session UI state:

- `ai-homeguard-safety-ack-v0.1.0`: versioned safety acknowledgement for the current browser session
- `ai-homeguard-advanced-options-open-v0.1.0`: whether the Advanced Options drawer is open

These keys prevent repeated safety prompts and preserve the Advanced Options drawer state during normal navigation. They do not contain questionnaire answers, report content, device inventory entries, IP/MAC data, hostnames, router information, exports, secrets, or telemetry IDs.

Exports are created only when the user clicks Export Markdown or Export JSON. Export generation posts the current in-memory `HomeGuardReport` to the local backend export endpoint and downloads the returned content in the browser. The frontend does not auto-save exports.

## D3FEND-Informed Knowledge Layer

```text
finding -> guidance_service -> enriched finding -> report/export/frontend
frontend -> GET /knowledge/d3fend-guidance -> local curated catalog
```

Slice 8 stores a small curated local catalog in `backend/app/knowledge/d3fend_catalog.py`. The catalog is bundled with the app and contains educational defensive concepts such as host firewall, remote access review, strong authentication, full-disk encryption, endpoint protection, update hygiene, asset identification, isolation, backup, least privilege, router hardening, and local service exposure review.

The enrichment service in `backend/app/knowledge/guidance_service.py`:

- Preserves explicit guidance already attached to findings
- Adds catalog guidance when a finding has matching guidance IDs or tags
- Infers guidance from category/platform only when a finding lacks guidance
- Avoids duplicate guidance entries
- Keeps output deterministic and in memory

Knowledge API routes:

- `GET /knowledge/d3fend-guidance`: returns the local curated catalog plus version/source/disclaimer metadata
- `GET /knowledge/d3fend-guidance/{guidance_id}`: returns one catalog entry

The catalog is D3FEND-informed educational guidance, not official certification, not full D3FEND coverage, and not a guarantee of security. No live MITRE data, remote catalog data, or AI provider is fetched at runtime. A future slice may consider full ontology ingestion, but that is outside v0.1.0.

## Local Network Awareness Foundation

```text
frontend -> network authorization acknowledgement
frontend -> POST /reports/network-awareness
network runner -> passive context service -> network findings -> HomeGuardReport
combined report -> optional network_authorization -> network runner -> merge
```

Slice 9 introduces:

- `backend/app/models/network.py`: request-level authorization, scope, and passive context models
- `backend/app/network/guardrails.py`: private/local target classification and future scan-scope validation
- `backend/app/network/context.py`: passive local context parsing from read-only local route/neighbor cache commands
- `backend/app/network/findings.py`: network awareness findings using the existing Finding model
- `backend/app/network/runner.py`: authorization-gated report runner
- `GET /network/safety-policy`: authorization/disallowed-action policy
- `POST /reports/network-awareness`: passive local network awareness report

The guardrails classify RFC1918 IPv4 ranges, loopback, link-local, public IPs, IPv6 loopback, and IPv6 unique local addresses. Hostnames and domains are rejected as discovery targets in v0.1.0. Public targets are rejected.

The passive context service may read local route and neighbor-cache information through allowlisted read-only commands such as `route -n get default`, `netstat -rn`, `arp -a`, `ip route`, `ip neigh show`, `ipconfig`, and `route print`. These commands are used only for local passive context; they do not send discovery packets, scan ports, run Nmap, capture packets, log in to routers, or test credentials. User-facing output summarizes counts and private-context presence, not full MAC addresses or hostnames.

In Docker, network context may describe the container network rather than the host or home network.

## Safe Private Network Discovery

```text
dashboard -> discovery authorization
frontend -> POST /reports/network-discovery or /reports/combined
discovery route -> authorization checks -> private IPv4 guardrails
discovery runner -> passive cache + optional bounded private ping
discovery findings -> HomeGuardReport -> dashboard/export
```

Slice 14 introduces:

- `backend/app/models/network_discovery.py`: discovery authorization, method, runtime mode, discovered device, request, and result models
- `backend/app/network/guardrails.py`: private IPv4 subnet validation, hostname/public-target rejection, and conservative host limits
- `backend/app/network/discovery.py`: passive cache parsing, optional bounded ping-only private discovery, masked device hints, discovery findings, demo result, and report builder
- `backend/app/network/device_classifier.py`: deterministic conservative device classifier
- `GET /network/discovery-policy`: plain safety policy
- `GET /network/discovery/demo`: fake masked discovery result for screenshots/tests
- `POST /reports/network-discovery`: authorization-gated discovery report
- `POST /reports/combined`: optional `include_network_discovery` integration

Discovery requires `acknowledged: true`, `scope: home_network`, private-network-only acknowledgement, and explicit active-discovery consent before bounded ping checks run. The backend does not accept public targets, hostnames, domains, or arbitrary target fields in the primary UI. If active discovery runs, it only builds private IPv4 addresses from a detected local subnet, applies a conservative host cap, uses platform ping command arrays with timeouts, and skips unsupported/large/unknown ranges with limitations instead of escalating privileges.

Safe Private Network Discovery does not scan ports, run Nmap, fingerprint services, capture packets, log in to routers, test credentials, inspect public targets, persist results, upload data, call an AI provider, or change settings. MAC hints are masked and hostnames are hidden by default. Unknown devices are review-level findings, not panic findings.

## Device Inventory and Router Guidance Foundation

```text
frontend -> manual/demo device inventory
frontend -> GET /router/guidance
frontend -> POST /reports/device-inventory
inventory analyzer -> manual/demo findings -> HomeGuardReport
combined report -> optional device_inventory_submission -> merge
```

Slice 10 introduces:

- `backend/app/models/device_inventory.py`: device type, trust, update, placement, inventory item, submission, and result models
- `backend/app/demo/device_inventory.py`: deterministic fake inventory with no real IPs, MACs, or hostnames
- `backend/app/inventory/analyzer.py`: aggregate manual/demo inventory findings and report builder
- `backend/app/knowledge/router_guidance.py`: generic vendor-neutral router guidance topics
- `GET /inventory/demo`: fake demo inventory, result, and report
- `POST /inventory/analyze`: inventory result without persistence
- `POST /reports/device-inventory`: inventory `HomeGuardReport`
- `GET /router/guidance`: generic router guidance

The inventory model does not require hostname, IP address, MAC address, owner name, exact room, serial number, or router credentials. Optional MAC hints are masked before user-facing output, and optional IP hints are privacy-masked. The analyzer uses manual/demo evidence only, keeps confidence calm, avoids high-severity findings from manual inventory alone, and enriches findings through the local D3FEND-informed guidance catalog.

Router guidance is generic and vendor-neutral. It helps users review connected devices, unknown devices, guest Wi-Fi, router firmware, Wi-Fi security, remote administration, and router admin hygiene without providing exploit instructions, default router passwords, router bypass guidance, credential collection, or router login automation.

Manual inventory remains useful when router apps show more complete labels than passive cache or bounded ping discovery.

## Platform Check Architecture

Platform checks use a guarded command runner and explicit platform detection:

- `backend/app/core/platform.py`: detects `windows`, `macos`, `linux`, or `unknown`
- `backend/app/models/runtime.py`: privacy-safe runtime context model with platform, runtime environment, architecture, hostname-present boolean, notes, and limitations
- `backend/app/core/command_runner.py`: runs allowlisted commands with timeouts and captured output
- `backend/app/checks/local_runner.py`: unified local device audit dispatcher
- `backend/app/reports/merge.py`: combined report merge and summary helper
- `backend/app/reports/markdown.py`: Markdown report renderer
- `backend/app/reports/json_export.py`: JSON export helper
- `backend/app/knowledge/d3fend_catalog.py`: local curated defensive guidance catalog
- `backend/app/knowledge/guidance_service.py`: deterministic guidance lookup and enrichment
- `backend/app/network/guardrails.py`: private/public target classification for future network checks
- `backend/app/network/context.py`: passive local network context service
- `backend/app/network/runner.py`: authorization-gated network awareness report runner
- `backend/app/models/device_inventory.py`: manual/demo device inventory models
- `backend/app/inventory/analyzer.py`: inventory result/report builder
- `backend/app/knowledge/router_guidance.py`: generic router guidance topics
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

The unified runner reads privacy-safe runtime context, calls exactly one matching platform runner, attaches runtime context to the report, recomputes summary counts, and appends safety notes. In Docker, it adds a container runtime finding and limitation note because the backend sees the container operating system rather than the host. Docker on a Mac may therefore report Linux container runtime visibility; for host-level macOS checks, run the backend natively with uv.

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

Development currently happens on a Mac Mini. Windows and Linux behavior is validated with fake command results and monkeypatched platform detection. macOS mapping is also covered by mocked outputs so tests do not depend on the developer machine's exact settings. Unified local audit tests monkeypatch runtime context and platform runners to verify dispatch without running real platform commands. Tests verify unsupported behavior, mocked output mapping, D3FEND-informed guidance presence, catalog integrity, knowledge routes, command safety, and privacy-safe summaries without requiring Windows, Linux host access, real PowerShell, sudo, package updates, remote MITRE fetches, AI calls, or file scans.

## Planned Modules

- `checks`: safe local checks for future audit slices
- `knowledge`: D3FEND-informed defensive guidance references and future catalog ingestion experiments
- `reports`: plain-English local report generation and future report merging
- `questionnaire`: beginner-friendly user inputs and context
- `inventory`: manual/demo device inventory and router guidance
- `platform adapters`: future router and network-aware implementations

Future slices may add explicitly authorized network-aware checks or richer router guidance. Those checks should stay defensive, local-first, and explicit about user authorization.
