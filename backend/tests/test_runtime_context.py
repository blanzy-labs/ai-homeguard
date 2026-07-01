from app.core.platform import LocalPlatform, detect_platform, detect_runtime_environment, get_runtime_context
from app.models.runtime import RuntimeEnvironment


def test_detect_platform_values(monkeypatch) -> None:
    monkeypatch.setattr("platform.system", lambda: "Windows")
    assert detect_platform() == LocalPlatform.WINDOWS

    monkeypatch.setattr("platform.system", lambda: "Darwin")
    assert detect_platform() == LocalPlatform.MACOS

    monkeypatch.setattr("platform.system", lambda: "Linux")
    assert detect_platform() == LocalPlatform.LINUX

    monkeypatch.setattr("platform.system", lambda: "Plan9")
    assert detect_platform() == LocalPlatform.UNKNOWN


def test_docker_detection_from_dockerenv(monkeypatch) -> None:
    monkeypatch.setattr("app.core.platform._path_exists", lambda path: path == "/.dockerenv")
    monkeypatch.setattr("app.core.platform._read_text", lambda path: "")

    assert detect_runtime_environment() == RuntimeEnvironment.DOCKER


def test_docker_detection_from_cgroup(monkeypatch) -> None:
    monkeypatch.setattr("app.core.platform._path_exists", lambda path: False)
    monkeypatch.setattr("app.core.platform._read_text", lambda path: "0::/docker/container-id")

    assert detect_runtime_environment() == RuntimeEnvironment.DOCKER


def test_runtime_context_is_privacy_safe(monkeypatch) -> None:
    monkeypatch.setattr("platform.system", lambda: "Darwin")
    monkeypatch.setattr("platform.machine", lambda: "arm64")
    monkeypatch.setattr("platform.node", lambda: "Rob-Mac-mini.local")
    monkeypatch.setattr("app.core.platform._path_exists", lambda path: False)
    monkeypatch.setattr("app.core.platform._read_text", lambda path: "")

    context = get_runtime_context()
    serialized = context.model_dump_json()

    assert context.detected_platform == "macos"
    assert context.runtime_environment == "native"
    assert context.architecture == "arm64"
    assert context.hostname_present is True
    assert "Rob-Mac-mini" not in serialized
    assert "rob" not in serialized.lower()
    assert "/Users/" not in serialized
    assert "OPENAI_API_KEY" not in serialized
