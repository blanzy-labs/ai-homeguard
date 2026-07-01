import pytest

from app.network.guardrails import (
    limit_subnet_size,
    reject_hostnames,
    reject_public_targets,
    validate_private_subnet,
)


def test_validate_private_subnet_accepts_rfc1918_ipv4_only() -> None:
    assert str(validate_private_subnet("192.168.1.0/24")) == "192.168.1.0/24"
    assert str(validate_private_subnet("10.0.0.12")) == "10.0.0.12/32"
    assert str(validate_private_subnet("172.16.4.0/24")) == "172.16.4.0/24"


@pytest.mark.parametrize("target", ["8.8.8.8", "example.com", "127.0.0.1", "169.254.1.1", "fc00::/7"])
def test_validate_private_subnet_rejects_unsupported_targets(target: str) -> None:
    with pytest.raises(ValueError):
        validate_private_subnet(target)


def test_reject_helpers_block_public_targets_and_hostnames() -> None:
    with pytest.raises(ValueError):
        reject_public_targets(["192.168.1.0/24", "1.1.1.1"])
    with pytest.raises(ValueError):
        reject_hostnames(["192.168.1.0/24", "router.local"])


def test_limit_subnet_size_is_conservative() -> None:
    hosts = limit_subnet_size(validate_private_subnet("192.168.1.0/24"), max_hosts=64)

    assert len(hosts) == 64
    assert str(hosts[0]) == "192.168.1.1"

    with pytest.raises(ValueError):
        limit_subnet_size(validate_private_subnet("10.0.0.0/8"), max_hosts=64)
    with pytest.raises(ValueError):
        limit_subnet_size(validate_private_subnet("192.168.1.0/24"), max_hosts=257)
