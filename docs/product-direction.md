# Product Direction

## Slice 13 - Dashboard-First HomeGuard Experience

Manual review after Slice 12A clarified that AI HomeGuard should move toward a dashboard-first experience for non-technical home users.

Most users should not need to choose between technical modules. The primary product path should feel like one guided home safety check, with a clear call to action such as `Run HomeGuard Check` or `Full HomeGuard Report`.

Dashboard-first goals:

- Make the recommended path obvious on the home page.
- Present Demo Mode, Local Device Audit, Questionnaire, Local Network Awareness, and Device Inventory Helper as parts of one HomeGuard product flow.
- De-emphasize advanced/manual platform checks.
- Avoid forcing users to make technical decisions before seeing value.
- Avoid repeated safety acknowledgement during the same browser session.
- Avoid implementation details such as development slice language in user-facing UI.
- Keep the app local web-based for consistent UI across platforms.
- Keep backend platform-specific checks behind the product flow.

The dashboard should prioritize:

- Overall status
- Top actions
- What was checked
- What still needs user input
- What could not be checked
- Simple next steps

Out of scope for v0.1.0 and Slice 12A:

- Full dashboard redesign
- Active network discovery
- Nmap
- Ping sweeps
- Port scanning
- Packet capture
- Router login
- Credential testing
- Public target scanning
- Telemetry
- New persistence

Slice 13 should treat dashboard-first UX as a product direction alongside the deferred Safe Private Network Discovery research. Any future discovery work must remain explicitly authorized, private-network-only, user-controlled, transparent, and free of credential testing, exploit logic, packet capture, router login, public target scanning, and telemetry.
