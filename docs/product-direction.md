# Product Direction

## Slice 13 - Dashboard-First HomeGuard Experience

Manual review after Slice 12A clarified that AI HomeGuard should move toward a dashboard-first experience for non-technical home users. Slice 13 implements the first version of that direction.

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

The Slice 13 dashboard prioritizes:

- Overall status
- Top actions
- What was checked
- What still needs user input
- What could not be checked
- Simple next steps

Still out of scope for v0.1.0:

- Public, arbitrary-target, or port-based network discovery
- Nmap
- Ping sweeps
- Port scanning
- Packet capture
- Router login
- Credential testing
- Public target scanning
- Telemetry
- Sensitive or report persistence

Follow-up dashboard work should continue reducing technical choices before value, improve the plain-English action plan, and preserve the local web-based app model. Slice 14 adds Safe Private Network Discovery under explicit authorization, private IPv4-only guardrails, no port scanning, no router login, no credential testing, no packet capture, no public target scanning, no persistence, and no telemetry. Future discovery work should stay within those guardrails.
