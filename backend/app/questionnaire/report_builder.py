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
from app.models.guidance import D3FENDGuidance
from app.models.questionnaire import (
    QuestionnaireAnswer,
    QuestionnaireResult,
    QuestionnaireSubmission,
    answer_value_as_text,
)
from app.models.report import HomeGuardReport, ReportSummary
from app.knowledge.guidance_service import enrich_finding_guidance, enrich_report_guidance
from app.version import APP_NAME, APP_VERSION

QUESTIONNAIRE_DISCLAIMER = (
    "This report is based on questionnaire answers only. AI HomeGuard did not run device checks, "
    "scan a network, inspect local settings, call an AI provider, upload data, or store answers."
)


def _answers_by_id(submission: QuestionnaireSubmission) -> dict[str, QuestionnaireAnswer]:
    return {answer.question_id: answer for answer in submission.answers}


def _answer_text(answers: dict[str, QuestionnaireAnswer], question_id: str) -> str | None:
    answer = answers.get(question_id)
    if answer is None or answer.skipped:
        return None
    value = answer.value
    if isinstance(value, list):
        return ",".join(str(item) for item in value)
    if value is None:
        return None
    return str(value)


def _evidence(question_id: str, answer: str | None, expected_value: str, notes: str) -> Evidence:
    return Evidence(
        source="questionnaire",
        method="user-provided questionnaire answer",
        observed_value=answer if answer is not None else "not answered",
        expected_value=expected_value,
        notes=f"{notes} No device or network check was run.",
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


def _finding(
    *,
    finding_id: str,
    home_title: str,
    status: FindingStatus,
    severity: Severity,
    confidence: Confidence,
    platform: Platform,
    category: Category,
    summary: str,
    why_it_matters: str,
    evidence: Evidence,
    d3fend_guidance: list[D3FENDGuidance],
    recommended_action: str,
    difficulty: Difficulty,
    estimated_time_minutes: int,
    requires_admin: bool = False,
    safe_to_ignore: bool = False,
    tags: list[str] | None = None,
) -> Finding:
    return Finding(
        id=finding_id,
        title=f"Questionnaire: {home_title}",
        home_title=home_title,
        technical_title=f"Questionnaire-derived finding for {finding_id}",
        status=status,
        severity=severity,
        confidence=confidence,
        platform=platform,
        category=category,
        summary=summary,
        why_it_matters=why_it_matters,
        evidence=[evidence],
        d3fend_guidance=d3fend_guidance,
        recommended_action=recommended_action,
        difficulty=difficulty,
        estimated_time_minutes=estimated_time_minutes,
        user_can_fix=True,
        requires_admin=requires_admin,
        safe_to_ignore=safe_to_ignore,
        tags=["questionnaire", *(tags or [])],
    )


def _router_admin_finding(answer: str | None) -> Finding | None:
    if answer == "yes":
        return _finding(
            finding_id="questionnaire-router-admin-password-changed",
            home_title="Router admin password has been reviewed",
            status=FindingStatus.GOOD,
            severity=Severity.INFO,
            confidence=Confidence.MEDIUM,
            platform=Platform.ROUTER,
            category=Category.IDENTITY_ACCESS,
            summary="Your answer says the router admin password was changed from the default.",
            why_it_matters="A unique router admin password helps protect the settings that manage the home network.",
            evidence=_evidence("router_admin_password_changed", answer, "yes", "Good questionnaire answer."),
            d3fend_guidance=[
                _guidance(
                    D3FENDGuidanceCategory.HARDEN,
                    "Credential hardening",
                    "Keep the router admin password unique and stored safely.",
                    "Unique admin credentials reduce the chance of unwanted router setting changes.",
                    Difficulty.EASY,
                    5,
                )
            ],
            recommended_action="No immediate action from this answer. Keep the password stored safely.",
            difficulty=Difficulty.EASY,
            estimated_time_minutes=5,
            requires_admin=True,
            safe_to_ignore=True,
            tags=["router", "identity-access"],
        )
    if answer in {"no", "unsure"}:
        status = FindingStatus.FIX_SOON if answer == "no" else FindingStatus.REVIEW
        confidence = Confidence.MEDIUM if answer == "no" else Confidence.LOW
        return _finding(
            finding_id="questionnaire-router-admin-password-review",
            home_title="Router admin password should be checked",
            status=status,
            severity=Severity.MEDIUM if answer == "no" else Severity.LOW,
            confidence=confidence,
            platform=Platform.ROUTER,
            category=Category.IDENTITY_ACCESS,
            summary="Your answer suggests the router admin password may still need review.",
            why_it_matters="The router admin password protects settings that control Wi-Fi, updates, and remote access.",
            evidence=_evidence("router_admin_password_changed", answer, "yes", "Questionnaire answer suggests review."),
            d3fend_guidance=[
                _guidance(
                    D3FENDGuidanceCategory.HARDEN,
                    "Credential hardening",
                    "Change the router admin password if it is still the default.",
                    "Default admin passwords are easier to guess or look up.",
                    Difficulty.MEDIUM,
                    15,
                ),
                _guidance(
                    D3FENDGuidanceCategory.HARDEN,
                    "Remote administration reduction",
                    "Confirm remote admin access is off unless you specifically need it.",
                    "Most homes do not need router settings reachable from outside the home.",
                    Difficulty.MEDIUM,
                    10,
                ),
                _guidance(
                    D3FENDGuidanceCategory.EDUCATE,
                    "Password storage",
                    "Store the router admin password in a safe place such as a password manager.",
                    "Safe storage helps prevent lockouts and reduces reuse.",
                    Difficulty.EASY,
                    10,
                ),
            ],
            recommended_action="Check your router admin password and change it if it is still the default.",
            difficulty=Difficulty.MEDIUM,
            estimated_time_minutes=20,
            requires_admin=True,
            tags=["router", "identity-access"],
        )
    return None


def _password_manager_finding(answer: str | None) -> Finding | None:
    if answer not in {"no", "unsure"}:
        return None
    return _finding(
        finding_id="questionnaire-password-manager-review",
        home_title="Password manager use is worth considering",
        status=FindingStatus.REVIEW,
        severity=Severity.LOW,
        confidence=Confidence.MEDIUM if answer == "no" else Confidence.LOW,
        platform=Platform.QUESTIONNAIRE,
        category=Category.IDENTITY_ACCESS,
        summary="Your answer suggests a password manager may not be in regular use.",
        why_it_matters="A password manager can make it easier to use unique passwords without memorizing them all.",
        evidence=_evidence("uses_password_manager", answer, "yes", "Questionnaire answer suggests review."),
        d3fend_guidance=[
            _guidance(
                D3FENDGuidanceCategory.HARDEN,
                "Authentication strengthening",
                "Consider using a reputable password manager for unique passwords.",
                "Unique passwords reduce the impact if one account password is exposed elsewhere.",
                Difficulty.EASY,
                30,
            ),
            _guidance(
                D3FENDGuidanceCategory.EDUCATE,
                "Password reuse reduction",
                "Start with email, banking, Apple, Google, Microsoft, and router accounts.",
                "Improving the most important accounts first keeps the task manageable.",
                Difficulty.EASY,
                30,
            ),
        ],
        recommended_action="Consider using a reputable password manager for unique passwords.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=30,
        tags=["accounts", "passwords"],
    )


def _mfa_finding(answer: str | None) -> Finding | None:
    if answer in {"yes", None}:
        return None
    status = FindingStatus.FIX_SOON if answer == "no" else FindingStatus.REVIEW
    return _finding(
        finding_id="questionnaire-mfa-important-accounts",
        home_title="Multi-factor authentication can be improved",
        status=status,
        severity=Severity.MEDIUM,
        confidence=Confidence.MEDIUM if answer in {"no", "some"} else Confidence.LOW,
        platform=Platform.QUESTIONNAIRE,
        category=Category.IDENTITY_ACCESS,
        summary="Your answer suggests some important accounts may not use multi-factor authentication.",
        why_it_matters="MFA adds another step that can help protect important accounts even if a password is guessed or reused.",
        evidence=_evidence("uses_mfa_important_accounts", answer, "yes", "Questionnaire answer suggests review."),
        d3fend_guidance=[
            _guidance(
                D3FENDGuidanceCategory.HARDEN,
                "Authentication strengthening",
                "Turn on MFA for email, banking, Apple, Google, Microsoft, and password manager accounts.",
                "Protecting important accounts first gives the best everyday benefit.",
                Difficulty.MEDIUM,
                45,
            )
        ],
        recommended_action="Turn on MFA for email, banking, Apple/Google/Microsoft, and password manager accounts.",
        difficulty=Difficulty.MEDIUM,
        estimated_time_minutes=45,
        tags=["accounts", "mfa"],
    )


def _backup_finding(answer: str | None) -> Finding | None:
    if answer in {"yes", None}:
        return None
    status = FindingStatus.FIX_SOON if answer == "no" else FindingStatus.REVIEW
    return _finding(
        finding_id="questionnaire-important-file-backups",
        home_title="Important file backups should be confirmed",
        status=status,
        severity=Severity.MEDIUM,
        confidence=Confidence.MEDIUM if answer == "no" else Confidence.LOW,
        platform=Platform.QUESTIONNAIRE,
        category=Category.BACKUP_RECOVERY,
        summary="Your answer suggests important file backups may not be set up or confirmed.",
        why_it_matters="Backups help recover photos, documents, and other personal files after mistakes or hardware failure.",
        evidence=_evidence("has_important_file_backups", answer, "yes", "Questionnaire answer suggests review."),
        d3fend_guidance=[
            _guidance(
                D3FENDGuidanceCategory.RECOVER,
                "Backup creation",
                "Set up regular backups for important files.",
                "Regular backups make recovery much easier after common home technology problems.",
                Difficulty.EASY,
                30,
            ),
            _guidance(
                D3FENDGuidanceCategory.RECOVER,
                "Restore testing",
                "Test restoring at least one harmless file.",
                "A quick restore test confirms the backup is usable before you need it.",
                Difficulty.EASY,
                10,
            ),
        ],
        recommended_action="Set up regular backups and test that you can restore at least one file.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=40,
        tags=["backup", "recovery"],
    )


def _backup_restore_finding(answer: str | None) -> Finding | None:
    if answer in {"yes", None}:
        return None
    return _finding(
        finding_id="questionnaire-backup-restore-test",
        home_title="Backup restore test would build confidence",
        status=FindingStatus.REVIEW,
        severity=Severity.LOW,
        confidence=Confidence.MEDIUM if answer == "no" else Confidence.LOW,
        platform=Platform.QUESTIONNAIRE,
        category=Category.BACKUP_RECOVERY,
        summary="Your answer suggests a backup restore has not been tested recently.",
        why_it_matters="A restore test helps confirm that backup files are available and usable.",
        evidence=_evidence("tested_backup_restore", answer, "yes", "Questionnaire answer suggests review."),
        d3fend_guidance=[
            _guidance(
                D3FENDGuidanceCategory.RECOVER,
                "Restore testing",
                "Restore one harmless file from backup as a quick test.",
                "Testing a small file is a calm way to check backup readiness.",
                Difficulty.EASY,
                10,
            )
        ],
        recommended_action="Test restoring one harmless file from your backup.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=10,
        tags=["backup", "restore-test"],
    )


def _unknown_devices_finding(answer: str | None) -> Finding | None:
    if answer in {"yes", None}:
        return None
    return _finding(
        finding_id="questionnaire-connected-device-awareness",
        home_title="Connected devices should be reviewed",
        status=FindingStatus.REVIEW,
        severity=Severity.LOW,
        confidence=Confidence.MEDIUM if answer == "no" else Confidence.LOW,
        platform=Platform.NETWORK,
        category=Category.NETWORK_AWARENESS,
        summary="Your answer suggests connected devices may not be fully known.",
        why_it_matters="Knowing what is connected helps spot old devices, guest devices, or equipment that should be separated.",
        evidence=_evidence("knows_connected_devices", answer, "yes", "Questionnaire answer suggests review."),
        d3fend_guidance=[
            _guidance(
                D3FENDGuidanceCategory.DETECT,
                "Asset identification",
                "Review connected devices in your router app or admin page.",
                "A simple household device list improves home network awareness.",
                Difficulty.EASY,
                20,
            ),
            _guidance(
                D3FENDGuidanceCategory.ISOLATE,
                "Network segmentation",
                "Move guest or less-trusted devices to guest Wi-Fi where practical.",
                "Keeping casual devices separate can reduce confusion and exposure.",
                Difficulty.MEDIUM,
                20,
            ),
        ],
        recommended_action="Review connected devices in your router app/admin page.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=20,
        tags=["network-awareness"],
    )


def _smart_device_isolation_finding(answer: str | None, has_smart_devices: str | None) -> Finding | None:
    if has_smart_devices in {"no"} or answer in {"yes", "not_applicable", None}:
        return None
    return _finding(
        finding_id="questionnaire-smart-device-isolation",
        home_title="Smart devices may benefit from guest Wi-Fi",
        status=FindingStatus.REVIEW,
        severity=Severity.LOW,
        confidence=Confidence.MEDIUM if answer == "no" else Confidence.LOW,
        platform=Platform.ROUTER,
        category=Category.NETWORK_AWARENESS,
        summary="Your answer suggests smart devices may share the same network as personal devices.",
        why_it_matters="Guest Wi-Fi can help keep less-trusted or rarely updated devices away from personal computers.",
        evidence=_evidence("smart_devices_isolated", answer, "yes or not_applicable", "Questionnaire answer suggests review."),
        d3fend_guidance=[
            _guidance(
                D3FENDGuidanceCategory.ISOLATE,
                "Network segmentation",
                "Consider putting smart devices on a guest Wi-Fi network.",
                "Separating less-trusted devices is a practical home hardening step.",
                Difficulty.MEDIUM,
                30,
            )
        ],
        recommended_action="Consider putting smart devices on a guest Wi-Fi network.",
        difficulty=Difficulty.MEDIUM,
        estimated_time_minutes=30,
        requires_admin=True,
        tags=["smart-devices", "network-awareness"],
    )


def _unsupported_devices_finding(answer: str | None) -> Finding | None:
    if answer in {"no", None}:
        return None
    status = FindingStatus.FIX_SOON if answer == "yes" else FindingStatus.REVIEW
    return _finding(
        finding_id="questionnaire-old-unsupported-devices",
        home_title="Old unsupported devices should be reviewed",
        status=status,
        severity=Severity.MEDIUM if answer == "yes" else Severity.LOW,
        confidence=Confidence.MEDIUM if answer == "yes" else Confidence.LOW,
        platform=Platform.CROSS_PLATFORM,
        category=Category.UPDATES,
        summary="Your answer suggests there may be devices connected that no longer receive updates.",
        why_it_matters="Devices that no longer receive updates may miss reliability and security fixes.",
        evidence=_evidence("old_unsupported_devices", answer, "no", "Questionnaire answer suggests review."),
        d3fend_guidance=[
            _guidance(
                D3FENDGuidanceCategory.HARDEN,
                "Unsupported software exposure reduction",
                "Retire, isolate, or replace devices that no longer receive updates.",
                "Reducing unsupported devices keeps the home network easier to maintain.",
                Difficulty.MEDIUM,
                45,
            ),
            _guidance(
                D3FENDGuidanceCategory.ISOLATE,
                "Network segmentation",
                "If a device must stay, keep it away from sensitive accounts and personal devices where practical.",
                "Isolation can reduce the practical impact of old devices.",
                Difficulty.MEDIUM,
                30,
            ),
        ],
        recommended_action="Retire, isolate, or replace devices that no longer receive updates.",
        difficulty=Difficulty.MEDIUM,
        estimated_time_minutes=45,
        requires_admin=False,
        tags=["updates", "unsupported-devices"],
    )


def build_questionnaire_findings(submission: QuestionnaireSubmission) -> list[Finding]:
    answers = _answers_by_id(submission)
    answer = lambda question_id: _answer_text(answers, question_id)

    maybe_findings = [
        _router_admin_finding(answer("router_admin_password_changed")),
        _password_manager_finding(answer("uses_password_manager")),
        _mfa_finding(answer("uses_mfa_important_accounts")),
        _backup_finding(answer("has_important_file_backups")),
        _backup_restore_finding(answer("tested_backup_restore")),
        _unknown_devices_finding(answer("knows_connected_devices")),
        _smart_device_isolation_finding(
            answer("smart_devices_isolated"),
            answer("has_smart_devices"),
        ),
        _unsupported_devices_finding(answer("old_unsupported_devices")),
    ]
    return [enrich_finding_guidance(finding) for finding in maybe_findings if finding is not None]


def evaluate_questionnaire(submission: QuestionnaireSubmission) -> QuestionnaireResult:
    answered_count = sum(1 for answer in submission.answers if not answer.skipped and answer.value is not None)
    skipped_count = sum(1 for answer in submission.answers if answer.skipped or answer.value is None)
    findings = build_questionnaire_findings(submission)
    top_actions = [finding.recommended_action for finding in findings if not finding.safe_to_ignore][:5]
    return QuestionnaireResult(
        answered_count=answered_count,
        skipped_count=skipped_count,
        findings=findings,
        top_actions=top_actions,
    )


def _summary_from_findings(findings: list[Finding], top_actions: list[str]) -> ReportSummary:
    counts = {status: 0 for status in FindingStatus}
    for finding in findings:
        counts[finding.status] += 1

    if counts[FindingStatus.FIX_SOON] or counts[FindingStatus.NEEDS_ATTENTION]:
        overall_status = FindingStatus.FIX_SOON
    elif counts[FindingStatus.REVIEW] or counts[FindingStatus.UNABLE_TO_CHECK]:
        overall_status = FindingStatus.REVIEW
    else:
        overall_status = FindingStatus.GOOD

    score = max(0, 100 - counts[FindingStatus.FIX_SOON] * 12 - counts[FindingStatus.REVIEW] * 7)

    return ReportSummary(
        overall_status=overall_status,
        overall_score=score,
        good_count=counts[FindingStatus.GOOD],
        review_count=counts[FindingStatus.REVIEW],
        fix_soon_count=counts[FindingStatus.FIX_SOON],
        needs_attention_count=counts[FindingStatus.NEEDS_ATTENTION],
        unable_to_check_count=counts[FindingStatus.UNABLE_TO_CHECK],
        top_actions=top_actions,
    )


def build_questionnaire_report(submission: QuestionnaireSubmission) -> HomeGuardReport:
    result = evaluate_questionnaire(submission)
    generated_at = submission.generated_at or datetime.now(UTC)
    return enrich_report_guidance(HomeGuardReport(
        report_id=f"questionnaire-homeguard-report-{generated_at.strftime('%Y%m%d%H%M%S')}",
        app=APP_NAME,
        version=APP_VERSION,
        generated_at=generated_at,
        mode=ReportMode.DEMO,
        platform_scope=[
            Platform.ROUTER,
            Platform.QUESTIONNAIRE,
            Platform.NETWORK,
            Platform.CROSS_PLATFORM,
        ],
        summary=_summary_from_findings(result.findings, result.top_actions),
        findings=result.findings,
        disclaimer=QUESTIONNAIRE_DISCLAIMER,
        safety_notes=[
            "These findings are based on questionnaire answers only.",
            "No device or network checks were run.",
            "Questionnaire answers are not written to disk or sent to an external service.",
            "Do not enter passwords, credentials, addresses, or personal identifiers into questionnaire fields.",
        ],
    ))


def get_demo_answers() -> QuestionnaireSubmission:
    return QuestionnaireSubmission(
        answers=[
            QuestionnaireAnswer(question_id="router_admin_password_changed", value="unsure"),
            QuestionnaireAnswer(question_id="wifi_wpa2_wpa3", value="yes"),
            QuestionnaireAnswer(question_id="guest_wifi_available", value="no"),
            QuestionnaireAnswer(question_id="router_remote_admin_disabled", value="unsure"),
            QuestionnaireAnswer(question_id="router_firmware_updated", value="over_6_months"),
            QuestionnaireAnswer(question_id="uses_password_manager", value="no"),
            QuestionnaireAnswer(question_id="uses_mfa_important_accounts", value="some"),
            QuestionnaireAnswer(question_id="separate_family_device_accounts", value="yes"),
            QuestionnaireAnswer(question_id="regular_updates", value="sometimes"),
            QuestionnaireAnswer(question_id="old_unsupported_devices", value="yes"),
            QuestionnaireAnswer(question_id="knows_connected_devices", value="mostly"),
            QuestionnaireAnswer(question_id="has_important_file_backups", value="no"),
            QuestionnaireAnswer(question_id="tested_backup_restore", value="no"),
            QuestionnaireAnswer(question_id="backup_separate_location", value="unsure"),
            QuestionnaireAnswer(question_id="has_smart_devices", value="yes"),
            QuestionnaireAnswer(question_id="smart_devices_isolated", value="no"),
            QuestionnaireAnswer(question_id="shared_family_devices", value="yes"),
            QuestionnaireAnswer(question_id="parental_controls_used", value="unsure"),
        ],
    )
