# Security and Privacy

AI HomeGuard is designed as a local-first defensive cyber hygiene app.

AI HomeGuard v0.1.0 includes:

- No telemetry
- No database
- No cloud storage
- No login or account system
- No background service
- No public target scanning or port scanning
- No OpenAI or other AI provider calls
- Read-only Windows local audit commands only when running on Windows
- Read-only macOS local audit commands only when running on macOS
- Read-only Linux local audit commands only when running on Linux
- Unified local device audit that calls only the matching detected platform runner
- Combined reports from questionnaire findings and optional local device findings
- User-triggered Markdown and JSON exports
- Local static D3FEND-informed guidance catalog and enrichment service
- Authorization-gated passive local network awareness
- Authorization-gated Safe Private Network Discovery using passive cache data and bounded private IPv4 ping only
- Manual/demo device inventory helper
- Generic vendor-neutral router guidance
- Frontend report review with shared report, finding, filter, export, loading, error, and empty states
- Start Over and Clear Current Report controls that clear in-memory frontend state only
- Versioned frontend safety acknowledgement stored in `sessionStorage` for the current browser session only
- Privacy-safe runtime context through `/runtime`
- Unsupported-platform reports when a local audit route is called from the wrong operating system
- No sudo, administrator escalation, package installs, or remediation
- No ClamAV file scans
- No unauthenticated or public device discovery
- No real router login or router credential collection
- No Nmap, ping sweeps across arbitrary ranges, ARP scanning, port scanning, packet capture, device fingerprinting, router login, credential testing, or public target scanning
- Static fake demo data only
- Dashboard-first Run HomeGuard Check flow that reuses existing backend reports and exports
- Questionnaire answers kept in browser memory and submitted only to the local backend
- No questionnaire answer persistence
- No browser persistence of questionnaire answers, device inventory entries, reports, or export status
- No automatic report persistence

AI HomeGuard does not exploit, brute-force, capture credentials, sniff packets, or attack targets.

Network-aware checks require explicit user authorization and must remain limited to systems and networks the user owns or is authorized to assess.

The `/demo/report` endpoint returns a deterministic fake report for UI development and education. It does not inspect the local system, read local security settings, enumerate devices, call an AI provider, store records, or send telemetry.

The questionnaire avoids passwords, credentials, addresses, usernames, email addresses, IP addresses, MAC addresses, and other personal identifiers. Users should not enter secrets or identifying details into questionnaire fields.

The questionnaire endpoints do not upload data to an external service and do not write answers to disk. The returned report is generated in memory from the submitted answers. The v0.1.0 frontend stores answers and reports in React state only; it does not use `localStorage`, IndexedDB, cookies, or telemetry for questionnaire answers, reports, exports, device inventory entries, or scan data.

The only browser storage used by the v0.1.0 frontend is low-risk `sessionStorage` UI state:

- `ai-homeguard-safety-ack-v0.1.0`: versioned safety acknowledgement for the current browser session
- `ai-homeguard-advanced-options-open-v0.1.0`: whether the Advanced Options drawer is open

These keys let users move through the local app without repeated safety prompts and keep the advanced drawer state predictable. They do not contain questionnaire answers, report data, device inventory entries, secrets, IP addresses, MAC addresses, hostnames, router information, exports, telemetry IDs, or account identifiers.

Combined report endpoints generate reports in memory. They do not write reports to disk, create a database record, upload data, call an AI provider, or add telemetry. If local device findings are requested, the request must include explicit authorization acknowledgement. If device inventory findings are requested, the request must include manual/demo inventory data.

Markdown and JSON exports are user-triggered. The backend returns export content to the browser or caller; it does not save a copy. The frontend creates browser downloads only after an export button is clicked. Exported reports may contain user-provided questionnaire answers, manual inventory labels, and local audit evidence, so users should review exports before sharing them.

The D3FEND-informed guidance catalog is local and static. AI HomeGuard does not fetch live MITRE data, call an AI provider, send telemetry, persist catalog lookups, or change settings while enriching guidance. Guidance is educational and may be incomplete.

