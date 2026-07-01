# Security and Privacy

AI HomeGuard is designed as a local-first defensive cyber hygiene app.

Slice 5 includes:

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
- Unsupported-platform reports when a local audit route is called from the wrong operating system
- No sudo, administrator escalation, package installs, or remediation
- No ClamAV file scans
- No real router or network checks
- Static fake demo data only
- Questionnaire answers kept in browser memory and submitted only to the local backend
- No questionnaire answer persistence

AI HomeGuard does not exploit, brute-force, capture credentials, sniff packets, or attack targets.

Future network checks will require explicit user authorization and must remain limited to systems and networks the user owns or is authorized to assess.

The `/demo/report` endpoint returns a deterministic fake report for UI development and education. It does not inspect the local system, read local security settings, enumerate devices, call an AI provider, store records, or send telemetry.

The questionnaire avoids passwords, credentials, addresses, usernames, email addresses, IP addresses, MAC addresses, and other personal identifiers. Users should not enter secrets or identifying details into questionnaire fields.

The questionnaire endpoints do not upload data to an external service and do not write answers to disk. The returned report is generated in memory from the submitted answers.

Windows local checks are designed to be read-only. They do not enable or disable Defender, Firewall, BitLocker, Remote Desktop, SMB, services, or Windows Update. They do not attempt remediation and do not require administrator privileges for baseline behavior.

macOS local checks are designed to be read-only. They read firewall, FileVault, Gatekeeper, Remote Login, listening port, and version/update visibility where available. They do not change System Settings, enable or disable sharing, request administrator credentials, or contact update services.

Linux local checks are designed to be read-only. They read common firewall, SSH, listening port, ClamAV presence, system info, update visibility, and limited disk encryption signals where available. They do not use sudo, change services, install packages, update packages, scan files, or modify disks.

Windows, macOS, and Linux listening ports are local-only socket summaries. AI HomeGuard does not scan remote hosts or the local network. User-facing output summarizes ports and generic service hints, not usernames, file paths, process command arguments, passwords, tokens, or secrets.

The local Administrators group check reports counts and categories only. Full local administrator usernames are intentionally not included in user-facing findings.

On unsupported platforms, local check routes return an unsupported-platform report and do not run commands for the wrong operating system. In Docker, the backend sees the container operating system rather than the host.

Local configuration should use `.env` files for private values. The repository ignores `.env` and `.env.*` while keeping `.env.example` as a safe placeholder file. Do not commit real secrets, API keys, credentials, private keys, or sensitive reports.

Vulnerability reporting should follow the Blanzy Labs organization `SECURITY.md` policy if one is present. Until then, report suspected security issues through the normal Blanzy Labs maintainer channel.
