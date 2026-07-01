# AI HomeGuard Demo Script

This script uses fake/demo data where possible and keeps the safety boundaries visible throughout the walkthrough.

1. Open the app at `http://localhost:5173`.
2. Show the safety-first home screen and explain that AI HomeGuard is local-first, defensive, and part of the Blanzy Labs AI app family.
3. Open Demo Mode.
4. Review the sample report summary, top actions, findings, evidence source labels, limitations, and safety notes.
5. Open a finding's technical details and show the D3FEND-informed guidance. Explain that the guidance is educational and not official certification or a guarantee.
6. Return to modes and run the Home Security Questionnaire flow with non-sensitive sample answers.
7. Run Local Device Audit or show the Docker/platform limitation if the backend is running in Docker.
8. Open Local Network Awareness and show that authorization is required before passive context is requested.
9. Open Device Inventory Helper and show that it is manual/demo only, with no router login and no router passwords.
10. Build the Full HomeGuard Report with selected sources.
11. Export Markdown and JSON only after reviewing the export copy.
12. Close by emphasizing safety boundaries: no active discovery, no Nmap, no public target scanning, no packet capture, no router login, no credential collection, no AI provider calls, no telemetry, and no persistence.

Demo reminder: use fake labels and sample answers. Do not enter real router passwords, real account identifiers, private IP/MAC values, personal names, serial numbers, or sensitive reports.

