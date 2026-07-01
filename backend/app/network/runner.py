from datetime import UTC, datetime

from app.knowledge.guidance_service import enrich_report_guidance
from app.models.enums import Platform, ReportMode
from app.models.network import NetworkAuthorization, NetworkAuthorizationScope, NetworkContext, NetworkScopeType
from app.models.report import HomeGuardReport
from app.models.runtime import RuntimeEnvironment
from app.network.context import collect_passive_network_context
from app.network.findings import build_network_awareness_findings, build_network_scope
from app.reports.merge import summary_from_findings
from app.version import APP_NAME, APP_VERSION

NETWORK_AWARENESS_DISCLAIMER = (
    "Network awareness uses passive local context only. AI HomeGuard does not run active discovery, "
    "scan ports, run Nmap, capture packets, log in to routers, test credentials, scan public targets, "
    "upload data, change settings, or save this report automatically."
)

NETWORK_AUTHORIZATION_ERROR = "Network awareness requires authorization acknowledgement."
NETWORK_SCOPE_ERROR = "Network awareness requires home_network or demo scope."


def run_network_awareness(
    authorization: NetworkAuthorization,
    *,
    generated_at: datetime | None = None,
    context: NetworkContext | None = None,
) -> HomeGuardReport:
    if not authorization.acknowledged:
        raise ValueError(NETWORK_AUTHORIZATION_ERROR)
    if authorization.scope not in {NetworkAuthorizationScope.HOME_NETWORK, NetworkAuthorizationScope.DEMO}:
        raise ValueError(NETWORK_SCOPE_ERROR)

    report_time = generated_at or datetime.now(UTC)
    network_context = context or _context_for_authorization(authorization)
    scope = build_network_scope(network_context)
    findings = build_network_awareness_findings(authorization, network_context)
    safety_notes = _safety_notes(network_context, scope.scope_type)

    return enrich_report_guidance(HomeGuardReport(
        report_id=f"network-awareness-report-{report_time.strftime('%Y%m%d%H%M%S')}",
        app=APP_NAME,
        version=APP_VERSION,
        generated_at=report_time,
        mode=ReportMode.NETWORK_AWARENESS,
        platform_scope=[Platform.NETWORK],
        summary=summary_from_findings(findings),
        findings=findings,
        disclaimer=NETWORK_AWARENESS_DISCLAIMER,
        safety_notes=safety_notes,
    ))


def _context_for_authorization(authorization: NetworkAuthorization) -> NetworkContext:
    if authorization.scope == NetworkAuthorizationScope.DEMO:
        return NetworkContext(
            runtime_platform=Platform.NETWORK,
            runtime_environment=RuntimeEnvironment.UNKNOWN,
            possible_private_ranges=["192.168.1.0/24"],
            gateway_present=True,
            gateway_private=True,
            passive_neighbor_count=0,
            passive_neighbor_summary="Demo passive local cache shows 0 nearby network entries. No active discovery was run.",
            limitations=["Demo scope uses deterministic sample network context only."],
            safety_notes=[
                "Demo network awareness uses sample context only.",
                "No active discovery was run.",
                "No ports were scanned.",
                "No data was uploaded.",
            ],
        )
    return collect_passive_network_context()


def _safety_notes(context: NetworkContext, scope_type: NetworkScopeType) -> list[str]:
    notes = [
        "Network authorization is request-level only and is not stored.",
        "Passive local network context only.",
        "No active discovery was run.",
        "No Nmap command was run.",
        "No ping sweep was run.",
        "No ports were scanned.",
        "No packets were captured.",
        "No router login was attempted.",
        "No credentials were collected or tested.",
        "No public targets were scanned.",
        "No data was uploaded.",
        "No report was saved automatically.",
        "No settings were changed.",
        "Full MAC addresses and hostnames are not shown by default.",
        *context.safety_notes,
        *context.limitations,
    ]
    if scope_type == NetworkScopeType.PUBLIC_OR_UNKNOWN:
        notes.append("Private local network scope could not be confirmed from passive context.")
    return _unique(notes)


def _unique(values: list[str]) -> list[str]:
    unique_values: list[str] = []
    for value in values:
        if value not in unique_values:
            unique_values.append(value)
    return unique_values
