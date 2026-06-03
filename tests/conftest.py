"""Shared fixtures and configuration for the MARK XL test suite."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# Ensure the project root is on sys.path so imports like "core.cache" work
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ── Global fixtures ──────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _patch_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Provide a clean environment for every test."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)


@pytest.fixture
def sample_message_dict() -> dict:
    return {
        "role": "assistant",
        "content": "Hello from Ollama!",
        "tool_calls": None,
    }


@pytest.fixture
def sample_tool_call_dict() -> dict:
    return {
        "role": "assistant",
        "content": "",
        "tool_calls": [
            {
                "function": {
                    "name": "get_weather",
                    "arguments": '{"city": "London"}',
                }
            }
        ],
    }


# ── Fixtures used by test_config_manager.py ──────────────────────────
# These must be kept stable — existing tests depend on them.

@pytest.fixture
def temp_config_dir(tmp_path: Path) -> Path:
    """Return a temporary directory to use as the config directory."""
    d = tmp_path / "config"
    d.mkdir(parents=True, exist_ok=True)
    return d


@pytest.fixture
def cleaned_config_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch memory.config_manager to use an isolated temp directory
    and reset the in-memory cache before each test."""
    from memory import config_manager

    test_config_dir = tmp_path / "config"
    test_config_dir.mkdir(parents=True, exist_ok=True)
    test_config_file = test_config_dir / "api_keys.json"

    monkeypatch.setattr(config_manager, "CONFIG_DIR", test_config_dir)
    monkeypatch.setattr(config_manager, "CONFIG_FILE", test_config_file)
    monkeypatch.setattr(config_manager, "_config_cache", None)
    monkeypatch.setattr(config_manager, "_cache_time", 0)

    yield

    config_manager._config_cache = None
    config_manager._cache_time = 0
