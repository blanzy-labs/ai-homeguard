from app.models.enums import Category, Confidence, Difficulty, FindingStatus, Platform, Severity
from app.models.evidence import Evidence
from app.models.finding import Finding
from app.models.network import NetworkAuthorization, NetworkContext, NetworkScope, NetworkScopeType


def build_network_scope(context: NetworkContext) -> NetworkScope:
    if context.runtime_environment.value == "docker":
        scope_type = NetworkScopeType.DOCKER_OR_CONTAINER_LIMITED
    elif context.gateway_private or context.possible_private_ranges:
        scope_type = NetworkScopeType.PRIVATE_LOCAL
    else:
        scope_type = NetworkScopeType.PUBLIC_OR_UNKNOWN

    return NetworkScope(
        scope_type=scope_type,
        detected_platform=context.runtime_platform,
        runtime_environment=context.runtime_environment,
        local_interface_count=context.local_interface_count,
        private_network_count=len(context.possible_private_ranges),
        gateway_detected=context.gateway_present,
        gateway_private=context.gateway_private,
        limitations=context.limitations,
        safety_notes=context.safety_notes,
    )


def build_network_awareness_findings(
    authorization: NetworkAuthorization,
    context: NetworkContext,
) -> list[Finding]:
    findings = [
        _authorization_finding(authorization),
        _passive_only_finding(),
    ]
    if context.gateway_private or context.possible_private_ranges:
        findings.append(_private_context_finding(context))
    else:
        findings.append(_unknown_scope_finding(context))
    if context.runtime_environment.value == "docker":
        findings.append(_container_limitation_finding(context))
    if context.passive_neighbor_count is not None:
        findings.append(_passive_neighbor_finding(context))
    return findings


def _authorization_finding(authorization: NetworkAuthorization) -> Finding:
    return _network_finding(
        finding_id="network-awareness-authorization-acknowledged",
        home_title="Network awareness authorization was acknowledged",
        status=FindingStatus.GOOD,
        severity=Severity.INFO,
        confidence=Confidence.HIGH,
        category=Category.SAFETY,
        summary="The request included authorization acknowledgement for passive local network awareness.",
        why_it_matters="Authorization keeps network-aware features limited to networks you own or are allowed to assess.",
        evidence=[
            Evidence(
                source="request authorization",
                method="network_authorization",
                observed_value=f"acknowledged: {authorization.acknowledged}; scope: {authorization.scope.value}",
                expected_value="acknowledged home_network or demo scope",
                notes="Authorization is request-level only and is not stored.",
            )
        ],
        recommended_action="Continue only on networks you own or are authorized to assess.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=1,
        safe_to_ignore=True,
        tags=["network-awareness", "authorization", "safety"],
    )


def _passive_only_finding() -> Finding:
    return _network_finding(
        finding_id="network-awareness-passive-only",
        home_title="Network awareness is passive only",
        status=FindingStatus.GOOD,
        severity=Severity.INFO,
        confidence=Confidence.HIGH,
        category=Category.SAFETY,
        summary="AI HomeGuard used passive local context only and did not probe the network.",
        why_it_matters="Passive awareness avoids scanning devices, testing ports, or sending discovery traffic.",
        evidence=[
            Evidence(
                source="network awareness policy",
                method="network safety policy",
                observed_value="passive local context only",
                expected_value="no active discovery, port scanning, packet capture, router login, or public target scanning",
                notes="No target input was accepted and no network scan was run.",
            )
        ],
        recommended_action="Use this as a starting point before enabling any future discovery features.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=1,
        safe_to_ignore=True,
        tags=["network-awareness", "safety"],
    )


def _private_context_finding(context: NetworkContext) -> Finding:
    range_count = len(context.possible_private_ranges)
    observed_parts = [f"private range hints: {range_count}"]
    if context.gateway_present:
        observed_parts.append("gateway present")
    if context.gateway_private:
        observed_parts.append("gateway appears private")
    return _network_finding(
        finding_id="network-awareness-private-context",
        home_title="Private local network context was detected",
        status=FindingStatus.GOOD,
        severity=Severity.INFO,
        confidence=Confidence.MEDIUM,
        category=Category.NETWORK_AWARENESS,
        summary="Passive local context suggests a private/local network is present.",
        why_it_matters="Knowing that the context appears private helps keep future network-aware features scoped to home networks.",
        evidence=[
            Evidence(
                source="passive network context",
                method="local route/interface cache",
                observed_value="; ".join(observed_parts),
                expected_value="private local context only",
                notes="No public targets were scanned and no active discovery was run.",
            )
        ],
        recommended_action="Review your router app or admin page to identify connected devices.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=10,
        tags=["network-awareness", "identify_assets", "review_router_admin"],
    )


