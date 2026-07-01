from app.checks.linux.base import (
    LinuxCheckContext,
    command_text,
    guidance,
    make_linux_finding,
    unable_to_check_finding,
)
from app.core.command_runner import CommandResult
from app.models.enums import Category, Confidence, D3FENDGuidanceCategory, Difficulty, FindingStatus, Severity
from app.models.evidence import Evidence
from app.models.finding import Finding


def check_linux_firewall(context: LinuxCheckContext) -> Finding:
    results = [
        context.runner.run(
            "linux_firewall_ufw",
            ["ufw", "status"],
            timeout_seconds=10,
            platform_name=context.platform_name,
        ),
        context.runner.run(
            "linux_firewall_firewall_cmd",
            ["firewall-cmd", "--state"],
            timeout_seconds=10,
            platform_name=context.platform_name,
        ),
        context.runner.run(
            "linux_firewall_firewalld_active",
            ["systemctl", "is-active", "firewalld"],
            timeout_seconds=10,
            platform_name=context.platform_name,
        ),
    ]
    finding = firewall_finding_from_results(results)
    if finding is None:
        return unable_to_check_finding(
            finding_id="linux-firewall-unable-to-check",
            home_title="Linux firewall status could not be checked",
            technical_title="ufw/firewalld status unavailable",
            category=Category.DEVICE_POSTURE,
            summary="AI HomeGuard could not read Linux firewall status from common tools.",
            result=results[-1],
        )
    return finding


def firewall_finding_from_results(results: list[CommandResult]) -> Finding | None:
    states = [_firewall_signal(result) for result in results]
    usable_states = [state for state in states if state != "unavailable"]
    if not usable_states:
        return None

    active = "active" in usable_states
    status = FindingStatus.GOOD if active else FindingStatus.FIX_SOON
    evidence_summary = "; ".join(
        f"{result.command_name.replace('linux_firewall_', '')}: {state}"
        for result, state in zip(results, states, strict=False)
    )

    return make_linux_finding(
        finding_id="linux-firewall-status",
        title="Linux host firewall status",
        home_title="A Linux firewall appears active" if active else "Linux firewall needs review",
        technical_title="ufw/firewalld activity status",
        status=status,
        severity=Severity.INFO if active else Severity.MEDIUM,
        confidence=Confidence.MEDIUM,
        category=Category.DEVICE_POSTURE,
        summary=(
            "A common Linux host firewall appears active."
            if active
            else "Common Linux host firewall tools appear inactive where visible."
        ),
        why_it_matters="A host firewall helps limit unsolicited inbound connections to the device.",
        evidence=[
            Evidence(
                source="Linux local check",
                method="ufw status; firewall-cmd --state; systemctl is-active firewalld",
                observed_value=evidence_summary,
                expected_value="a host firewall active when available",
                notes="Read-only firewall status checks. No firewall rules or settings were changed.",
            )
        ],
        d3fend_guidance=[
            guidance(
                D3FENDGuidanceCategory.HARDEN,
                "Host firewall",
                "Keep a host firewall enabled unless another trusted control handles inbound filtering.",
                "Host firewall filtering reduces unexpected inbound access.",
                Difficulty.MEDIUM,
                15,
            )
        ],
        recommended_action=(
            "No immediate action from this check."
            if active
            else "Review your distribution firewall settings, such as UFW or firewalld."
        ),
        difficulty=Difficulty.MEDIUM,
        estimated_time_minutes=15,
        safe_to_ignore=active,
        tags=["firewall", "device-posture"],
    )


def _firewall_signal(result: CommandResult) -> str:
    text = command_text(result).lower()
    if not result.supported or result.error or result.timed_out:
        return "unavailable"
    if result.command_name == "linux_firewall_ufw":
        if "status: active" in text:
            return "active"
        if "status: inactive" in text:
            return "inactive"
    if result.command_name == "linux_firewall_firewall_cmd":
        if text.strip() == "running":
            return "active"
        if "not running" in text or "inactive" in text:
            return "inactive"
    if result.command_name == "linux_firewall_firewalld_active":
        if text.strip().splitlines()[:1] == ["active"]:
            return "active"
        if any(value in text for value in ["inactive", "failed", "unknown"]):
            return "inactive"
    return "unavailable"
