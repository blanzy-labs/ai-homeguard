# Troubleshooting

## Docker Is Not Running

Start Docker Desktop or the Docker daemon, then retry:

```bash
docker compose build
```

## Port 8000 or 5173 Is Already In Use

Stop the process using the port or adjust the port mapping in `docker-compose.yml`.

## uv Is Missing

Install uv using the official uv installation instructions or Homebrew, then confirm:

```bash
uv --version
```

## pnpm Is Missing

Enable pnpm with Corepack or install it through the approved local package manager, then confirm:

```bash
pnpm --version
```

## Frontend Cannot Reach Backend

Confirm the backend is running:

```bash
curl http://localhost:8000/health
```

If the backend is on a non-default URL, set `VITE_API_BASE_URL` for the frontend.

The footer status panel shows `Backend unavailable` when the browser cannot reach the local API. Confirm the backend is running on port 8000, then refresh the frontend.

## Report Generation Failed

Report screens show a text-visible error when a route returns a validation error or the backend is unavailable. Check the relevant API directly, then retry from the frontend:

```bash
curl http://localhost:8000/demo/report
curl http://localhost:8000/reports/local-device
curl http://localhost:8000/knowledge/d3fend-guidance
```

For combined reports, confirm required acknowledgements are checked and that Device Inventory Helper has at least one manual device or loaded demo inventory before including inventory findings.

## Backend Health Check Fails

Run the backend directly and inspect the terminal output:

```bash
cd backend
uv run uvicorn app.main:app --reload
```

Then retry:

```bash
curl http://localhost:8000/health
```

## .env Is Not Loaded

v0.1.0 does not require a `.env` file. If you add one locally, keep it out of git and compare it with `.env.example`.

## Browser Shows a Stale Frontend

Hard-refresh the browser tab, stop and restart the Vite dev server, or clear the browser cache for `localhost:5173`.

## Safety Acknowledgement Appears Again

AI HomeGuard stores only the versioned safety acknowledgement in `sessionStorage` for the current browser session. It does not store questionnaire answers, reports, device inventory entries, exports, or telemetry. If you close the browser session, clear site data, or use a private browsing window, the acknowledgement may appear again.

## Windows Checks Are Unavailable on Mac or Linux

Windows local checks only run when AI HomeGuard is running on a Windows computer. On macOS or Linux, `/reports/windows-local` returns an unsupported-platform report and does not run Windows commands.

## Local Device Audit Picked the Wrong Host

`/reports/local-device` detects the runtime where the backend process runs. If the backend is in Docker on a Mac, it usually detects Linux because the container is Linux. That is expected container visibility, not proof that the Mac host is Linux. Run the backend directly with `uv run uvicorn app.main:app --reload` for host-level macOS checks.

## macOS Checks Are Unavailable on Windows or Linux

macOS local checks only run when AI HomeGuard is running directly on macOS. On Windows or Linux, `/reports/macos-local` returns an unsupported-platform report and does not run macOS commands.

## Linux Checks Are Unavailable on Windows or macOS

Linux local checks only run when AI HomeGuard is running on Linux. On Windows or macOS, `/reports/linux-local` returns an unsupported-platform report and does not run Linux commands.

## Unsupported Platform Result

Unsupported-platform results are expected when a platform-specific route is opened from the wrong operating system or when the runtime cannot be matched safely. AI HomeGuard returns `unable_to_check` findings instead of running commands for the wrong platform.

## Docker Platform Looks Different From the Host

Docker Compose runs the backend inside a Linux container. On a Mac host, `/runtime` and `/reports/local-device` may report Linux/container runtime visibility. `/reports/macos-local` returns unsupported-platform output in Docker, and `/reports/linux-local` checks the container environment rather than the Mac. Run the backend natively with `uv run uvicorn app.main:app --reload` for true host-level macOS checks.

The `/runtime` route can help confirm what the backend sees. It returns privacy-safe runtime context without the hostname string.

## Manual Platform Routes for Debugging

Use `/reports/local-device` for normal home-user flow. The manual routes remain available for platform validation and debugging:

- `/reports/windows-local`
- `/reports/macos-local`
- `/reports/linux-local`

