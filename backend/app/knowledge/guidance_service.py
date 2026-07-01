from app.knowledge.d3fend_catalog import CATALOG_BY_ID, D3FEND_GUIDANCE_CATALOG
from app.models.enums import Category, Platform
from app.models.finding import Finding
from app.models.guidance import D3FENDGuidance
from app.models.report import HomeGuardReport

GUIDANCE_ID_TAGS = set(CATALOG_BY_ID)

TAG_TO_GUIDANCE_IDS: dict[str, tuple[str, ...]] = {
    "firewall": ("enable_host_firewall",),
    "device-posture": ("review_local_services",),
    "remote-access": ("review_remote_access", "strengthen_authentication"),
    "remote-desktop": ("review_remote_access", "strengthen_authentication"),
    "remote-login": ("review_remote_access", "strengthen_authentication"),
    "ssh": ("review_remote_access", "strengthen_authentication"),
    "listening-ports": ("review_local_services",),
    "network-awareness": ("identify_assets",),
    "smart-devices": ("isolate_untrusted_devices",),
    "router": ("review_router_admin",),
    "accounts": ("strengthen_authentication",),
    "passwords": ("strengthen_authentication",),
    "mfa": ("strengthen_authentication",),
    "identity-access": ("strengthen_authentication",),
    "local-admins": ("reduce_admin_use",),
    "admin": ("reduce_admin_use",),
    "least-privilege": ("reduce_admin_use",),
    "bitlocker": ("enable_full_disk_encryption",),
    "filevault": ("enable_full_disk_encryption",),
    "disk-encryption": ("enable_full_disk_encryption",),
    "device-encryption": ("enable_full_disk_encryption",),
    "encryption": ("enable_full_disk_encryption",),
    "luks": ("enable_full_disk_encryption",),
    "defender": ("keep_endpoint_protection_enabled",),
    "gatekeeper": ("keep_endpoint_protection_enabled",),
    "clamav": ("keep_endpoint_protection_enabled",),
    "malware-protection": ("keep_endpoint_protection_enabled",),
    "updates": ("keep_system_updated",),
    "unsupported-devices": ("keep_system_updated", "isolate_untrusted_devices"),
    "backup": ("backup_important_data",),
    "recovery": ("backup_important_data",),
    "restore-test": ("backup_important_data",),
}

CATEGORY_DEFAULTS: dict[Category, tuple[str, ...]] = {
    Category.DEVICE_POSTURE: ("review_local_services",),
    Category.NETWORK_AWARENESS: ("identify_assets",),
    Category.IDENTITY_ACCESS: ("strengthen_authentication",),
    Category.DATA_PROTECTION: ("enable_full_disk_encryption",),
    Category.UPDATES: ("keep_system_updated",),
    Category.MALWARE_PROTECTION: ("keep_endpoint_protection_enabled",),
    Category.BACKUP_RECOVERY: ("backup_important_data",),
}

PLATFORM_DEFAULTS: dict[Platform, tuple[str, ...]] = {
    Platform.ROUTER: ("review_router_admin",),
    Platform.NETWORK: ("identify_assets",),
}


def get_guidance_by_id(guidance_id: str) -> D3FENDGuidance:
    return CATALOG_BY_ID[guidance_id].to_guidance()


def get_guidance_for_finding(finding: Finding) -> list[D3FENDGuidance]:
    guidance_ids = _guidance_ids_from_tags(finding.tags)
    if not guidance_ids:
        guidance_ids = _guidance_ids_from_defaults(finding)
    return [get_guidance_by_id(guidance_id) for guidance_id in guidance_ids]


def enrich_finding_guidance(finding: Finding) -> Finding:
    guidance = list(finding.d3fend_guidance)
    guidance_ids = _guidance_ids_from_tags(finding.tags)
    if not guidance_ids and not guidance:
        guidance_ids = _guidance_ids_from_defaults(finding)
    for catalog_guidance in (get_guidance_by_id(guidance_id) for guidance_id in guidance_ids):
        if not _contains_guidance(guidance, catalog_guidance):
            guidance.append(catalog_guidance)
    return finding.model_copy(update={"d3fend_guidance": guidance})


def enrich_report_guidance(report: HomeGuardReport) -> HomeGuardReport:
    findings = [enrich_finding_guidance(finding) for finding in report.findings]
    return report.model_copy(update={"findings": findings})


def _guidance_ids_from_tags(tags: list[str]) -> list[str]:
    guidance_ids: list[str] = []
    for tag in tags:
        normalized = _normalize_tag(tag)
        explicit_id = normalized.replace("-", "_")
        if explicit_id in GUIDANCE_ID_TAGS:
            _append_unique(guidance_ids, explicit_id)
        for guidance_id in TAG_TO_GUIDANCE_IDS.get(normalized, ()):
            _append_unique(guidance_ids, guidance_id)
    return guidance_ids


def _guidance_ids_from_defaults(finding: Finding) -> list[str]:
    guidance_ids: list[str] = []
    for guidance_id in PLATFORM_DEFAULTS.get(finding.platform, ()):
        _append_unique(guidance_ids, guidance_id)
    for guidance_id in CATEGORY_DEFAULTS.get(finding.category, ()):
        _append_unique(guidance_ids, guidance_id)
    if guidance_ids:
        return guidance_ids

    for entry in D3FEND_GUIDANCE_CATALOG:
        if finding.category in entry.applies_to_categories and finding.platform in entry.applies_to_platforms:
            return [entry.guidance_id]
    return []


def _contains_guidance(existing: list[D3FENDGuidance], candidate: D3FENDGuidance) -> bool:
    candidate_key = _guidance_key(candidate)
    return any(_guidance_key(guidance) == candidate_key for guidance in existing)


def _guidance_key(guidance: D3FENDGuidance) -> tuple[str | None, str, str, str]:
    return (
        guidance.guidance_id,
        guidance.category.value,
        guidance.defensive_concept.lower(),
        guidance.home_action.lower(),
    )


def _append_unique(values: list[str], value: str) -> None:
    if value not in values:
        values.append(value)


def _normalize_tag(tag: str) -> str:
    return tag.strip().lower().replace("_", "-")
