from app.network.guardrails import (
    classify_network_target,
    is_link_local_ip,
    is_loopback_ip,
    is_private_ip,
    is_public_ip,
    validate_network_scope,
)


def test_private_ipv4_ranges_are_classified_private() -> None:
    assert is_private_ip("10.1.2.3") is True
    assert is_private_ip("172.16.0.1") is True
    assert is_private_ip("172.31.255.254") is True
    assert is_private_ip("192.168.1.10") is True
    assert classify_network_target("192.168.1.0/24") == "private"


def test_public_ipv4_addresses_are_rejected() -> None:
    assert is_public_ip("8.8.8.8") is True
    assert classify_network_target("8.8.8.8") == "public"
    result = validate_network_scope(["192.168.1.0/24", "8.8.8.8"])

    assert result.allowed is False
    assert result.rejected_targets == ["8.8.8.8"]


def test_loopback_and_link_local_are_classified_separately() -> None:
    assert is_loopback_ip("127.0.0.1") is True
    assert classify_network_target("127.0.0.1") == "loopback"
    assert is_link_local_ip("169.254.10.10") is True
    assert classify_network_target("169.254.10.10") == "link_local"


def test_invalid_inputs_and_hostnames_are_rejected() -> None:
    result = validate_network_scope(["router.local", "example.com", "not an ip"])

    assert result.allowed is False
    assert result.classifications["router.local"] == "hostname_rejected"
    assert result.classifications["example.com"] == "hostname_rejected"
    assert result.classifications["not an ip"] == "hostname_rejected"


def test_ipv6_loopback_and_ula_are_classified_safely() -> None:
    assert classify_network_target("::1") == "loopback"
    assert classify_network_target("fc00::1") == "private"
    assert classify_network_target("2001:4860:4860::8888") in {"public", "unsupported"}


def test_overbroad_private_supernet_is_not_allowed() -> None:
    assert classify_network_target("10.0.0.0/7") == "unsupported"
