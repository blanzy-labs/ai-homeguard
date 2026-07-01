from app.checks.linux.base import LINUX_ALLOWED_COMMANDS
from app.checks.macos.base import MACOS_ALLOWED_COMMANDS


def test_local_check_allowlists_do_not_include_prohibited_tools() -> None:
    all_args = [
        arg
        for command in [*MACOS_ALLOWED_COMMANDS.values(), *LINUX_ALLOWED_COMMANDS.values()]
        for arg in command
    ]
    command_text = " ".join(all_args).lower()

    for prohibited in [
        "sudo",
        "nmap",
        "tcpdump",
        "tshark",
        "wireshark",
        "aircrack",
        "hydra",
        "john",
        "hashcat",
        "sshpass",
        "softwareupdate",
    ]:
        assert prohibited not in command_text


def test_clamav_allowlist_is_version_only() -> None:
    assert LINUX_ALLOWED_COMMANDS["linux_clamscan_version"] == ("clamscan", "--version")
    assert LINUX_ALLOWED_COMMANDS["linux_freshclam_version"] == ("freshclam", "--version")


def test_linux_allowlist_does_not_run_package_updates_or_scans() -> None:
    rendered = [" ".join(command) for command in LINUX_ALLOWED_COMMANDS.values()]

    assert all(" update" not in command for command in rendered)
    assert all(" upgrade" not in command for command in rendered)
    assert all(" install" not in command for command in rendered)
    assert all("clamscan --version" in command or "clamscan" not in command for command in rendered)


def test_unified_local_runner_does_not_define_scan_or_remediation_commands() -> None:
    source_path = "app/checks/local_runner.py"
    source = open(source_path, encoding="utf-8").read().lower()

    for prohibited in ["nmap", "tcpdump", "tshark", "sudo", "subprocess", "clamscan", "softwareupdate"]:
        assert prohibited not in source


def test_report_export_modules_do_not_persist_or_call_external_services() -> None:
    for source_path in ["app/reports/markdown.py", "app/reports/json_export.py", "app/reports/merge.py"]:
        source = open(source_path, encoding="utf-8").read().lower()
        for prohibited in [
            "open(",
            "write_text",
            "requests",
            "httpx",
            "openai",
            "telemetry",
            "sqlite",
            "postgres",
            "subprocess",
            "nmap",
        ]:
            assert prohibited not in source
