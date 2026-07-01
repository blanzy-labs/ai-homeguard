from app.checks.macos.filevault import filevault_finding_from_output
from app.checks.macos.firewall import firewall_finding_from_output
from app.checks.macos.gatekeeper import gatekeeper_finding_from_output
from app.checks.macos.listening_ports import listening_ports_finding_from_ports, parse_lsof_listening_ports
from app.checks.macos.remote_login import remote_login_finding_from_output
from app.checks.macos.system_info import system_info_finding_from_output
from app.checks.macos.updates import update_visibility_finding_from_output


def test_mocked_macos_firewall_enabled_maps_to_good() -> None:
    finding = firewall_finding_from_output("Firewall is enabled. (State = 1)")

    assert finding.status == "good"
    assert finding.safe_to_ignore is True


def test_mocked_macos_firewall_disabled_maps_to_fix_soon() -> None:
    finding = firewall_finding_from_output("Firewall is disabled. (State = 0)")

    assert finding.status == "fix_soon"
    assert finding.severity == "medium"


def test_mocked_filevault_on_maps_to_good() -> None:
    finding = filevault_finding_from_output("FileVault is On.")

    assert finding.status == "good"
    assert finding.category == "data_protection"


def test_mocked_filevault_off_maps_to_fix_soon() -> None:
    finding = filevault_finding_from_output("FileVault is Off.")

    assert finding.status == "fix_soon"
    assert finding.severity == "medium"


def test_mocked_gatekeeper_enabled_maps_to_good() -> None:
    finding = gatekeeper_finding_from_output("assessments enabled")

    assert finding.status == "good"
    assert finding.category == "device_posture"


def test_mocked_gatekeeper_disabled_maps_to_fix_soon() -> None:
    finding = gatekeeper_finding_from_output("assessments disabled")

    assert finding.status == "fix_soon"
    assert finding.severity == "medium"


def test_mocked_remote_login_on_maps_to_review() -> None:
    finding = remote_login_finding_from_output("Remote Login: On")

    assert finding.status == "review"
    assert finding.category == "identity_access"
    assert finding.attack_context
    assert finding.attack_context[0].educational_only is True


def test_mocked_macos_ports_with_ssh_and_vnc_map_to_review() -> None:
    finding = listening_ports_finding_from_ports([22, 5900, 49152])

    assert finding.status == "review"
    assert "22" in finding.evidence[0].observed_value
    assert "5900" in finding.evidence[0].observed_value


def test_macos_lsof_parser_reports_ports_only() -> None:
    ports = parse_lsof_listening_ports(
        "\n".join(
            [
                "COMMAND PID USER FD TYPE DEVICE SIZE/OFF NODE NAME",
                "sshd 111 root 5u IPv4 0xabc 0t0 TCP *:22 (LISTEN)",
                "node 222 alice 20u IPv6 0xdef 0t0 TCP localhost:5173 (LISTEN)",
            ]
        )
    )
    finding = listening_ports_finding_from_ports(ports)
    user_facing = " ".join(
        [finding.summary, finding.evidence[0].observed_value, finding.evidence[0].notes or ""]
    )

    assert ports == [22, 5173]
    assert "alice" not in user_facing
    assert "node" not in user_facing


def test_macos_system_info_is_informational() -> None:
    finding = system_info_finding_from_output(
        "ProductName:\t\tmacOS\nProductVersion:\t\t14.5\nBuildVersion:\t\t23F79"
    )

    assert finding.status == "good"
    assert finding.severity == "info"
    assert "does not prove" in (finding.evidence[0].notes or "")


def test_macos_update_visibility_is_informational_review() -> None:
    finding = update_visibility_finding_from_output("ProductVersion:\t\t14.5")

    assert finding.status == "review"
    assert finding.severity == "info"
    assert "fully patched" in finding.summary


def test_all_mocked_macos_findings_include_guidance() -> None:
    findings = [
        firewall_finding_from_output("Firewall is enabled. (State = 1)"),
        filevault_finding_from_output("FileVault is On."),
        gatekeeper_finding_from_output("assessments enabled"),
        remote_login_finding_from_output("Remote Login: Off"),
        listening_ports_finding_from_ports([443]),
        system_info_finding_from_output("ProductName: macOS\nProductVersion: 14.5\nBuildVersion: 23F79"),
        update_visibility_finding_from_output("ProductVersion: 14.5"),
    ]

    assert all(finding.d3fend_guidance for finding in findings)
    assert all(finding.platform == "macos" for finding in findings)
