# Sample Scenarios

These scenarios are fake examples for demos, docs, and validation. They do not include real IP addresses, MAC addresses, hostnames, account names, serial numbers, or router credentials.

## Family Laptop Check

A household wants to review a laptop before school starts. They run the Home Security Questionnaire, then optionally run the Local Device Audit. AI HomeGuard summarizes read-only local check results, notes any platform/runtime limitations, and suggests calm next steps such as reviewing updates, local firewall status, disk encryption, and backup habits.

## Router/Device List Review

A family opens their router app and sees several device entries. They use Device Inventory Helper with broad labels such as `family phone`, `smart TV`, `printer`, and `guest device`. AI HomeGuard labels findings as manual inventory and reminds the user that the router app is the source of truth.

## Smart TV and IoT Review

A household notices smart TVs, speakers, cameras, and similar devices on the main network. They use the inventory helper to mark those devices as limited-trust or unknown-update-status. AI HomeGuard suggests considering guest Wi-Fi or isolation where practical and reviewing firmware/update settings.

## Backup Readiness Review

A user is unsure whether important files are backed up. The questionnaire produces a backup readiness finding and recommends setting up regular backups and testing a harmless restore. The report does not inspect files or upload data.

## Docker Limitation Example

The backend runs in Docker on a Mac. The unified local audit reports Linux/container context because the backend sees the container runtime, not the macOS host. AI HomeGuard documents this limitation and recommends running the backend natively for host-level macOS checks.

## Deferred Network Discovery

A household wants AI HomeGuard to list devices automatically. v0.1.0 does not run active discovery, Nmap, ping sweeps, port scans, packet capture, router login, credential testing, or public target scanning. Slice 13 - Safe Private Network Discovery is the deferred follow-up for explicit, user-controlled private-network discovery with strict guardrails.

## Unsupported Platform Example

A user opens the Windows Device Audit while the backend is running on macOS or Linux. AI HomeGuard returns an unsupported-platform result instead of running Windows commands on the wrong operating system.
