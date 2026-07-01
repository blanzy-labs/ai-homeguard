import re
from typing import Iterable

from app.checks.linux.base import (
    LinuxCheckContext,
    command_missing_or_failed,
    command_text,
    guidance,
    make_linux_finding,
    unable_to_check_finding,
)
from app.models.enums import Category, Confidence, D3FENDGuidanceCategory, Difficulty, FindingStatus, Severity
from app.models.evidence import Evidence
from app.models.finding import Finding

PORTS_FOR_REVIEW = {
    22: "SSH",
    80: "local web server",
    443: "local web server",
    3306: "MySQL or MariaDB",
    5432: "PostgreSQL",
    5900: "VNC",
    6379: "Redis",
    8000: "developer web service",
    5173: "developer web service",
}


def check_linux_listening_ports(context: LinuxCheckContext) -> Finding:
    result = context.runner.run(
        "linux_listening_ports_ss",
        ["ss", "-tuln"],
        timeout_seconds=12,
        platform_name=context.platform_name,
    )
    if not command_missing_or_failed(result):
        return listening_ports_finding_from_ports(parse_ss_listening_ports(command_text(result)))

    fallback = context.runner.run(
        "linux_listening_ports_netstat",
        ["netstat", "-tuln"],
        timeout_seconds=12,
        platform_name=context.platform_name,
    )
    if command_missing_or_failed(fallback):
        return unable_to_check_finding(
            finding_id="linux-listening-ports-unable-to-check",
            home_title="Local listening services could not be summarized",
            technical_title="ss and netstat unavailable",
            category=Category.NETWORK_AWARENESS,
            summary="AI HomeGuard could not summarize local listening TCP/UDP services.",
            result=fallback,
        )
    return listening_ports_finding_from_ports(parse_netstat_listening_ports(command_text(fallback)))


def listening_ports_finding_from_ports(port_values: Iterable[int]) -> Finding:
    ports = sorted({port for port in port_values if 0 < port <= 65535})
    review_ports = [port for port in ports if port in PORTS_FOR_REVIEW]
    review_labels = [f"{port} ({PORTS_FOR_REVIEW[port]})" for port in review_ports]
    status = FindingStatus.REVIEW if review_ports else FindingStatus.GOOD

    return make_linux_finding(
        finding_id="linux-listening-ports-summary",
        title="Linux local listening services",
        home_title="Local listening services need review" if review_ports else "No common review ports stood out",
        technical_title="Local listening port summary",
        status=status,
        severity=Severity.LOW if review_ports else Severity.INFO,
        confidence=Confidence.MEDIUM,
        category=Category.NETWORK_AWARENESS,
        summary=(
            "Common remote-access, database, or local server ports were found listening locally."
            if review_ports
            else "The local listening port summary did not find common review ports."
        ),
        why_it_matters="Listening services can be legitimate, but unused services are worth reviewing.",
        evidence=[
            Evidence(
                source="Linux local check",
                method="ss -tuln or netstat -tuln",
                observed_value=(
                    f"{len(ports)} unique listening ports; review ports: "
                    f"{', '.join(review_labels) if review_labels else 'none'}"
                ),
                expected_value="only expected local services listening",
                notes=(
                    "Local-only listening socket summary. No remote hosts were scanned. "
                    "Usernames, file paths, and process command arguments were not collected or reported."
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
        safe_to_ignore=not review_ports,
        tags=["listening-ports", "network-awareness"],
    )


def parse_ss_listening_ports(output: str) -> list[int]:
    ports: list[int] = []
    for line in output.splitlines():
        if "LISTEN" not in line:
            continue
        parts = line.split()
        if len(parts) < 5:
            continue
        port = _port_from_endpoint(parts[4])
        if port is not None:
            ports.append(port)
    return ports


def parse_netstat_listening_ports(output: str) -> list[int]:
    ports: list[int] = []
    for line in output.splitlines():
        if "LISTEN" not in line:
            continue
        parts = line.split()
        if len(parts) < 4:
            continue
        port = _port_from_endpoint(parts[3])
        if port is not None:
            ports.append(port)
    return ports


def _port_from_endpoint(endpoint: str) -> int | None:
    cleaned = endpoint.strip("[]")
    match = re.search(r"[:.](\d+)$", cleaned)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None
