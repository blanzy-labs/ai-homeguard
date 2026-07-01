from datetime import UTC, datetime

from app.models.enums import (
    Category,
    Confidence,
    D3FENDGuidanceCategory,
    Difficulty,
    FindingStatus,
    Platform,
    ReportMode,
    Severity,
)
from app.models.evidence import Evidence
from app.models.finding import Finding
from app.models.guidance import AttackContext, D3FENDGuidance
from app.models.report import HomeGuardReport, ReportSummary
from app.version import APP_NAME, APP_VERSION

DEMO_GENERATED_AT = datetime(2026, 7, 1, 12, 0, tzinfo=UTC)


def _evidence(source: str, observed_value: str, expected_value: str, notes: str) -> Evidence:
    return Evidence(
        source=source,
        method="static demo sample",
        observed_value=observed_value,
        expected_value=expected_value,
        notes=notes,
    )


def _guidance(
    category: D3FENDGuidanceCategory,
    defensive_concept: str,
    home_action: str,
    rationale: str,
    difficulty: Difficulty,
    estimated_time_minutes: int,
    technical_action: str | None = None,
) -> D3FENDGuidance:
    return D3FENDGuidance(
        category=category,
        defensive_concept=defensive_concept,
        home_action=home_action,
        technical_action=technical_action,
        rationale=rationale,
        difficulty=difficulty,
        estimated_time_minutes=estimated_time_minutes,
    )


