"""MARK XL — Shared test fixtures and configuration."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture
def temp_config_dir():
    """Create a temporary directory to isolate config file writes."""
    with tempfile.TemporaryDirectory() as tmp:
        original = "memory.config_manager"
        # We'll patch BASE_DIR at the module level
        with patch("memory.config_manager.BASE_DIR", Path(tmp)):
            with patch("memory.config_manager.CONFIG_DIR", Path(tmp) / "config"):
                with patch("memory.config_manager.CONFIG_FILE", Path(tmp) / "config" / "api_keys.json"):
                    # Ensure config dir exists
                    (Path(tmp) / "config").mkdir(parents=True, exist_ok=True)
                    yield tmp


@pytest.fixture
def cleaned_config_cache():
    """Clear the config cache before and after each test."""
    import memory.config_manager as cm
    cm._config_cache = None
    cm._cache_time = 0
    yield
    cm._config_cache = None
    cm._cache_time = 0
