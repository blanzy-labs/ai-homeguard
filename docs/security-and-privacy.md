# Security and Privacy

AI HomeGuard is designed as a local-first defensive cyber hygiene app.

Slice 2 includes:

- No telemetry
- No database
- No cloud storage
- No login or account system
- No background service
- No network scanning
- No OpenAI or other AI provider calls
- No local audit commands
- No real Windows, macOS, Linux, router, or network checks
- Static fake demo data only

AI HomeGuard does not exploit, brute-force, capture credentials, sniff packets, or attack targets.

Future network checks will require explicit user authorization and must remain limited to systems and networks the user owns or is authorized to assess.

The `/demo/report` endpoint returns a deterministic fake report for UI development and education. It does not inspect the local system, read local security settings, enumerate devices, call an AI provider, store records, or send telemetry.

Local configuration should use `.env` files for private values. The repository ignores `.env` and `.env.*` while keeping `.env.example` as a safe placeholder file. Do not commit real secrets, API keys, credentials, private keys, or sensitive reports.

Vulnerability reporting should follow the Blanzy Labs organization `SECURITY.md` policy if one is present. Until then, report suspected security issues through the normal Blanzy Labs maintainer channel.