def get_demo_report() -> HomeGuardReport:
    findings = [
        Finding(
            id="demo-windows-defender-enabled",
            title="Demo: Windows Defender is enabled",
            home_title="Built-in malware protection is on",
            technical_title="Microsoft Defender Antivirus appears enabled",
            status=FindingStatus.GOOD,
            severity=Severity.INFO,
            confidence=Confidence.HIGH,
            platform=Platform.WINDOWS,
            category=Category.MALWARE_PROTECTION,
            summary="The sample report shows built-in Windows malware protection enabled.",
            why_it_matters=(
                "Malware protection helps block common unsafe downloads and suspicious files "
                "before they can affect a home device."
            ),
            evidence=[
                _evidence(
                    "demo data",
                    "Microsoft Defender: enabled",
                    "Microsoft Defender: enabled",
                    "This is sample evidence only. AI HomeGuard did not inspect this computer.",
                )
            ],
            d3fend_guidance=[
                _guidance(
                    D3FENDGuidanceCategory.HARDEN,
                    "Endpoint protection",
                    "Keep built-in malware protection turned on and allow regular updates.",
                    "Updated malware protection reduces exposure to common harmful files.",
                    Difficulty.EASY,
                    5,
                )
            ],
            recommended_action="No action needed in this demo finding.",
            difficulty=Difficulty.EASY,
            estimated_time_minutes=5,
            user_can_fix=True,
            requires_admin=False,
            safe_to_ignore=True,
            tags=["demo", "malware-protection"],
        ),
        Finding(
            id="demo-windows-firewall-enabled",
            title="Demo: Windows Firewall is enabled",
            home_title="The firewall is on",
            technical_title="Windows Firewall appears enabled",
            status=FindingStatus.GOOD,
            severity=Severity.INFO,
            confidence=Confidence.HIGH,
            platform=Platform.WINDOWS,
            category=Category.DEVICE_POSTURE,
            summary="The sample report shows the device firewall enabled.",
            why_it_matters=(
                "A firewall helps reduce unexpected inbound connections to a home computer."
            ),
            evidence=[
                _evidence(
                    "demo data",
                    "Firewall profile: enabled",
                    "Firewall profile: enabled",
                    "This value is fake and deterministic for demo mode.",
                )
            ],
            d3fend_guidance=[
                _guidance(
                    D3FENDGuidanceCategory.HARDEN,
                    "Network traffic filtering",
                    "Leave the firewall enabled on home devices.",
                    "Filtering unexpected inbound traffic is a simple defensive baseline.",
                    Difficulty.EASY,
                    5,
                )
            ],
            recommended_action="No action needed in this demo finding.",
            difficulty=Difficulty.EASY,
            estimated_time_minutes=5,
            user_can_fix=True,
            requires_admin=False,
            safe_to_ignore=True,
            tags=["demo", "firewall"],
        ),
        Finding(
            id="demo-remote-desktop-review",
            title="Demo: Remote Desktop appears enabled",
            home_title="Remote access may need a quick review",
            technical_title="Remote Desktop service appears enabled",
            status=FindingStatus.REVIEW,
            severity=Severity.MEDIUM,
            confidence=Confidence.MEDIUM,
            platform=Platform.WINDOWS,
            category=Category.IDENTITY_ACCESS,
            summary="The sample report shows Remote Desktop enabled on a Windows device.",
            why_it_matters=(
                "Remote access can be useful, but it should be enabled only when someone in "
                "the household needs it and understands how it is protected."
            ),
            evidence=[
                _evidence(
                    "demo data",
                    "Remote Desktop: enabled",
                    "Remote Desktop: disabled unless needed",
                    "This is a fake example. No services were checked.",
                )
            ],
            d3fend_guidance=[
                _guidance(
                    D3FENDGuidanceCategory.HARDEN,
                    "Remote access reduction",
                    "Turn off Remote Desktop if no one in the household uses it.",
                    "Removing unused remote access reduces ways a device can be reached.",
                    Difficulty.MEDIUM,
                    15,
                    "Disable Remote Desktop or restrict it to trusted users and networks.",
                ),
                _guidance(
                    D3FENDGuidanceCategory.ISOLATE,
                    "Network access control",
                    "Keep remote access limited to trusted home networks.",
                    "Trusted network restrictions make accidental exposure less likely.",
                    Difficulty.MEDIUM,
                    20,
                ),
                _guidance(
                    D3FENDGuidanceCategory.HARDEN,
                    "Authentication strengthening",
                    "Use strong sign-in settings for any account allowed to connect remotely.",
                    "Stronger authentication helps protect access that must remain enabled.",
                    Difficulty.MEDIUM,
                    20,
                ),
            ],
            attack_context=[
                AttackContext(
                    tactic="Lateral Movement",
                    technique_id="T1021.001",
                    technique_name="Remote Services: Remote Desktop Protocol",
                    explanation=(
                        "ATT&CK lists Remote Desktop as a way systems can be accessed. "
                        "This demo context is educational only and does not mean your device "
                        "was scanned or attacked."
                    ),
                    confidence=Confidence.MEDIUM,
                )
            ],
            recommended_action="Confirm whether Remote Desktop is needed. If not, disable it.",
            difficulty=Difficulty.MEDIUM,
            estimated_time_minutes=15,
            user_can_fix=True,
            requires_admin=False,
            tags=["demo", "remote-access"],
        ),
        Finding(
            id="demo-device-encryption-disabled",
            title="Demo: Disk encryption appears disabled",
            home_title="Device encryption may need to be turned on",
            technical_title="Full-disk encryption appears disabled",
            status=FindingStatus.FIX_SOON,
            severity=Severity.MEDIUM,
            confidence=Confidence.MEDIUM,
            platform=Platform.WINDOWS,
            category=Category.DATA_PROTECTION,
            summary="The sample report shows full-disk encryption disabled.",
            why_it_matters=(
                "Device encryption helps protect personal files if a computer is lost, stolen, "
                "or repaired by someone outside the household."
            ),
            evidence=[
                _evidence(
                    "demo data",
                    "Device encryption: disabled",
                    "Device encryption: enabled where supported",
                    "This is sample evidence only. No storage settings were checked.",
                )
            ],
            d3fend_guidance=[
                _guidance(
                    D3FENDGuidanceCategory.HARDEN,
                    "Data-at-rest protection",
                    "Enable full-disk encryption if the device supports it.",
                    "Encryption helps keep local files private when the device is not in use.",
                    Difficulty.MEDIUM,
                    30,
                    "Enable BitLocker or device encryption and verify recovery options.",
                ),
                _guidance(
                    D3FENDGuidanceCategory.RECOVER,
                    "Recovery key management",
                    "Store the recovery key somewhere safe before relying on encryption.",
                    "A saved recovery key helps avoid losing access after hardware or account issues.",
                    Difficulty.EASY,
                    10,
                ),
            ],
            recommended_action="Plan a short maintenance window to enable encryption and save the recovery key.",
            difficulty=Difficulty.MEDIUM,
            estimated_time_minutes=30,
            user_can_fix=True,
            requires_admin=True,
            tags=["demo", "device-encryption", "data-protection"],
        ),
        Finding(
            id="demo-unknown-home-device",
            title="Demo: Unknown device detected on home network",
            home_title="A sample home device needs identification",
            technical_title="Unrecognized device appears in demo asset list",
            status=FindingStatus.REVIEW,
            severity=Severity.LOW,
            confidence=Confidence.LOW,
            platform=Platform.NETWORK,
            category=Category.NETWORK_AWARENESS,
            summary="The sample report includes an unknown device named demo-device.",
            why_it_matters=(
                "Knowing what is connected at home helps spot old devices, guest devices, "
                "or equipment that should move to a guest network."
            ),
            evidence=[
                _evidence(
                    "demo data",
                    "Device name: demo-device",
                    "Known household device or guest device",
                    "No real network scan was run and no real network identifiers are included.",
                )
            ],
            d3fend_guidance=[
                _guidance(
                    D3FENDGuidanceCategory.DETECT,
                    "Asset identification",
                    "Check whether demo-device represents something you recognize.",
                    "A simple device inventory improves everyday home network awareness.",
                    Difficulty.EASY,
                    10,
                ),
                _guidance(
                    D3FENDGuidanceCategory.ISOLATE,
                    "Network segmentation",
                    "Place untrusted or guest devices on guest Wi-Fi.",
                    "Guest Wi-Fi keeps casual devices separate from personal computers.",
                    Difficulty.MEDIUM,
                    20,
                ),
            ],
            recommended_action="Identify the device owner, then move guest or IoT devices to guest Wi-Fi.",
            difficulty=Difficulty.EASY,
            estimated_time_minutes=15,
            user_can_fix=True,
            requires_admin=False,
            tags=["demo", "network-awareness"],
        ),
        Finding(
            id="demo-router-password-confirmation",
            title="Demo: Router admin password needs confirmation",
            home_title="Router admin settings should be confirmed",
            technical_title="Router admin credential posture not checked",
            status=FindingStatus.UNABLE_TO_CHECK,
            severity=Severity.LOW,
            confidence=Confidence.UNKNOWN,
            platform=Platform.ROUTER,
            category=Category.IDENTITY_ACCESS,
            summary="The sample report cannot confirm whether the router admin password was changed.",
            why_it_matters=(
                "A strong router admin password helps protect the settings that control the "
                "home network."
            ),
            evidence=[
                _evidence(
                    "questionnaire/demo",
                    "Not confirmed in demo mode",
                    "User confirms router admin password is unique",
                    "No router login was attempted and no credentials were tested.",
                )
            ],
            d3fend_guidance=[
                _guidance(
                    D3FENDGuidanceCategory.HARDEN,
                    "Credential hardening",
                    "Change the router admin password if it still uses a default value.",
                    "Unique admin credentials reduce the chance of unwanted settings changes.",
                    Difficulty.MEDIUM,
                    15,
                ),
                _guidance(
                    D3FENDGuidanceCategory.HARDEN,
                    "Remote administration reduction",
                    "Disable remote admin access unless you specifically need it.",
                    "Most homes do not need router admin pages reachable from outside the home.",
                    Difficulty.MEDIUM,
                    10,
                ),
                _guidance(
                    D3FENDGuidanceCategory.HARDEN,
                    "Firmware maintenance",
                    "Check the router firmware update page or vendor app.",
                    "Firmware updates often include reliability and security improvements.",
                    Difficulty.MEDIUM,
                    20,
                ),
            ],
            recommended_action="Log in to the router admin page or vendor app and confirm the basics.",
            difficulty=Difficulty.MEDIUM,
            estimated_time_minutes=20,
            user_can_fix=True,
            requires_admin=True,
            tags=["demo", "router"],
        ),
        Finding(
            id="demo-backups-not-confirmed",
            title="Demo: Backups not confirmed",
            home_title="Backups should be confirmed",
            technical_title="Backup status not confirmed by questionnaire",
            status=FindingStatus.FIX_SOON,
            severity=Severity.MEDIUM,
            confidence=Confidence.UNKNOWN,
            platform=Platform.QUESTIONNAIRE,
            category=Category.BACKUP_RECOVERY,
            summary="The sample report shows that backups have not been confirmed.",
            why_it_matters=(
                "Backups help recover family photos, documents, and other personal files after "
                "device loss, mistakes, or hardware failure."
            ),
            evidence=[
                _evidence(
                    "questionnaire/demo",
                    "Backup answer: not confirmed",
                    "Backups configured and restore tested",
                    "This is fake questionnaire data for demo mode.",
                )
            ],
            d3fend_guidance=[
                _guidance(
                    D3FENDGuidanceCategory.RECOVER,
                    "Backup creation",
                    "Set up regular backups for important household files.",
                    "Regular backups make recovery much easier after common home tech problems.",
                    Difficulty.EASY,
                    30,
                ),
                _guidance(
                    D3FENDGuidanceCategory.RECOVER,
                    "Restore testing",
                    "Test restoring one harmless file so you know the backup works.",
                    "A quick restore test builds confidence before you actually need it.",
                    Difficulty.EASY,
                    10,
                ),
            ],
            recommended_action="Choose a backup location and test restoring one small file.",
            difficulty=Difficulty.EASY,
            estimated_time_minutes=30,
            user_can_fix=True,
            requires_admin=False,
            tags=["demo", "backup"],
        ),
        Finding(
            id="demo-no-real-network-scan",
            title="Demo: No real network scan was run",
            home_title="Demo mode uses sample findings only",
            technical_title="Static demo report with no local commands",
            status=FindingStatus.GOOD,
            severity=Severity.INFO,
            confidence=Confidence.HIGH,
            platform=Platform.SAFETY,
            category=Category.SAFETY,
            summary="This report is generated from static sample data.",
            why_it_matters=(
                "Demo mode is safe to explore because it does not run checks, scan networks, "
                "inspect devices, or send data to an AI provider."
            ),
            evidence=[
                _evidence(
                    "demo data",
                    "Static report returned by /demo/report",
                    "No real checks in Slice 2",
                    "No system command, network scanner, packet capture, telemetry, database, or AI call is used.",
                )
            ],
            d3fend_guidance=[
                _guidance(
                    D3FENDGuidanceCategory.EDUCATE,
                    "Safe demonstration",
                    "Use this dashboard to learn the report format before real checks exist.",
                    "Static sample data lets the user experience be shaped without touching devices.",
                    Difficulty.EASY,
                    5,
                )
            ],
            recommended_action="Treat all findings on this page as examples, not results from your device.",
            difficulty=Difficulty.EASY,
            estimated_time_minutes=5,
            user_can_fix=True,
            requires_admin=False,
            safe_to_ignore=True,
            tags=["demo", "safety"],
        ),
    ]

    return HomeGuardReport(
        report_id="demo-homeguard-report-v0-1-slice-2",
        app=APP_NAME,
        version=APP_VERSION,
        generated_at=DEMO_GENERATED_AT,
        mode=ReportMode.DEMO,
        platform_scope=[
            Platform.WINDOWS,
            Platform.NETWORK,
            Platform.ROUTER,
            Platform.QUESTIONNAIRE,
            Platform.SAFETY,
        ],
        summary=ReportSummary(
            overall_status=FindingStatus.FIX_SOON,
            overall_score=72,
            good_count=3,
            review_count=2,
            fix_soon_count=2,
            needs_attention_count=0,
            unable_to_check_count=1,
            top_actions=[
                "Confirm whether Remote Desktop is needed and disable it if unused.",
                "Plan to enable disk encryption and store the recovery key safely.",
                "Set up regular backups and test restoring one harmless file.",
                "Review router admin settings, password, remote admin, and firmware.",
            ],
        ),
        findings=findings,
        disclaimer=(
            "This is a deterministic demo report using fake sample findings only. AI HomeGuard "
            "did not run local checks, scan a network, inspect this device, call an AI provider, "
            "or store data."
        ),
        safety_notes=[
            "Demo mode uses static sample data only.",
            "No real Windows, macOS, Linux, router, or network checks are run in Slice 2.",
            "No network scan, packet capture, credential test, exploit, AI call, telemetry, or database is used.",
            "Any ATT&CK context is educational only and does not indicate activity on your device.",
        ],
    )
