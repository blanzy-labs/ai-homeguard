# AI HomeGuard v0.1.0 Release Checklist

Release target: v0.1.0 - Local Home Security Audit MVP

## Project Metadata

- [x] Repo name confirmed: `ai-homeguard`
- [x] Display name confirmed: AI HomeGuard
- [x] App family confirmed: Blanzy Labs
- [x] Repo URL confirmed: `https://github.com/blanzy-labs/ai-homeguard`
- [x] Default branch confirmed: `main`
- [x] Release version set to `0.1.0`
- [x] `.env` and `.env.*` ignored
- [x] `.env.example` committed with placeholders only

## Documentation

- [x] README finalized for v0.1.0
- [x] Slice 13 dashboard-first product direction implemented and documented
- [x] Disclaimer complete
- [x] Security and privacy notes complete
- [x] Architecture notes complete
- [x] Local install notes complete
- [x] Troubleshooting notes complete
- [x] Release notes ready: `docs/release-notes/v0.1.0.md`
- [x] Validation document ready: `docs/validation/v0.1.0-validation.md`
- [x] Demo script ready: `docs/demo-script.md`
- [x] Sample scenarios ready: `docs/sample-scenarios.md`

## Validation

- [x] Backend tests pass
- [x] Frontend tests pass
- [x] Frontend build passes
- [x] Docker build passes
- [x] Docker smoke checks pass
- [x] Endpoint smoke checks pass
- [x] Dashboard-first smoke items documented in `docs/validation/slice-13-validation.md`
- [x] Safe Private Network Discovery validation documented in `docs/validation/slice-14-validation.md`
- [ ] Manual UI smoke check complete - owner manual smoke found release-blocking issues; Slice 12A fixes require owner retest
- [x] Release checklist result recorded in validation document

## Safety and Privacy

- [x] No secrets found
- [x] No `.env` committed
- [x] Safe Private Network Discovery limited to explicit authorization and private IPv4 local ranges
- [x] Public target rejection validated
- [x] Hostname/domain target rejection validated
- [x] Large subnet limit validated
- [x] No Nmap execution path
- [x] No arbitrary ping sweep path
- [x] No port scanning other devices
- [x] No packet capture path
- [x] No router login flow
- [x] No credential collection
- [x] No router password fields
- [x] No public IP scanning
- [x] No target scan fields
- [x] No OpenAI/API provider calls
- [x] No telemetry
- [x] No database/report/questionnaire/inventory persistence
- [x] Browser storage limited to versioned safety acknowledgement and low-risk Advanced Options drawer state only
- [x] No report auto-save to disk
- [x] No remediation/settings changes
- [x] No sudo/admin requirement for baseline behavior
- [x] No automatic-repair buttons
- [x] No certification, guarantee, or compromise-style overclaiming language
- [x] D3FEND guidance labeled educational/informed
- [x] Exports warn users to review before sharing
- [x] Full MAC addresses and hostnames are not exposed by default
- [x] MAC hints are masked in discovery output
- [x] Docker/container discovery limitation documented

## Feature Scope

- [x] Demo Mode included
- [x] Safety-first guided UX included
- [x] Home security questionnaire included
- [x] Questionnaire-derived findings included
- [x] Read-only Windows local audit foundation included
- [x] Read-only macOS local audit foundation included
- [x] Read-only Linux local audit foundation included
- [x] Unified local device audit with platform auto-detection included
- [x] Combined HomeGuard report included
- [x] Markdown and JSON export included
- [x] D3FEND-informed defensive guidance catalog included
- [x] Passive local network awareness foundation included
- [x] Safe Private Network Discovery included
- [x] Manual/demo device inventory helper included
- [x] Router guidance included
- [x] Report review experience included
- [x] Dashboard-first Run HomeGuard Check experience included

## GitHub Release

- [x] GitHub metadata set
- [x] v0.1.0 tag absent before creation
- [x] v0.1.0 release absent before creation
- [ ] Final release commit pushed to `main`
- [ ] Annotated tag `v0.1.0` created and pushed
- [ ] GitHub release created from `docs/release-notes/v0.1.0.md`
- [ ] Final release verification complete
