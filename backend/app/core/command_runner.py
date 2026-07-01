import subprocess
from collections.abc import Sequence

from pydantic import BaseModel, Field

from app.core.platform import LocalPlatform, current_platform


class CommandResult(BaseModel):
    command_name: str
    return_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False
    supported: bool = True
    error: str | None = None


class SafeCommandRunner:
    def __init__(self, allowed_commands: dict[str, tuple[str, ...]]) -> None:
        self.allowed_commands = allowed_commands

    def run(
        self,
        command_name: str,
        args: Sequence[str],
        timeout_seconds: int = 10,
        platform_name: LocalPlatform | None = None,
    ) -> CommandResult:
        active_platform = platform_name or current_platform()
        if active_platform != LocalPlatform.WINDOWS:
            return CommandResult(
                command_name=command_name,
                supported=False,
                error=f"Unsupported platform for Windows check: {active_platform.value}",
            )

        allowed_prefix = self.allowed_commands.get(command_name)
        if allowed_prefix is None or tuple(args[: len(allowed_prefix)]) != allowed_prefix:
            return CommandResult(
                command_name=command_name,
                return_code=None,
                error="Command is not allowlisted for this check.",
            )

        try:
            completed = subprocess.run(
                list(args),
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                shell=False,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            return CommandResult(
                command_name=command_name,
                return_code=None,
                stdout=error.stdout or "",
                stderr="Command timed out.",
                timed_out=True,
                error="Command timed out.",
            )
        except OSError as error:
            return CommandResult(
                command_name=command_name,
                return_code=None,
                error=error.__class__.__name__,
            )

        return CommandResult(
            command_name=command_name,
            return_code=completed.returncode,
            stdout=completed.stdout[:20000],
            stderr=_summarize_stderr(completed.stderr),
        )


def _summarize_stderr(stderr: str) -> str:
    if not stderr:
        return ""
    compact = " ".join(stderr.split())
    return compact[:500]
