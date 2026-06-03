"""Tests for core.sandbox — safe code execution."""

from __future__ import annotations

import pytest

from core.sandbox import (
    run_python,
    run_shell,
    SandboxResult,
    _is_dangerous,
)


class TestIsDangerous:
    def test_blocked_commands(self):
        assert _is_dangerous("rm -rf /") is True
        assert _is_dangerous("echo rm -rf /") is False  # inside echo is OK
        assert _is_dangerous("sudo rm -rf /*") is True
        assert _is_dangerous("format C:") is True
        assert _is_dangerous("shutdown -h now") is True

    def test_safe_commands(self):
        assert _is_dangerous("ls -la") is False
        assert _is_dangerous("echo hello") is False
        assert _is_dangerous("cat /etc/passwd") is False


@pytest.mark.asyncio
class TestRunPython:
    async def test_simple_print(self):
        result = await run_python("print('hello')")
        assert result.success is True
        assert "hello" in result.stdout.strip()

    async def test_return_value(self):
        code = """
result = 2 + 2
print(f"The answer is {result}")
"""
        result = await run_python(code)
        assert result.success is True
        assert "The answer is 4" in result.stdout

    async def test_syntax_error(self):
        result = await run_python("this is not valid python")
        assert result.success is False
        assert result.stderr or not result.stdout

    async def test_timeout(self):
        result = await run_python("import time; time.sleep(100)", timeout=0.5)
        assert result.timed_out is True
        assert result.success is False

    async def test_empty_code(self):
        result = await run_python("")
        assert result.success is True
        assert result.exit_code == 0


@pytest.mark.asyncio
class TestRunShell:
    async def test_echo(self):
        result = await run_shell("echo hello world")
        assert result.success is True
        assert "hello world" in result.stdout

    async def test_dangerous_blocked(self):
        result = await run_shell("rm -rf /")
        assert result.success is False
        assert "blocked" in result.stderr.lower()

    async def test_timeout(self):
        # python -c "import time; time.sleep(N)" is cross-platform (sleep is not in cmd.exe)
        result = await run_shell(
            'python -c "import time; time.sleep(100)"', timeout=0.5
        )
        assert result.timed_out is True
