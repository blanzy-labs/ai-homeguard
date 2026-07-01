# AI HomeGuard Demo Script

This script uses fake/demo data where possible and keeps the safety boundaries visible throughout the walkthrough.

1. Open the app at `http://localhost:5173`.
2. Show the dashboard-first home screen and explain that AI HomeGuard is local-first, defensive, and part of the Blanzy Labs AI app family.
3. Click Run HomeGuard Check, review the safety boundaries, and keep the default guided options.
4. Answer quick questions with non-sensitive sample answers, or skip questions to show that selected local checks can still run.
5. Review the HomeGuard Dashboard: overall status, Things to Do First, what was checked, what still needs input, grouped findings, limitations, and export controls.
6. Open a finding's More Detail section and show the D3FEND-informed guidance. Explain that the guidance is educational and not official certification or a guarantee.
7. Open Try Demo to show fake sample data and the same dashboard structure.
8. Open Advanced Options and show that Demo Mode, Local Device Audit, Questionnaire Only, Local Network Awareness, Device Inventory Helper, and platform-specific checks remain available.
9. Run Local Device Audit or show the Docker/platform limitation if the backend is running in Docker.
10. Open Local Network Awareness and show that authorization is required before passive context is requested.
11. Open Device Inventory Helper and show that it is manual/demo only, with no router login and no router passwords.
12. Export Markdown and JSON only after reviewing the export copy.
13. Close by emphasizing safety boundaries: no active discovery, no Nmap, no public target scanning, no packet capture, no router login, no credential collection, no AI provider calls, no telemetry, and no sensitive persistence.

Demo reminder: use fake labels and sample answers. Do not enter real router passwords, real account identifiers, private IP/MAC values, personal names, serial numbers, or sensitive reports.
