import re
from typing import Iterable

from app.checks.macos.base import (
    MacOSCheckContext,
    command_text,
    command_unavailable,
    guidance,
    make_macos_finding,
    unable_to_check_finding,
)
from app.models.enums import Category, Confidence, D3FENDGuidanceCategory, Difficulty, FindingStatus, Severity
from app.models.evidence import Evidence
from app.models.finding import Finding

PORTS_FOR_REVIEW = {
    22: "SSH",
    80: "local web server",
    443: "local web server",
    3283: "Apple Remote Desktop",
    5000: "developer web service",
    5173: "developer web service",
    5900: "Screen Sharing or VNC",
    8000: "developer web service",
}


def check_macos_listening_ports(context: MacOSCheckContext) -> Finding:
    result = context.runner.run(
        "macos_listening_ports_lsof",
        ["lsof", "-nP", "-iTCP", "-sTCP:LISTEN"],
        timeout_seconds=12,
        platform_name=context.platform_name,
    )
    if not command_unavailable(result):
        ports = parse_lsof_listening_ports(command_text(result))
        return listening_ports_finding_from_ports(ports)

    fallback = context.runner.run(
        "macos_listening_ports_netstat",
        ["netstat", "-anv", "-p", "tcp"],
        timeout_seconds=12,
        platform_name=context.platform_name,
    )
    if command_unavailable(fallback):
        return unable_to_check_finding(
            finding_id="macos-listening-ports-unable-to-check",
            home_title="Local listening services could not be summarized",
            technical_title="lsof and netstat unavailable",
            category=Category.NETWORK_AWARENESS,
            summary="AI HomeGuard could not summarize local listening TCP services.",
            result=fallback,
        )
    return listening_ports_finding_from_ports(parse_netstat_listening_ports(command_text(fallback)))


def listening_ports_finding_from_ports(port_values: Iterable[int]) -> Finding:
    ports = sorted({port for port in port_values if 0 < port <= 65535})
    review_ports = [port for port in ports if port in PORTS_FOR_REVIEW]
    review_labels = [f"{port} ({PORTS_FOR_REVIEW[port]})" for port in review_ports]
    status = FindingStatus.REVIEW if review_ports else FindingStatus.GOOD

    return make_macos_finding(
        finding_id="macos-listening-ports-summary",
        title="macOS local listening services",
        home_title="Local listening services need review" if review_ports else "No common review ports stood out",
        technical_title="Local TCP listening port summary",
        status=status,
        severity=Severity.LOW if review_ports else Severity.INFO,
        confidence=Confidence.MEDIUM,
        category=Category.NETWORK_AWARENESS,
        summary=(
            "Common remote-access or local server ports were found listening locally."
            if review_ports
            else "The local listening port summary did not find common review ports."
        ),
        why_it_matters="Listening services can be legitimate, but unused services are worth reviewing.",
        evidence=[
            Evidence(
                source="macOS local check",
                method="lsof -nP -iTCP -sTCP:LISTEN or netstat -anv -p tcp",
                observed_value=(
                    f"{len(ports)} unique listening TCP ports; review ports: "
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
                "Keep the firewall enabled and limit sharing services to trusted networks.",
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


def parse_lsof_listening_ports(output: str) -> list[int]:
    ports: list[int] = []
    for line in output.splitlines():
        if "LISTEN" not in line or "TCP" not in line:
            continue
        match = re.search(r"TCP\s+.*:(\d+)\s+\(LISTEN\)", line)
        if match:
            ports.append(int(match.group(1)))
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
    match = re.search(r"[:.](\d+)$", endpoint)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None
