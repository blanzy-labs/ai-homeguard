from typing import Any

from app.checks.windows.base import (
    WindowsCheckContext,
    as_list,
    guidance,
    make_windows_finding,
    parse_json_output,
    powershell_args,
    unable_to_check_finding,
)
from app.models.enums import Category, Confidence, D3FENDGuidanceCategory, Difficulty, FindingStatus, Severity
from app.models.evidence import Evidence
from app.models.finding import Finding

PORTS_FOR_REVIEW = {
    22: "SSH",
    80: "local web server",
    443: "local web server",
    445: "SMB file sharing",
    3389: "Remote Desktop",
    5985: "WinRM",
    5986: "WinRM",
}


def check_windows_listening_ports(context: WindowsCheckContext) -> Finding:
    result = context.runner.run(
        "windows_listening_ports",
        powershell_args(
            "Get-NetTCPConnection -State Listen | "
            "Select-Object LocalAddress, LocalPort, OwningProcess | ConvertTo-Json"
        ),
        timeout_seconds=12,
        platform_name=context.platform_name,
    )
    data = parse_json_output(result)
    rows = [item for item in as_list(data) if isinstance(item, dict)]
    if not rows:
        return unable_to_check_finding(
            finding_id="windows-listening-ports-unable-to-check",
            home_title="Local listening services could not be summarized",
            technical_title="Get-NetTCPConnection unavailable",
            category=Category.NETWORK_AWARENESS,
            summary="AI HomeGuard could not read local listening TCP services.",
            result=result,
        )
    return listening_ports_finding_from_connections(rows)


def listening_ports_finding_from_connections(rows: list[dict[str, Any]]) -> Finding:
    ports = sorted({_port_number(row.get("LocalPort")) for row in rows if _port_number(row.get("LocalPort"))})
    review_ports = [port for port in ports if port in PORTS_FOR_REVIEW]
    review_labels = [f"{port} ({PORTS_FOR_REVIEW[port]})" for port in review_ports]
    status = FindingStatus.REVIEW if review_ports else FindingStatus.GOOD

    return make_windows_finding(
        finding_id="windows-listening-ports-summary",
        title="Windows local listening services",
        home_title="Local listening services need review" if review_ports else "No common remote-access ports stood out",
        technical_title="Local TCP listening port summary",
        status=status,
        severity=Severity.LOW if review_ports else Severity.INFO,
        confidence=Confidence.MEDIUM,
        category=Category.NETWORK_AWARENESS,
        summary=(
            "Common remote-access or server ports were found listening locally."
            if review_ports
            else "The local listening port summary did not find common review ports."
        ),
        why_it_matters="Listening services can be legitimate, but unused services are worth reviewing.",
        evidence=[
            Evidence(
                source="windows local check",
                method="Get-NetTCPConnection -State Listen",
                observed_value=(
                    f"{len(ports)} unique listening TCP ports; review ports: "
                    f"{', '.join(review_labels) if review_labels else 'none'}"
                ),
                expected_value="only expected local services listening",
                notes=(
                    "Local-only listening socket summary. No remote hosts were scanned. "
                    "Process command lines, file paths, and usernames were not collected."
                ),
            )
        ],
        d3fend_guidance=[
            guidance(
                D3FENDGuidanceCategory.DETECT,
                "Service exposure review",
                "Review local services that listen for connections.",
                "Understanding listening services helps identify software that may not be needed.",
                Difficulty.MEDIUM,
                20,
            ),
            guidance(
                D3FENDGuidanceCategory.HARDEN,
                "Inbound access restriction",
                "Keep the firewall enabled and restrict inbound access to trusted networks.",
                "Firewall restrictions help keep local services from being reachable unexpectedly.",
                Difficulty.MEDIUM,
                20,
            ),
        ],
        recommended_action=(
            "Review whether these listening services are expected: " + ", ".join(review_labels)
            if review_labels
            else "No immediate action from this check."
        ),
        difficulty=Difficulty.MEDIUM,
        estimated_time_minutes=20,
        requires_admin=False,
        safe_to_ignore=not review_ports,
        tags=["listening-ports", "network-awareness"],
    )


def _port_number(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
