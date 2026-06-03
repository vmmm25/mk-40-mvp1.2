"""MARK XL — Crypto utilities.

Provides encryption / decryption helpers for sensitive configuration
values such as API keys stored on disk.

Uses Fernet (symmetric AES-128-CBC with HMAC) backed by a
machine-derived key so that keys are encrypted at rest.
"""

from __future__ import annotations

import base64
import hashlib
import logging
import os
from pathlib import Path

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Key derivation
# ---------------------------------------------------------------------------

_KEY_FILE: Path | None = None  # set via set_key_file()


def set_key_file(path: str | Path | None) -> None:
    global _KEY_FILE
    _KEY_FILE = Path(path) if path is not None else None


def _get_machine_key_path() -> Path:
    """Return path to the machine-local key file."""
    if _KEY_FILE is not None:
        return _KEY_FILE
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData"))
    else:
        base = Path.home() / ".config"
    return base / "mark-xl" / "master.key"


def _load_or_create_machine_key() -> bytes:
    """Load the machine-local Fernet key, creating it if absent."""
    key_path = _get_machine_key_path()
    key_path.parent.mkdir(parents=True, exist_ok=True)

    if key_path.exists():
        raw = key_path.read_bytes()
        if len(raw) == 44:  # base64-encoded Fernet key
            return raw

    # Generate a new Fernet key
    from cryptography.fernet import Fernet
    key = Fernet.generate_key()
    key_path.write_bytes(key)
    # Restrict permissions on Unix
    if os.name != "nt":
        key_path.chmod(0o600)
    log.info("Created new master encryption key at %s", key_path)
    return key


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_fernet: object | None = None


def _get_fernet():
    global _fernet
    if _fernet is None:
        from cryptography.fernet import Fernet
        key = _load_or_create_machine_key()
        _fernet = Fernet(key)
    return _fernet


def encrypt(plaintext: str) -> str:
    """Encrypt *plaintext* and return a base64-encoded cipher string."""
    if not plaintext:
        return ""
    f = _get_fernet()
    token = f.encrypt(plaintext.encode("utf-8"))
    return token.decode("utf-8")


def decrypt(ciphertext: str) -> str:
    """Decrypt a base64-encoded cipher string produced by :func:`encrypt`.

    Returns empty string on failure.
    """
    if not ciphertext:
        return ""
    try:
        f = _get_fernet()
        return f.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
    except Exception as exc:
        log.error("Decryption failed: %s", exc)
        return ""


def encrypt_file(src: str | Path, dst: str | Path | None = None) -> bool:
    """Encrypt a file in-place (or to *dst*)."""
    src = Path(src)
    data = src.read_bytes()
    f = _get_fernet()
    token = f.encrypt(data)
    dst = Path(dst) if dst else src
    dst.write_bytes(token)
    return True


def decrypt_file(src: str | Path, dst: str | Path | None = None) -> bool:
    """Decrypt a file in-place (or to *dst*)."""
    src = Path(src)
    data = src.read_bytes()
    try:
        f = _get_fernet()
        plain = f.decrypt(data)
    except Exception as exc:
        log.error("File decryption failed for %s: %s", src, exc)
        return False
    dst = Path(dst) if dst else src
    dst.write_bytes(plain)
    return True


# ---------------------------------------------------------------------------
# Convenience: encrypt all known API keys in api_keys.json
# ---------------------------------------------------------------------------

def encrypt_config_keys(config_path: str | Path) -> int:
    """Encrypt all ``*_key`` / ``*_api_key`` fields in the JSON config.

    Returns the number of fields encrypted.
    """
    import json
    path = Path(config_path)
    if not path.exists():
        return 0

    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    count = 0
    for key in list(data.keys()):
        if key.endswith("_key") or key.endswith("_api_key"):
            val = data[key]
            if val and not val.startswith("gAAAAA"):  # Fernet tokens start with gAAAAA
                data[key] = encrypt(val)
                count += 1

    if count:
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        log.info("Encrypted %d key(s) in %s", count, path)
    return count


def decrypt_config_keys(config_path: str | Path) -> dict[str, str]:
    """Read config and return a dict of decrypted key values."""
    import json
    path = Path(config_path)
    if not path.exists():
        return {}

    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    result = {}
    for key in data:
        if key.endswith("_key") or key.endswith("_api_key"):
            val = data[key]
            result[key] = decrypt(val) if val.startswith("gAAAAA") else val
    return result
