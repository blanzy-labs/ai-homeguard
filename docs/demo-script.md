# AI HomeGuard Demo Script

This script uses fake/demo data where possible and keeps the safety boundaries visible throughout the walkthrough.

1. Open the app at `http://localhost:5173`.
2. Show the dashboard-first home screen and explain that AI HomeGuard is local-first, defensive, and part of the Blanzy Labs AI app family.
3. Click Run HomeGuard Check, review the safety boundaries, and keep the default guided options.
4. Answer quick questions with non-sensitive sample answers, or skip questions to show that selected local checks can still run.
5. Review the HomeGuard Dashboard: overall status, Things to Do First, what was checked, what still needs input, grouped findings, limitations, and export controls.
6. Rerun the guided setup with Find devices on my home network selected, show the private-network acknowledgements, and explain that discovery is private IPv4 only with no ports, no router login, no passwords, and no packet capture.
7. Open a finding's More Detail section and show the D3FEND-informed guidance. Explain that the guidance is educational and not official certification or a guarantee.
8. Open Try Demo to show fake sample data and the same dashboard structure.
9. Open Advanced Options and show that Demo Mode, Local Device Audit, Questionnaire Only, Local Network Awareness, Device Inventory Helper, and platform-specific checks remain available.
10. Run Local Device Audit or show the Docker/platform limitation if the backend is running in Docker.
11. Open Local Network Awareness and show that authorization is required before passive context is requested.
12. Open Device Inventory Helper and show that it is manual/demo only, with no router login and no router passwords.
13. Export Markdown and JSON only after reviewing the export copy.
14. Close by emphasizing safety boundaries: no Nmap, no public target scanning, no port scanning, no packet capture, no router login, no credential collection, no AI provider calls, no telemetry, and no sensitive persistence.

Demo reminder: use fake labels and sample answers. Do not enter real router passwords, real account identifiers, private IP/MAC values, personal names, serial numbers, or sensitive reports.
