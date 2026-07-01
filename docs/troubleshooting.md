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

Slice 1 does not require a `.env` file. If you add one locally, keep it out of git and compare it with `.env.example`.

## Browser Shows a Stale Frontend

Hard-refresh the browser tab, stop and restart the Vite dev server, or clear the browser cache for `localhost:5173`.

## Windows Checks Are Unavailable on Mac or Linux

Windows local checks only run when AI HomeGuard is running on a Windows computer. On macOS or Linux, `/reports/windows-local` returns an unsupported-platform report and does not run Windows commands.

## Local Device Audit Picked the Wrong Host

`/reports/local-device` detects the runtime where the backend process runs. If the backend is in Docker on a Mac, it usually detects Linux because the container is Linux. Run the backend directly with `uv run uvicorn app.main:app --reload` for host-level macOS checks.

## macOS Checks Are Unavailable on Windows or Linux

macOS local checks only run when AI HomeGuard is running directly on macOS. On Windows or Linux, `/reports/macos-local` returns an unsupported-platform report and does not run macOS commands.

## Linux Checks Are Unavailable on Windows or macOS

Linux local checks only run when AI HomeGuard is running on Linux. On Windows or macOS, `/reports/linux-local` returns an unsupported-platform report and does not run Linux commands.

## Docker Platform Looks Different From the Host

Docker Compose runs the backend inside a Linux container. On a Mac host, `/reports/macos-local` returns unsupported-platform output in Docker, and `/reports/linux-local` checks the container environment rather than the Mac. Run the backend natively with `uv run uvicorn app.main:app --reload` for true host macOS checks.

The `/runtime` route can help confirm what the backend sees. It returns privacy-safe runtime context without the hostname string.

## Manual Platform Routes for Debugging

Use `/reports/local-device` for normal home-user flow. The manual routes remain available for platform validation and debugging:

- `/reports/windows-local`
- `/reports/macos-local`
- `/reports/linux-local`

Manual routes return unsupported-platform reports when called from the wrong runtime.

## Combined Report Authorization Error

If `/reports/combined` returns an authorization error, the request asked to include local device audit findings without setting `acknowledged_authorization` to `true`. Local checks are read-only, but AI HomeGuard still requires explicit acknowledgement before adding them to a combined report.

## Questionnaire Required for Combined Report

If `include_questionnaire` is true, `/reports/combined` requires a questionnaire submission. Submit questionnaire answers first, or set `include_questionnaire` to false when only local device findings are wanted.

## Export Download Is Blocked

Markdown and JSON exports are created only after clicking an export button. If the browser blocks the download, check browser download permissions for `localhost:5173` or use the backend export response directly.

## Markdown Export Is Missing Findings

Markdown export renders the `HomeGuardReport` sent to `/reports/export/markdown`. If it has no findings, rebuild the combined report and confirm questionnaire answers or local audit findings were included.

## PowerShell Is Unavailable on Windows

The Windows check foundation uses read-only PowerShell commands for most checks. If PowerShell is unavailable or blocked, affected checks return `unable_to_check` instead of changing settings or requiring remediation.

## Permissions or Admin Limitations

Slice 6 does not require administrator privileges for baseline behavior. Some Windows, macOS, or Linux details may have limited visibility without elevated rights. In that case AI HomeGuard reports limited visibility or `unable_to_check` instead of requesting elevation.

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
