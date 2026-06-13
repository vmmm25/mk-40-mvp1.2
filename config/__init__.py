# config/__init__.py
"""Configuration access layer.

Reads from memory.config_manager which handles encryption/decryption
of API keys at rest.  Never read api_keys.json directly — use this module
or memory.config_manager.load_config() instead.

Also sets offline-first environment variables for HuggingFace/Transformers
to prevent accidental internet access during local development.
"""
import os

from memory.config_manager import load_config as _load_config


# ── Offline-first env vars (portado de Mark-XL) ────────────────────────
# Previene descargas accidentales de modelos/tokenizers desde HF.
# Si necesitas descargar algo, usa: os.environ.pop("HF_HUB_OFFLINE")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("HF_DATASETS_OFFLINE", "1")
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")


def get_config() -> dict:
    """Return full config dict with decrypted API keys.

    Uses memory.config_manager.load_config() which transparently
    decrypts Fernet-encrypted values.
    """
    return _load_config()


def get_os() -> str:
    """Returns: 'windows' | 'mac' | 'linux'"""
    return get_config().get("os_system", "windows").lower()


def is_windows() -> bool:
    return get_os() == "windows"


def is_mac() -> bool:
    return get_os() == "mac"


def is_linux() -> bool:
    return get_os() == "linux"