Manual routes return unsupported-platform reports when called from the wrong runtime.

## Combined Report Authorization Error

If `/reports/combined` returns an authorization error, the request asked to include local device audit findings without setting `acknowledged_authorization` to `true`. Local checks are read-only, but AI HomeGuard still requires explicit acknowledgement before adding them to a combined report.

## Combined Report Device Inventory Error

If `/reports/combined` says a device inventory submission is required, the request set `include_device_inventory` to true without sending `device_inventory_submission`. In the frontend, add at least one manual device or load the fake demo inventory before including Device Inventory Helper findings.

## Questionnaire Required for Combined Report

If `include_questionnaire` is true, `/reports/combined` requires a questionnaire submission. Submit questionnaire answers first, or set `include_questionnaire` to false when only local device findings are wanted.

## Export Download Is Blocked

Markdown and JSON exports are created only after clicking an export button. If the browser blocks the download, check browser download permissions for `localhost:5173` or use the backend export response directly.

## Export Failed

Export status appears in the report review panel after clicking Export Markdown or Export JSON. If export fails, confirm the backend is running and rebuild the report before exporting again. Exports are not saved automatically, so review the downloaded file before sharing.

## Markdown Export Is Missing Findings

Markdown export renders the `HomeGuardReport` sent to `/reports/export/markdown`. If it has no findings, rebuild the combined report and confirm questionnaire answers or local audit findings were included.

## Filters Hide All Findings

The report review filters can hide findings by status, platform, evidence source, or the Show good findings checkbox. Set Status, Platform, and Evidence source back to their `All` options and turn on Show good findings to restore the full finding list.

## Technical Details Are Collapsed

Finding cards keep technical details and evidence collapsed by default. Open the Technical details and evidence toggle on a finding to review evidence, technical title, and educational ATT&CK context when present.

## Guidance Catalog Route Is Unavailable

Confirm the backend is running, then call:

```bash
curl http://localhost:8000/knowledge/d3fend-guidance
```

The guidance catalog is bundled locally. It does not need internet access or a live MITRE connection.

## Report Has No Defensive Guidance

If a custom or future finding has no `d3fend_guidance`, check whether its category, platform, or tags match the local catalog. Unknown categories can still render, but they may not receive inferred guidance until a mapping is added.

## Missing Guidance Entry

If `/knowledge/d3fend-guidance/{guidance_id}` returns 404, confirm the ID is one of the bundled catalog IDs returned by `/knowledge/d3fend-guidance`.

## Network Awareness Authorization Required

`POST /reports/network-awareness` requires `acknowledged: true` and `scope: home_network` or `demo`. Authorization is request-level only and is not stored.

## Docker Network Context Looks Different

When the backend runs in Docker, passive network context may describe the container network rather than the host or home network. Run the backend natively for host-level local network context.

## Network Awareness Shows No Passive Device Entries

v0.1.0 does not actively discover devices. Passive local caches can be empty or incomplete. Your router app or admin page may show a more complete device list. Active private-network discovery is deferred to Slice 13 - Safe Private Network Discovery, which must require explicit authorization, private-network-only guardrails, no credential testing, no exploit logic, no packet capture, and no router login.

## Device Inventory Helper Has No Devices

v0.1.0 device inventory is manual/demo only. Add devices from your router app/device list or click the demo inventory button. AI HomeGuard does not automatically discover devices, scan the network, or log in to your router.

## Optional Device Hints Look Masked

Optional IP and MAC hints are privacy-masked by the backend. This is expected. Exact IP addresses, full MAC addresses, hostnames, serial numbers, exact room locations, and personal names are not required for the inventory helper.

## Router Guidance Does Not Match My Router Menu

Router menus vary by manufacturer and ISP. AI HomeGuard provides generic guidance only and does not provide default router passwords, router-login automation, or bypass instructions. Use your router app or router/ISP documentation as the source of truth.

## Router App Does Not Show Device Names

Some routers show generic labels, manufacturer names, randomized identifiers, or blank names. This is normal. Use calm labels in AI HomeGuard, such as family phone, smart TV, printer, guest device, or unknown device.

## Unknown Devices May Be Normal

