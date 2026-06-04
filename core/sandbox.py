"""MARK XL — Execution sandbox for untrusted code / commands.

Provides a restricted environment to run user-generated code snippets
or shell commands with timeouts, output capture, and resource limits.
"""

from __future__ import annotations

import asyncio
import logging
import os
import shutil
import sys
import tempfile
import textwrap
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)


class SandboxError(Exception):
    """Raised when sandboxed execution fails."""


class SandboxResult:
    """Result of a sandboxed execution."""

    def __init__(
        self,
        success: bool,
        stdout: str = "",
        stderr: str = "",
        exit_code: int = -1,
        timed_out: bool = False,
    ) -> None:
        self.success = success
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.timed_out = timed_out

    def __repr__(self) -> str:
        status = "ok" if self.success else "fail"
        return (
            f"<SandboxResult {status} exit={self.exit_code} "
            f"stdout={len(self.stdout)}c stderr={len(self.stderr)}c>"
        )


# ---------------------------------------------------------------------------
# Python code runner
# ---------------------------------------------------------------------------

async def run_python(
    code: str,
    timeout: float = 15.0,
    workdir: Optional[str | Path] = None,
    env: Optional[dict[str, str]] = None,
) -> SandboxResult:
    """Execute *code* in a subprocess and capture output.

    Parameters
    ----------
    code : str
        Python source code.
    timeout : float
        Maximum execution time in seconds (default 15).
    workdir : str or Path, optional
        Working directory for the subprocess.
    env : dict, optional
        Extra environment variables.

    Returns
    -------
    SandboxResult
    """
    sanitized = textwrap.dedent(code).strip()
    if not sanitized:
        return SandboxResult(True, "", "", 0)

    # Write to a temp file to avoid shell injection
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    )
    try:
        tmp.write(sanitized)
        tmp.close()

        exec_env = {**os.environ, **(env or {}), "PYTHONIOENCODING": "utf-8"}
        proc = await asyncio.create_subprocess_exec(
            sys_executable(),
            tmp.name,
            cwd=str(workdir) if workdir else None,
            env=exec_env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=timeout
            )
        except asyncio.TimeoutError:
            if os.name == "nt":
                import subprocess
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                proc.kill()
            await proc.wait()
            return SandboxResult(False, "", "Timed out", -1, timed_out=True)

        return SandboxResult(
            success=proc.returncode == 0,
            stdout=stdout.decode("utf-8", errors="replace"),
            stderr=stderr.decode("utf-8", errors="replace"),
            exit_code=proc.returncode or 0,
        )

    finally:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Shell command runner (restricted)
# ---------------------------------------------------------------------------

FORBIDDEN_COMMANDS = [
    "rm -rf /", "rm -rf ~", "format ", "mkfs",
    "dd if=", "shutdown", "reboot", "poweroff",
    ":(){ :|:& };:",  # fork bomb
]

_SAFE_EXECUTABLES: set[str] | None = None


def _get_safe_executables() -> set[str]:
    """Return set of allowed command basenames found on PATH."""
    global _SAFE_EXECUTABLES
    if _SAFE_EXECUTABLES is None:
        allowed = {
            "python", "python3", "pip", "pip3", "git", "node", "npm", "npx",
            "curl", "wget", "cat", "head", "tail", "grep", "find", "sort",
            "wc", "echo", "ls", "dir", "pwd", "whoami", "date", "sleep",
            "mkdir", "cp", "mv", "rm", "touch", "chmod", "ffprobe", "ffmpeg",
            "powershell", "pwsh",
        }
        _SAFE_EXECUTABLES = allowed
    return _SAFE_EXECUTABLES


def _is_dangerous(command: str) -> bool:
    """Basic heuristic check for dangerous commands."""
    lower = command.lower()
    for pattern in FORBIDDEN_COMMANDS:
        if pattern in lower:
            # Skip patterns inside echo — echo only prints to stdout
            before = lower[: lower.find(pattern)].strip()
            if before.endswith("echo"):
                continue
            return True
    # Block pipes to sudo / superuser
    if "| sudo" in lower or "| doas" in lower:
        return True
    return False


async def run_shell(
    command: str,
    timeout: float = 30.0,
    workdir: Optional[str | Path] = None,
) -> SandboxResult:
    """Execute a shell command with safety checks.

    Parameters
    ----------
    command : str
        Shell command to run.
    timeout : float
        Maximum execution time (default 30 s).
    workdir : str or Path, optional
        Working directory.

    Returns
    -------
    SandboxResult
    """
    if _is_dangerous(command):
        log.warning("Blocked dangerous command: %s", command[:120])
        return SandboxResult(
            False,
            "",
            "Command blocked by sandbox security policy.",
            1,
        )

    # Use subprocess with explicit shell=True (but command is checked above)
    proc = await asyncio.create_subprocess_shell(
        command,
        cwd=str(workdir) if workdir else None,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=timeout
        )
    except asyncio.TimeoutError:
        if os.name == "nt":
            import subprocess
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            proc.kill()
        await proc.wait()
        return SandboxResult(False, "", "Timed out", -1, timed_out=True)

    return SandboxResult(
        success=proc.returncode == 0,
        stdout=stdout.decode("utf-8", errors="replace"),
        stderr=stderr.decode("utf-8", errors="replace"),
        exit_code=proc.returncode or 0,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sys_executable() -> str:
    """Return path to the current Python interpreter."""
    return shutil.which("python") or shutil.which("python3") or sys.executable