Network awareness authorization is request-level only and is not stored. Passive local context uses local route and neighbor-cache visibility only. It does not accept target input fields, scan public IPs, enumerate all devices, log in to routers, request router credentials, capture packets, or test credentials. Passive neighbor information is summarized by count only. Full MAC addresses and hostnames are not shown by default.

Safe Private Network Discovery authorization is also request-level only and is not stored. It requires acknowledgement, `home_network` scope, private-network-only acknowledgement, and explicit active-discovery consent before bounded ping checks run. Discovery is limited to detected RFC1918 private IPv4 local ranges and a conservative host count. It uses passive cache data and, when enabled, simple platform ping command arrays with short timeouts. It does not accept user-entered public targets, hostnames, domains, or arbitrary target fields in the primary UI. It does not scan ports, run Nmap, fingerprint services, capture packets, log in to routers, request router credentials, test credentials, upload results, persist results, or change settings. MAC hints are masked and hostnames are hidden by default. Unknown devices are review-level findings.

Device inventory is manual/demo only. The inventory helper does not discover devices automatically, scan the network, send packets, fingerprint devices, log in to routers, request router credentials, capture packets, or upload inventory data. The UI labels inventory findings as Manual Device Inventory or Demo Device Inventory so it does not imply automatic detection. Hostnames, IP addresses, MAC addresses, personal names, exact room locations, and serial numbers are not required. Optional MAC hints are masked before user-facing output, and optional IP hints are privacy-masked.

Router guidance is local, generic, and vendor-neutral. It does not provide exploit instructions, default router passwords, router bypass guidance, or router-login automation. Users should use their router app/admin page as the source of truth and should not enter router passwords into AI HomeGuard.

Windows local checks are designed to be read-only. They do not enable or disable Defender, Firewall, BitLocker, Remote Desktop, SMB, services, or Windows Update. They do not attempt remediation and do not require administrator privileges for baseline behavior.

macOS local checks are designed to be read-only. They read firewall, FileVault, Gatekeeper, Remote Login, listening port, and version/update visibility where available. They do not change System Settings, enable or disable sharing, request administrator credentials, or contact update services.

Linux local checks are designed to be read-only. They read common firewall, SSH, listening port, ClamAV presence, system info, update visibility, and limited disk encryption signals where available. They do not use sudo, change services, install packages, update packages, scan files, or modify disks.

The unified local device audit auto-detects the runtime platform and dispatches to one matching platform runner. It does not run Windows, macOS, and Linux checks all at once.

Runtime context is intentionally minimal. It may report detected platform, runtime environment, architecture, whether a hostname exists, notes, and limitations. It does not return hostname strings, usernames, personal paths, environment variables, browser history, documents, tokens, passwords, or secrets.

Windows, macOS, and Linux listening ports are local-only socket summaries. AI HomeGuard does not scan remote hosts or the local network. User-facing output summarizes ports and generic service hints, not usernames, file paths, process command arguments, passwords, tokens, or secrets.

Network awareness may run read-only local route or neighbor-cache visibility commands when authorized. These commands are passive local context only and do not send packets to other devices. Safe Private Network Discovery may send bounded ping traffic only to validated private IPv4 addresses when explicitly authorized. In Docker, network context and discovery may reflect the container network instead of the home network.

The local Administrators group check reports counts and categories only. Full local administrator usernames are intentionally not included in user-facing findings.

Source labels and badges are user-facing labels derived from existing report evidence and tags. They do not add backend collection, scanning, storage, or telemetry.

On unsupported platforms, local check routes return an unsupported-platform report and do not run commands for the wrong operating system. In Docker, the backend sees the container operating system rather than the host, so unified local audit results may describe the container environment. This is a runtime visibility limitation, not an upload or cloud-processing behavior. For host-level macOS checks on a Mac, run the backend natively with `uv` instead of Docker.

Local configuration should use `.env` files for private values. The repository ignores `.env` and `.env.*` while keeping `.env.example` as a safe placeholder file. Do not commit real secrets, API keys, credentials, private keys, or sensitive reports.

Vulnerability reporting should follow the Blanzy Labs organization `SECURITY.md` policy if one is present. Until then, report suspected security issues through the normal Blanzy Labs maintainer channel.
