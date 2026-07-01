from app.checks.linux.clamav import clamav_finding_from_version, clamav_missing_finding
from app.checks.linux.disk_encryption import disk_encryption_finding_from_lsblk
from app.checks.linux.firewall import firewall_finding_from_results
from app.checks.linux.listening_ports import listening_ports_finding_from_ports, parse_ss_listening_ports
from app.checks.linux.ssh import ssh_finding_from_results
from app.checks.linux.system_info import system_info_finding_from_outputs
from app.checks.linux.updates import update_visibility_finding_from_outputs
from app.core.command_runner import CommandResult


def result(command_name: str, stdout: str = "", return_code: int = 0, error: str | None = None) -> CommandResult:
    return CommandResult(command_name=command_name, stdout=stdout, return_code=return_code, error=error)


def test_mocked_ufw_active_maps_to_good() -> None:
    finding = firewall_finding_from_results(
        [
            result("linux_firewall_ufw", "Status: active"),
            result("linux_firewall_firewall_cmd", "", error="FileNotFoundError"),
            result("linux_firewall_firewalld_active", "inactive", return_code=3),
        ]
    )

    assert finding is not None
    assert finding.status == "good"


def test_mocked_firewalld_active_maps_to_good() -> None:
    finding = firewall_finding_from_results(
        [
            result("linux_firewall_ufw", "Status: inactive"),
            result("linux_firewall_firewall_cmd", "running"),
            result("linux_firewall_firewalld_active", "active"),
        ]
    )

    assert finding is not None
    assert finding.status == "good"


def test_mocked_firewall_inactive_maps_to_fix_soon() -> None:
    finding = firewall_finding_from_results(
        [
            result("linux_firewall_ufw", "Status: inactive"),
            result("linux_firewall_firewall_cmd", "not running", return_code=252),
            result("linux_firewall_firewalld_active", "inactive", return_code=3),
        ]
    )

    assert finding is not None
    assert finding.status == "fix_soon"


def test_mocked_ssh_active_maps_to_review() -> None:
    finding = ssh_finding_from_results(
        [
            result("linux_ssh_systemctl_ssh", "inactive", return_code=3),
            result("linux_ssh_systemctl_sshd", "active"),
            result("linux_ssh_service", "ssh is running"),
        ]
    )

    assert finding is not None
    assert finding.status == "review"
    assert finding.attack_context


def test_mocked_linux_ports_with_ssh_and_vnc_map_to_review() -> None:
    finding = listening_ports_finding_from_ports([22, 5900, 49152])

    assert finding.status == "review"
    assert "22" in finding.evidence[0].observed_value
    assert "5900" in finding.evidence[0].observed_value


def test_linux_ss_parser_reports_ports_only() -> None:
    ports = parse_ss_listening_ports(
        "\n".join(
            [
                "Netid State Recv-Q Send-Q Local Address:Port Peer Address:Port",
                "tcp LISTEN 0 128 0.0.0.0:22 0.0.0.0:*",
                "tcp LISTEN 0 128 [::]:5173 [::]:*",
            ]
        )
    )
    finding = listening_ports_finding_from_ports(ports)
    user_facing = " ".join(
        [finding.summary, finding.evidence[0].observed_value, finding.evidence[0].notes or ""]
    )

    assert ports == [22, 5173]
    assert "0.0.0.0" not in user_facing
    assert "[::]" not in user_facing


def test_clamav_installed_maps_to_good_info() -> None:
    finding = clamav_finding_from_version("ClamAV 1.4.1/27000/Wed Jul  1 10:00:00 2026")

    assert finding.status == "good"
    assert finding.severity == "info"
    assert "did not run a file scan" in (finding.evidence[0].notes or "")


def test_clamav_missing_maps_to_review_info() -> None:
    finding = clamav_missing_finding()

    assert finding.status == "review"
    assert finding.severity == "info"
    assert "did not run a file scan" in (finding.evidence[0].notes or "")


def test_linux_system_info_is_informational() -> None:
    finding = system_info_finding_from_outputs('PRETTY_NAME="Ubuntu 24.04 LTS"', "6.8.0-31-generic")

    assert finding.status == "good"
    assert finding.severity == "info"


def test_linux_update_visibility_is_informational_review() -> None:
    finding = update_visibility_finding_from_outputs(
        'PRETTY_NAME="Ubuntu 24.04 LTS"',
        "6.8.0-31-generic",
    )

    assert finding.status == "review"
    assert finding.severity == "info"
    assert "fully patched" in finding.summary


def test_linux_disk_encryption_uncertain_maps_to_unable() -> None:
    finding = disk_encryption_finding_from_lsblk("NAME FSTYPE FSVER LABEL UUID FSAVAIL FSUSE% MOUNTPOINTS\nsda\n")

    assert finding.status == "unable_to_check"
    assert "not treated as proof" in (finding.evidence[0].notes or "")


def test_linux_disk_encryption_luks_marker_maps_to_good() -> None:
    finding = disk_encryption_finding_from_lsblk("nvme0n1p3 crypto_LUKS 2")

    assert finding.status == "good"
    assert finding.category == "data_protection"


def test_all_mocked_linux_findings_include_guidance() -> None:
    firewall = firewall_finding_from_results(
        [
            result("linux_firewall_ufw", "Status: active"),
            result("linux_firewall_firewall_cmd", "not running", return_code=252),
            result("linux_firewall_firewalld_active", "inactive", return_code=3),
        ]
    )
    ssh = ssh_finding_from_results(
        [
            result("linux_ssh_systemctl_ssh", "inactive", return_code=3),
            result("linux_ssh_systemctl_sshd", "inactive", return_code=3),
            result("linux_ssh_service", "ssh is not running", return_code=3),
        ]
    )
    assert firewall is not None
    assert ssh is not None

    findings = [
        firewall,
        ssh,
        listening_ports_finding_from_ports([12345]),
        clamav_finding_from_version("ClamAV 1.4.1"),
        system_info_finding_from_outputs('PRETTY_NAME="Ubuntu 24.04 LTS"', "6.8.0-31-generic"),
        update_visibility_finding_from_outputs('PRETTY_NAME="Ubuntu 24.04 LTS"', "6.8.0-31-generic"),
        disk_encryption_finding_from_lsblk("nvme0n1p3 crypto_LUKS 2"),
    ]

    assert all(finding.d3fend_guidance for finding in findings)
    assert all(finding.platform == "linux" for finding in findings)
