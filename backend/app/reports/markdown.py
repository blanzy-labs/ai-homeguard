from app.models.finding import Finding
from app.models.report import HomeGuardReport
from app.knowledge.guidance_service import enrich_report_guidance


def render_markdown_report(report: HomeGuardReport) -> str:
    report = enrich_report_guidance(report)
    lines = [
        "# AI HomeGuard Report",
        "",
        "## Report Overview",
        "",
        f"- App: {report.app}",
        f"- Version: {report.version}",
        f"- Mode: {report.mode.value}",
        f"- Generated at: {report.generated_at.isoformat()}",
        f"- Platforms: {', '.join(platform.value for platform in report.platform_scope) or 'not specified'}",
        "",
        "Review this report before sharing. Markdown and JSON exports may contain questionnaire answers or local audit evidence you chose to include.",
        "",
        "## Safety Notes",
        "",
    ]
    lines.extend(_bullet_list(report.safety_notes or ["No safety notes were provided."]))
    lines.extend(
        [
            "",
            "## Overall Summary",
            "",
            f"- Overall status: {report.summary.overall_status.value}",
            f"- Overall score: {report.summary.overall_score if report.summary.overall_score is not None else 'not scored'}",
            f"- Good: {report.summary.good_count}",
            f"- Review: {report.summary.review_count}",
            f"- Fix soon: {report.summary.fix_soon_count}",
            f"- Needs attention: {report.summary.needs_attention_count}",
            f"- Unable to check: {report.summary.unable_to_check_count}",
            "",
            "## Top Recommended Actions",
            "",
        ]
    )
    lines.extend(_numbered_list(report.summary.top_actions or ["No top actions were generated."]))
    lines.extend(["", "## Findings", ""])
    for finding in report.findings:
        lines.extend(_finding_section(finding))
    lines.extend(["", "## D3FEND-Informed Defensive Guidance", ""])
    lines.extend(
        [
            "These defensive actions are inspired by common defensive concepts and D3FEND-style "
            "countermeasure thinking. They are educational and do not guarantee complete protection.",
            "",
        ]
    )
    guidance_lines = _guidance_summary(report.findings)
    lines.extend(guidance_lines or ["No D3FEND-informed guidance was included."])
    lines.extend(["", "## Optional ATT&CK Educational Context", ""])
    attack_lines = _attack_context_summary(report.findings)
    lines.extend(attack_lines or ["No ATT&CK educational context was included."])
    lines.extend(["", "## Limitations", ""])
    if report.runtime_context and report.runtime_context.limitations:
        lines.extend(_bullet_list(report.runtime_context.limitations))
    else:
        lines.append("- No additional runtime limitations were reported.")
    lines.extend(["", "## Disclaimer", "", report.disclaimer, ""])
    return "\n".join(lines)


def _finding_section(finding: Finding) -> list[str]:
    lines = [
        f"### {_safe_text(finding.home_title)}",
        "",
        f"- Status: {finding.status.value}",
        f"- Severity: {finding.severity.value}",
        f"- Confidence: {finding.confidence.value}",
        f"- Platform: {finding.platform.value}",
        f"- Category: {finding.category.value}",
        f"- Difficulty: {finding.difficulty.value}",
    ]
    if finding.estimated_time_minutes:
        lines.append(f"- Estimated time: {finding.estimated_time_minutes} minutes")
    lines.extend(
        [
            "",
            f"Why it matters: {_safe_text(finding.why_it_matters)}",
            "",
            f"Recommended action: {_safe_text(finding.recommended_action)}",
            "",
            "Evidence summary:",
            "",
        ]
    )
    for evidence in finding.evidence:
        source = _evidence_source_label(finding, evidence.source)
        lines.extend(
            [
                f"- Source: {source}",
                f"  - Method: {_safe_text(evidence.method)}",
                f"  - Observed: {_safe_text(evidence.observed_value)}",
                f"  - Expected: {_safe_text(evidence.expected_value)}",
            ]
        )
        if evidence.notes:
            lines.append(f"  - Notes: {_safe_text(evidence.notes)}")
    if finding.d3fend_guidance:
        lines.extend(["", "D3FEND-informed guidance:"])
        for guidance in finding.d3fend_guidance:
            admin_note = "likely needs admin access" if guidance.requires_admin else "usually no admin access needed"
            educational_note = "educational mapping" if guidance.educational_only else "defensive guidance"
            lines.append(
                f"- {guidance.category.value}: {_safe_text(guidance.home_action)} "
                f"({educational_note}; {admin_note})"
            )
    if finding.attack_context:
        lines.extend(["", "ATT&CK educational context:"])
        for context in finding.attack_context:
            marker = "educational only" if context.educational_only else "context"
            lines.append(f"- {marker}: {_safe_text(context.explanation)}")
    lines.append("")
    return lines


def _guidance_summary(findings: list[Finding]) -> list[str]:
    lines: list[str] = []
    for finding in findings:
        for guidance in finding.d3fend_guidance:
            lines.append(
                f"- {finding.home_title}: {guidance.category.value} / "
                f"{_safe_text(guidance.defensive_concept)} - {_safe_text(guidance.home_action)}"
            )
    return lines


def _attack_context_summary(findings: list[Finding]) -> list[str]:
    lines: list[str] = []
    for finding in findings:
        for context in finding.attack_context:
            lines.append(
                f"- {finding.home_title}: educational only - {_safe_text(context.explanation)}"
            )
    return lines


def _bullet_list(values: list[str]) -> list[str]:
    return [f"- {_safe_text(value)}" for value in values]


def _numbered_list(values: list[str]) -> list[str]:
    return [f"{index}. {_safe_text(value)}" for index, value in enumerate(values, start=1)]


def _evidence_source_label(finding: Finding, source: str) -> str:
    source_text = source.lower()
    if "questionnaire" in source_text or "questionnaire" in finding.tags:
        return "questionnaire"
    if "platform guard" in source_text or "unsupported-platform" in finding.tags:
        return "unsupported_platform"
    if "runtime" in source_text:
        return "runtime_context"
    if "demo" in source_text or "demo" in finding.tags:
        return "demo"
    return "local_device"


def _safe_text(value: object) -> str:
    return str(value).replace("\n", " ").strip()
