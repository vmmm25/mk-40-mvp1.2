"""Tests for memory.config_manager — configuration persistence and provider defaults."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest


class TestDefaults:
    """DEFAULT_CONFIG shape and getter fallbacks."""

    def test_defaults_have_all_keys(self):
        from memory.config_manager import DEFAULT_CONFIG
        assert "gemini_api_key" in DEFAULT_CONFIG
        assert "openrouter_api_key" in DEFAULT_CONFIG
        assert "ollama_url" in DEFAULT_CONFIG
        assert "lmstudio_url" in DEFAULT_CONFIG
        assert "selected_provider" in DEFAULT_CONFIG
        assert "model" in DEFAULT_CONFIG
        assert "os_system" in DEFAULT_CONFIG
        assert "audio_input_device" in DEFAULT_CONFIG
        assert "audio_output_device" in DEFAULT_CONFIG
        assert "audio_volume" in DEFAULT_CONFIG

    def test_lmstudio_default_url(self):
        from memory.config_manager import DEFAULT_CONFIG
        assert DEFAULT_CONFIG["lmstudio_url"] == "http://localhost:1234"

    def test_selected_provider_default(self):
        from memory.config_manager import DEFAULT_CONFIG
        assert DEFAULT_CONFIG["selected_provider"] == "gemini"


class TestLoadConfig:
    """load_config() with no file, fresh file, and cache."""

    def test_load_config_returns_defaults_when_no_file(self, cleaned_config_cache, temp_config_dir):
        from memory.config_manager import load_config
        cfg = load_config()
        assert cfg["selected_provider"] == "gemini"
        assert cfg["lmstudio_url"] == "http://localhost:1234"
        assert cfg["ollama_url"] == "http://localhost:11434"

    def test_load_config_merges_saved_data(self, cleaned_config_cache, temp_config_dir):
        from memory.config_manager import load_config, CONFIG_FILE
        # Write partial data
        CONFIG_FILE.write_text(json.dumps({"selected_provider": "lmstudio"}), encoding="utf-8")
        cfg = load_config()
        assert cfg["selected_provider"] == "lmstudio"
        assert cfg["gemini_api_key"] == ""  # from defaults
        assert cfg["lmstudio_url"] == "http://localhost:1234"

    def test_load_config_overrides_default(self, cleaned_config_cache, temp_config_dir):
        from memory.config_manager import load_config, CONFIG_FILE
        CONFIG_FILE.write_text(json.dumps({"lmstudio_url": "http://192.168.1.100:1234"}), encoding="utf-8")
        cfg = load_config()
        assert cfg["lmstudio_url"] == "http://192.168.1.100:1234"

    def test_load_config_caching(self, cleaned_config_cache, temp_config_dir):
        from memory.config_manager import load_config, save_config, CONFIG_FILE
        # First load populates cache
        cfg1 = load_config()
        # Modify the file directly (behind cache's back)
        CONFIG_FILE.write_text(json.dumps({"selected_provider": "ollama"}), encoding="utf-8")
        # Cache should still return old value
        cfg2 = load_config()
        assert cfg2["selected_provider"] == "gemini"
        # Save invalidates cache
        save_config({"selected_provider": "openrouter"})
        cfg3 = load_config()
        assert cfg3["selected_provider"] == "openrouter"


class TestSaveConfig:
    """save_config() writes and merges correctly."""

    def test_save_and_load_roundtrip(self, cleaned_config_cache, temp_config_dir):
        from memory.config_manager import save_config, load_config
        save_config({"lmstudio_url": "http://localhost:8080"})
        cfg = load_config()
        assert cfg["lmstudio_url"] == "http://localhost:8080"

    def test_save_merges_without_losing_keys(self, cleaned_config_cache, temp_config_dir):
        from memory.config_manager import save_config, load_config
        save_config({"selected_provider": "lmstudio"})
        save_config({"model": "local-model"})
        cfg = load_config()
        assert cfg["selected_provider"] == "lmstudio"
        assert cfg["model"] == "local-model"
        assert cfg["lmstudio_url"] == "http://localhost:1234"


class TestGetters:
    """Convenience getter functions."""

    def test_get_lmstudio_url_default(self, cleaned_config_cache):
        from memory.config_manager import get_lmstudio_url
        assert get_lmstudio_url() == "http://localhost:1234"

    def test_get_lmstudio_url_saved(self, cleaned_config_cache, temp_config_dir):
        from memory.config_manager import save_config, get_lmstudio_url
        save_config({"lmstudio_url": "http://192.168.1.50:1234"})
        assert get_lmstudio_url() == "http://192.168.1.50:1234"

    def test_get_gemini_key_none_when_empty(self, cleaned_config_cache, temp_config_dir):
        from memory.config_manager import get_gemini_key
        assert get_gemini_key() is None

    def test_get_gemini_key_value(self, cleaned_config_cache, temp_config_dir):
        from memory.config_manager import save_config, get_gemini_key
        save_config({"gemini_api_key": "AIzaSyTest123"})
        assert get_gemini_key() == "AIzaSyTest123"

    def test_get_openrouter_key_none_when_empty(self, cleaned_config_cache, temp_config_dir):
        from memory.config_manager import get_openrouter_key
        assert get_openrouter_key() is None

    def test_get_ollama_url_default(self, cleaned_config_cache):
        from memory.config_manager import get_ollama_url
        assert get_ollama_url() == "http://localhost:11434"

    def test_get_selected_provider_default(self, cleaned_config_cache):
        from memory.config_manager import get_selected_provider
        assert get_selected_provider() == "gemini"

    def test_get_model_default(self, cleaned_config_cache, temp_config_dir):
        from memory.config_manager import get_model
        assert get_model() == ""

    def test_get_os_system_default(self, cleaned_config_cache):
        from memory.config_manager import get_os_system
        assert get_os_system() == "windows"


class TestIsConfigured:
    """is_configured() validation rules."""

    def test_gemini_requires_key(self, cleaned_config_cache, temp_config_dir):
        from memory.config_manager import save_config, is_configured
        save_config({"selected_provider": "gemini", "gemini_api_key": ""})
        assert is_configured() is False

    def test_gemini_accepts_valid_key(self, cleaned_config_cache, temp_config_dir):
        from memory.config_manager import save_config, is_configured
        save_config({"selected_provider": "gemini", "gemini_api_key": "AIzaSy" + "a" * 12})
        assert is_configured() is True

    def test_ollama_accepts_any_url(self, cleaned_config_cache, temp_config_dir):
        from memory.config_manager import save_config, is_configured
        save_config({"selected_provider": "ollama", "ollama_url": "http://localhost:11434"})
        assert is_configured() is True

    def test_ollama_rejects_empty_url(self, cleaned_config_cache, temp_config_dir):
        from memory.config_manager import save_config, is_configured
        save_config({"selected_provider": "ollama", "ollama_url": ""})
        assert is_configured() is False

    def test_openrouter_requires_key(self, cleaned_config_cache, temp_config_dir):
        from memory.config_manager import save_config, is_configured
        save_config({"selected_provider": "openrouter", "openrouter_api_key": ""})
        assert is_configured() is False

    def test_openrouter_accepts_valid_key(self, cleaned_config_cache, temp_config_dir):
        from memory.config_manager import save_config, is_configured
        save_config({"selected_provider": "openrouter", "openrouter_api_key": "sk-or-v1-test"})
        assert is_configured() is True

    def test_lmstudio_accepts_valid_url(self, cleaned_config_cache, temp_config_dir):
        from memory.config_manager import save_config, is_configured
        save_config({"selected_provider": "lmstudio", "lmstudio_url": "http://localhost:1234"})
        assert is_configured() is True

    def test_lmstudio_rejects_empty_url(self, cleaned_config_cache, temp_config_dir):
        from memory.config_manager import save_config, is_configured
        save_config({"selected_provider": "lmstudio", "lmstudio_url": ""})
        assert is_configured() is False

    def test_unknown_provider_not_configured(self, cleaned_config_cache, temp_config_dir):
        from memory.config_manager import save_config, is_configured
        save_config({"selected_provider": "nonexistent"})
        assert is_configured() is False
