"""Tests for core.crypto — encryption / decryption utilities."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest

from core.crypto import (
    encrypt,
    decrypt,
    encrypt_config_keys,
    decrypt_config_keys,
    set_key_file,
)


@pytest.fixture(autouse=True)
def _isolated_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Use a temporary directory for the master key."""
    key_path = tmp_path / "master.key"
    set_key_file(key_path)
    yield
    set_key_file(None)  # reset


class TestCrypto:
    def test_encrypt_decrypt_roundtrip(self):
        plain = "my-super-secret-api-key-12345"
        cipher = encrypt(plain)
        assert cipher != plain
        assert cipher.startswith("gAAAAA")  # Fernet marker
        assert decrypt(cipher) == plain

    def test_decrypt_empty(self):
        assert decrypt("") == ""

    def test_encrypt_empty(self):
        assert encrypt("") == ""

    def test_decrypt_invalid(self):
        result = decrypt("not-a-valid-token")
        assert result == ""

    def test_encrypt_decrypt_long_text(self):
        plain = "A" * 10_000
        assert decrypt(encrypt(plain)) == plain

    def test_deterministic_different(self):
        """Same plaintext should produce different ciphertexts (IV)."""
        plain = "hello"
        c1 = encrypt(plain)
        c2 = encrypt(plain)
        assert c1 != c2

    # --- config encryption ---

    def test_encrypt_config_keys(self, tmp_path: Path):
        config = {
            "gemini_api_key": "AIzaSy...",
            "openrouter_api_key": "sk-or-v1-...",
            "ollama_url": "http://localhost:11434",
            "selected_provider": "gemini",
        }
        cfg_path = tmp_path / "api_keys.json"
        cfg_path.write_text(json.dumps(config), encoding="utf-8")

        count = encrypt_config_keys(cfg_path)
        assert count == 2  # gemini + openrouter

        # Verify keys are now encrypted
        raw = json.loads(cfg_path.read_text(encoding="utf-8"))
        assert raw["gemini_api_key"].startswith("gAAAAA")
        assert raw["openrouter_api_key"].startswith("gAAAAA")
        assert raw["ollama_url"] == "http://localhost:11434"  # not a key, unchanged

    def test_decrypt_config_keys(self, tmp_path: Path):
        config = {
            "gemini_api_key": "AIzaSyRealKey",
            "ollama_url": "http://localhost:11434",
        }
        cfg_path = tmp_path / "api_keys.json"
        cfg_path.write_text(json.dumps(config), encoding="utf-8")
        encrypt_config_keys(cfg_path)

        decrypted = decrypt_config_keys(cfg_path)
        assert decrypted["gemini_api_key"] == "AIzaSyRealKey"
        assert "ollama_url" not in decrypted  # not a *_key field

    def test_encrypt_config_keys_noop_for_already_encrypted(self, tmp_path: Path):
        config = {"gemini_api_key": encrypt("already-encrypted")}
        cfg_path = tmp_path / "api_keys.json"
        cfg_path.write_text(json.dumps(config), encoding="utf-8")

        count = encrypt_config_keys(cfg_path)
        assert count == 0  # already Fernet-format
