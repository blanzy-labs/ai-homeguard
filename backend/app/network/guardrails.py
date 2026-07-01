import ipaddress

from app.models.network import NetworkScopeValidation

PRIVATE_IPV4_RANGES = (
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
)
UNIQUE_LOCAL_IPV6 = ipaddress.ip_network("fc00::/7")


def is_private_ip(value: str) -> bool:
    address = _parse_ip(value)
    return bool(address and _is_allowed_private_address(address))


def is_loopback_ip(value: str) -> bool:
    address = _parse_ip(value)
    return bool(address and address.is_loopback)


def is_link_local_ip(value: str) -> bool:
    address = _parse_ip(value)
    return bool(address and address.is_link_local)


def is_public_ip(value: str) -> bool:
    address = _parse_ip(value)
    return bool(address and address.is_global)


def classify_network_target(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        return "invalid"

    try:
        network = ipaddress.ip_network(stripped, strict=False)
    except ValueError:
        if _looks_like_hostname(stripped):
            return "hostname_rejected"
        address = _parse_ip(stripped)
        if address is None:
            return "invalid"
        return _classify_ip(address)

    if network.version == 4:
        if network.is_loopback:
            return "loopback"
        if network.is_link_local:
            return "link_local"
        if any(network.subnet_of(private_range) for private_range in PRIVATE_IPV4_RANGES):
            return "private"
        if any(network.overlaps(private_range) for private_range in PRIVATE_IPV4_RANGES):
            return "unsupported"
        if network.is_global:
            return "public"
        return "unsupported"

    if network.is_loopback:
        return "loopback"
    if network.subnet_of(UNIQUE_LOCAL_IPV6):
        return "private"
    return "unsupported"


def validate_network_scope(targets_or_ranges: list[str]) -> NetworkScopeValidation:
    classifications: dict[str, str] = {}
    rejected: list[str] = []
    for target in targets_or_ranges:
        classification = classify_network_target(target)
        classifications[target] = classification
        if classification not in {"private", "loopback"}:
            rejected.append(target)

    return NetworkScopeValidation(
        allowed=not rejected,
        classifications=classifications,
        rejected_targets=rejected,
        safety_notes=[
            "Only private local ranges are allowed for future local network checks.",
            "Public IPs, hostnames, domains, and unsupported values are rejected.",
            "This version does not run active discovery or port scanning.",
        ],
    )


def _classify_ip(address: ipaddress.IPv4Address | ipaddress.IPv6Address) -> str:
    if address.is_loopback:
        return "loopback"
    if address.is_link_local:
        return "link_local"
    if address.version == 6 and address in UNIQUE_LOCAL_IPV6:
        return "private"
    if _is_allowed_private_address(address):
        return "private"
    if address.is_global:
        return "public"
    if address.version == 6:
        return "unsupported"
    return "invalid"


def _parse_ip(value: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    try:
        return ipaddress.ip_address(value.strip())
    except ValueError:
        return None


def _is_allowed_private_address(address: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    if isinstance(address, ipaddress.IPv6Address):
        return address in UNIQUE_LOCAL_IPV6
    return any(address in private_range for private_range in PRIVATE_IPV4_RANGES)


def _looks_like_hostname(value: str) -> bool:
    if "/" in value:
        return False
    return any(char.isalpha() for char in value)