An unknown router entry is a review item, not proof of compromise. It may be a phone with MAC randomization, a powered-off device with an old lease, a smart-home device, a guest device, or a renamed device. Identify it before blocking or removing it.

## Duplicate or Old Router Device Entries

Routers may keep old device entries after a device leaves the network. Compare last-seen information in the router app if available. AI HomeGuard does not treat duplicate or stale entries as evidence of compromise by itself.

## Phone MAC Randomization Creates New Entries

Modern phones and tablets may use private or randomized Wi-Fi addresses. This can make the same device appear as a new router entry. Check the device Wi-Fi settings and router app before deciding a device is unknown.

## Guest Wi-Fi Is Not Available

Some routers or ISP-managed gateways do not support guest Wi-Fi or isolation. If guest Wi-Fi is unavailable, keep device firmware updated, use strong Wi-Fi passwords, and review unknown devices regularly.

## Device Inventory Is Not Saved After Refresh

v0.1.0 does not persist manual inventory data. If you refresh the browser, restart the frontend, or close the session, re-enter the inventory or load the fake demo inventory again.

## Review Exports Before Sharing

Markdown and JSON exports are user-triggered and may include questionnaire answers or manual inventory labels. Review exported reports before sharing them outside your household.

## Platform Network Command Is Unavailable

If local route or neighbor-cache commands are unavailable, AI HomeGuard returns limited visibility instead of requesting sudo/admin rights or running alternative active discovery.

## Public Scope Rejected

AI HomeGuard does not support public target scanning. Future target/range inputs must pass private/local guardrails, and v0.1.0 does not expose target inputs.

## PowerShell Is Unavailable on Windows

The Windows check foundation uses read-only PowerShell commands for most checks. If PowerShell is unavailable or blocked, affected checks return `unable_to_check` instead of changing settings or requiring remediation.

## Permissions or Admin Limitations

v0.1.0 does not require administrator privileges for baseline behavior. Some Windows, macOS, or Linux details may have limited visibility without elevated rights. In that case AI HomeGuard reports limited visibility or `unable_to_check` instead of requesting elevation.

## Endpoint Security Blocks PowerShell

Some endpoint security tools restrict PowerShell. AI HomeGuard treats blocked read-only commands as limited visibility and does not attempt to bypass security controls.

## BitLocker Check Is Unavailable

If `Get-BitLockerVolume` is unavailable, AI HomeGuard attempts a read-only `manage-bde -status` fallback on Windows. If neither is available, the encryption check returns `unable_to_check`.

## Firewall Command Is Unavailable

If `Get-NetFirewallProfile` is unavailable, the firewall check returns `unable_to_check`. Review Windows Security manually if firewall status matters for your setup.

On macOS, if `socketfilterfw` is unavailable, the firewall check returns `unable_to_check`. On Linux, if UFW and firewalld visibility are both unavailable, the firewall check returns `unable_to_check`.

## FileVault or Gatekeeper Check Is Unavailable

If `fdesetup status` or `spctl --status` is unavailable or returns limited visibility, the related macOS check returns `unable_to_check`. Review FileVault or app security settings manually in macOS System Settings if needed.

## Remote Login or SSH Status Is Unavailable

If `systemsetup -getremotelogin` is unavailable on macOS, Remote Login returns `unable_to_check`. If `systemctl` and `service` are unavailable on Linux, SSH status returns `unable_to_check`. AI HomeGuard does not start, stop, enable, or disable services.

## Listening Port Tools Are Unavailable

macOS uses `lsof` with a `netstat` fallback. Linux uses `ss` with a `netstat` fallback. If those tools are unavailable, the listening-port check returns `unable_to_check`. These checks summarize local ports only and do not scan the network.

## ClamAV Is Missing on Linux

If `clamscan --version` and `freshclam --version` are unavailable, AI HomeGuard returns an informational review finding. It does not install ClamAV and does not run file scans.

## Linux Disk Encryption Is Unclear

The Linux disk encryption check uses limited read-only `lsblk -f` visibility. If no LUKS marker is visible, AI HomeGuard returns `unable_to_check` rather than claiming encryption is disabled.