def _unknown_scope_finding(context: NetworkContext) -> Finding:
    return _network_finding(
        finding_id="network-awareness-private-context-unavailable",
        home_title="Private network context could not be confirmed",
        status=FindingStatus.UNABLE_TO_CHECK,
        severity=Severity.INFO,
        confidence=Confidence.UNKNOWN,
        category=Category.SAFETY,
        summary="AI HomeGuard could not safely confirm private local network context from passive sources.",
        why_it_matters="AI HomeGuard does not support public target scanning and will not infer permission from unknown context.",
        evidence=[
            Evidence(
                source="passive network context",
                method="local route/interface cache",
                observed_value=f"gateway present: {context.gateway_present}; private ranges: {len(context.possible_private_ranges)}",
                expected_value="private local context",
                notes="Public or unknown network scope is not used for active checks.",
            )
        ],
        recommended_action="Use AI HomeGuard only on your own private/local network and review your router app for device lists.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=5,
        tags=["network-awareness", "safety"],
    )


def _container_limitation_finding(context: NetworkContext) -> Finding:
    return _network_finding(
        finding_id="network-awareness-container-limitation",
        home_title="Container networking may limit visibility",
        status=FindingStatus.REVIEW,
        severity=Severity.INFO,
        confidence=Confidence.HIGH,
        category=Category.NETWORK_AWARENESS,
        summary="AI HomeGuard appears to be running inside a container, so network context may describe the container network.",
        why_it_matters="Container networking can differ from the home network seen by the host computer.",
        evidence=[
            Evidence(
                source="runtime context",
                method="detect_runtime_environment",
                observed_value=f"runtime environment: {context.runtime_environment.value}",
                expected_value="native runtime for host-level network context",
                notes="No host network scan was run.",
            )
        ],
        recommended_action="Run the backend natively if you want host-level network context.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=10,
        tags=["network-awareness", "runtime_context"],
    )


def _passive_neighbor_finding(context: NetworkContext) -> Finding:
    count = context.passive_neighbor_count or 0
    return _network_finding(
        finding_id="network-awareness-passive-neighbor-cache",
        home_title="Passive local neighbor cache was summarized",
        status=FindingStatus.REVIEW if count else FindingStatus.UNABLE_TO_CHECK,
        severity=Severity.INFO,
        confidence=Confidence.MEDIUM if count else Confidence.LOW,
        category=Category.NETWORK_AWARENESS,
        summary="AI HomeGuard summarized the local passive neighbor cache without listing device identifiers.",
        why_it_matters="Passive cache information can be incomplete, but it may hint that nearby local entries exist.",
        evidence=[
            Evidence(
                source="passive network context",
                method="local neighbor cache",
                observed_value=context.passive_neighbor_summary or "Passive local cache was empty or unavailable.",
                expected_value="count-only passive cache summary",
                notes="No full MAC addresses or hostnames are shown by default.",
            )
        ],
        recommended_action="Compare this with your router app or admin page device list.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=10,
        tags=["network-awareness", "identify_assets", "isolate_untrusted_devices"],
    )


def _network_finding(
    *,
    finding_id: str,
    home_title: str,
    status: FindingStatus,
    severity: Severity,
    confidence: Confidence,
    category: Category,
    summary: str,
    why_it_matters: str,
    evidence: list[Evidence],
    recommended_action: str,
    difficulty: Difficulty,
    estimated_time_minutes: int,
    tags: list[str],
    safe_to_ignore: bool = False,
) -> Finding:
    return Finding(
        id=finding_id,
        title=f"Network awareness: {home_title}",
        home_title=home_title,
        technical_title=f"Passive network awareness finding for {finding_id}",
        status=status,
        severity=severity,
        confidence=confidence,
        platform=Platform.NETWORK,
        category=category,
        summary=summary,
        why_it_matters=why_it_matters,
        evidence=evidence,
        d3fend_guidance=[],
        recommended_action=recommended_action,
        difficulty=difficulty,
        estimated_time_minutes=estimated_time_minutes,
        user_can_fix=True,
        requires_admin=False,
        safe_to_ignore=safe_to_ignore,
        tags=tags,
    )
