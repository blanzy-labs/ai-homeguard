# Security and Privacy

AI HomeGuard is designed as a local-first defensive cyber hygiene app.

Slice 10 includes:

- No telemetry
- No database
- No cloud storage
- No login or account system
- No background service
- No network scanning
- No OpenAI or other AI provider calls
- Read-only Windows local audit commands only when running on Windows
- Read-only macOS local audit commands only when running on macOS
- Read-only Linux local audit commands only when running on Linux
- Unified local device audit that calls only the matching detected platform runner
- Combined reports from questionnaire findings and optional local device findings
- User-triggered Markdown and JSON exports
- Local static D3FEND-informed guidance catalog and enrichment service
- Authorization-gated passive local network awareness
- Manual/demo device inventory helper
- Generic vendor-neutral router guidance
- Privacy-safe runtime context through `/runtime`
- Unsupported-platform reports when a local audit route is called from the wrong operating system
- No sudo, administrator escalation, package installs, or remediation
- No ClamAV file scans
- No automatic device discovery
- No real router login or router credential collection
- No active network scanning, Nmap, ping sweeps, ARP scanning, port scanning, packet capture, device fingerprinting, router login, credential testing, or public target scanning
- Static fake demo data only
- Questionnaire answers kept in browser memory and submitted only to the local backend
- No questionnaire answer persistence
- No automatic report persistence

AI HomeGuard does not exploit, brute-force, capture credentials, sniff packets, or attack targets.

Future network checks will require explicit user authorization and must remain limited to systems and networks the user owns or is authorized to assess.

The `/demo/report` endpoint returns a deterministic fake report for UI development and education. It does not inspect the local system, read local security settings, enumerate devices, call an AI provider, store records, or send telemetry.

The questionnaire avoids passwords, credentials, addresses, usernames, email addresses, IP addresses, MAC addresses, and other personal identifiers. Users should not enter secrets or identifying details into questionnaire fields.

The questionnaire endpoints do not upload data to an external service and do not write answers to disk. The returned report is generated in memory from the submitted answers.

Combined report endpoints generate reports in memory. They do not write reports to disk, create a database record, upload data, call an AI provider, or add telemetry. If local device findings are requested, the request must include explicit authorization acknowledgement. If device inventory findings are requested, the request must include manual/demo inventory data.

Markdown and JSON exports are user-triggered. The backend returns export content to the browser or caller; it does not save a copy. Exported reports may contain user-provided questionnaire answers and local audit evidence, so users should review exports before sharing them.

The D3FEND-informed guidance catalog is local and static. AI HomeGuard does not fetch live MITRE data, call an AI provider, send telemetry, persist catalog lookups, or change settings while enriching guidance. Guidance is educational and may be incomplete.

Network awareness authorization is request-level only and is not stored. Slice 9 uses passive local context only. It does not accept target input fields, scan public IPs, enumerate all devices, log in to routers, request router credentials, capture packets, or test credentials. Passive neighbor information is summarized by count only. Full MAC addresses and hostnames are not shown by default.

Device inventory is manual/demo only in Slice 10. AI HomeGuard does not discover devices automatically, scan the network, send packets, fingerprint devices, log in to routers, request router credentials, capture packets, or upload inventory data. Hostnames, IP addresses, MAC addresses, personal names, exact room locations, and serial numbers are not required. Optional MAC hints are masked before user-facing output, and optional IP hints are privacy-masked.

Router guidance is local, generic, and vendor-neutral. It does not provide exploit instructions, default router passwords, router bypass guidance, or router-login automation. Users should use their router app/admin page as the source of truth and should not enter router passwords into AI HomeGuard.

Windows local checks are designed to be read-only. They do not enable or disable Defender, Firewall, BitLocker, Remote Desktop, SMB, services, or Windows Update. They do not attempt remediation and do not require administrator privileges for baseline behavior.

macOS local checks are designed to be read-only. They read firewall, FileVault, Gatekeeper, Remote Login, listening port, and version/update visibility where available. They do not change System Settings, enable or disable sharing, request administrator credentials, or contact update services.

Linux local checks are designed to be read-only. They read common firewall, SSH, listening port, ClamAV presence, system info, update visibility, and limited disk encryption signals where available. They do not use sudo, change services, install packages, update packages, scan files, or modify disks.

The unified local device audit auto-detects the runtime platform and dispatches to one matching platform runner. It does not run Windows, macOS, and Linux checks all at once.

Runtime context is intentionally minimal. It may report detected platform, runtime environment, architecture, whether a hostname exists, notes, and limitations. It does not return hostname strings, usernames, personal paths, environment variables, browser history, documents, tokens, passwords, or secrets.

Windows, macOS, and Linux listening ports are local-only socket summaries. AI HomeGuard does not scan remote hosts or the local network. User-facing output summarizes ports and generic service hints, not usernames, file paths, process command arguments, passwords, tokens, or secrets.

Network awareness may run read-only local route or neighbor-cache visibility commands when authorized. These commands are passive local context only and do not send packets to other devices. In Docker, network context may reflect the container network instead of the home network.

The local Administrators group check reports counts and categories only. Full local administrator usernames are intentionally not included in user-facing findings.

On unsupported platforms, local check routes return an unsupported-platform report and do not run commands for the wrong operating system. In Docker, the backend sees the container operating system rather than the host, so unified local audit results may describe the container environment.

Local configuration should use `.env` files for private values. The repository ignores `.env` and `.env.*` while keeping `.env.example` as a safe placeholder file. Do not commit real secrets, API keys, credentials, private keys, or sensitive reports.

Vulnerability reporting should follow the Blanzy Labs organization `SECURITY.md` policy if one is present. Until then, report suspected security issues through the normal Blanzy Labs maintainer channel.
