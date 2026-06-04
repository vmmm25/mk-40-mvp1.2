"""MARK XL — Configuration manager for multi-provider support.

Manages api_keys.json which now supports multiple AI providers:
- Gemini (Live API + Chat)
- Ollama (local models)
- OpenRouter (cloud models)
- LM Studio (local OpenAI-compatible server)

API keys are encrypted at rest using :mod:`core.crypto`.
"""

import json
import logging
import sys
import time
from pathlib import Path

log = logging.getLogger(__name__)


def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR    = get_base_dir()
CONFIG_DIR  = BASE_DIR / "config"
CONFIG_FILE = CONFIG_DIR / "api_keys.json"

DEFAULT_CONFIG = {
    "gemini_api_key": "",
    "openrouter_api_key": "",
    "ollama_url": "http://localhost:11434",
    "lmstudio_url": "http://localhost:1234",
    "lmstudio_port": "1234",
    "lmstudio_auto_launch": True,
    "selected_provider": "gemini",
    "model": "",
    "model_gemini": "",
    "model_ollama": "",
    "model_openrouter": "",
    "model_lmstudio": "",
    "os_system": "windows",
    "audio_input_device": None,
    "audio_output_device": None,
    "audio_volume": 80,
    "voice_wrapper_enabled": False,
    "stt_engine": "gemini",
    "tts_engine": "gemini",
    "whisper_path": "",
    "whisper_model": "",
    "piper_path": "",
    "piper_model": "",
}

# Cache configuration
_config_cache = None
_cache_time = 0
CACHE_DURATION = 60  # Cache for 60 seconds


def ensure_config_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def config_exists() -> bool:
    return CONFIG_FILE.exists()


def save_config(data: dict) -> None:
    ensure_config_dir()

    current = {}
    if CONFIG_FILE.exists():
        try:
            current = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            current = {}

    from core.crypto import encrypt
    for key_field in ("gemini_api_key", "openrouter_api_key"):
        if key_field in data and data[key_field]:
            if not data[key_field].startswith("gAAAAA"):
                data[key_field] = encrypt(data[key_field])

    current.update(data)

    CONFIG_FILE.write_text(
        json.dumps(current, indent=2),
        encoding="utf-8"
    )
    
    # Clear cache after save
    global _config_cache, _cache_time
    _config_cache = None
    _cache_time = 0


def load_config() -> dict:
    global _config_cache, _cache_time
    
    current_time = time.time()
    if _config_cache and (current_time - _cache_time) < CACHE_DURATION:
        return _config_cache
    
    if not CONFIG_FILE.exists():
        _config_cache = dict(DEFAULT_CONFIG)
        _cache_time = current_time
        return _config_cache
        
    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        merged = dict(DEFAULT_CONFIG)
        merged.update(data)

        from core.crypto import decrypt
        for key_field in ("gemini_api_key", "openrouter_api_key"):
            if key_field in merged and merged[key_field]:
                try:
                    decrypted = decrypt(merged[key_field])
                    if decrypted:
                        merged[key_field] = decrypted
                except Exception:
                    pass

        _config_cache = merged
        _cache_time = current_time
        return merged
    except Exception as e:
        log.error("Failed to load config: %s", e)
        _config_cache = dict(DEFAULT_CONFIG)
        _cache_time = current_time
        return dict(DEFAULT_CONFIG)


def save_api_keys(
    gemini_api_key: str = "",
    openrouter_api_key: str = "",
    ollama_url: str = "http://localhost:11434",
    selected_provider: str = "gemini",
    model: str = "",
    os_system: str = "windows",
) -> None:
    save_config({
        "gemini_api_key": gemini_api_key.strip(),
        "openrouter_api_key": openrouter_api_key.strip(),
        "ollama_url": ollama_url.strip(),
        "selected_provider": selected_provider,
        "model": model,
        "os_system": os_system,
    })


def load_api_keys() -> dict:
    return load_config()


def get_gemini_key() -> str | None:
    cfg = load_config()
    key = cfg.get("gemini_api_key", "")
    return key if key else None


def get_openrouter_key() -> str | None:
    cfg = load_config()
    key = cfg.get("openrouter_api_key", "")
    return key if key else None


def get_ollama_url() -> str:
    cfg = load_config()
    return cfg.get("ollama_url", "http://localhost:11434")


def get_lmstudio_url() -> str:
    cfg = load_config()
    return cfg.get("lmstudio_url", "http://localhost:1234")


def get_selected_provider() -> str:
    cfg = load_config()
    return cfg.get("selected_provider", "gemini")


def get_model(provider: str = "") -> str:
    """Get the saved model, with per-provider fallback.

    If provider is given, reads model_{provider} key first, falling
    back to the old shared 'model' key, then empty string.
    """
    cfg = load_config()
    if provider:
        return cfg.get(f"model_{provider}", cfg.get("model", ""))
    return cfg.get("model", "")


def set_model(model: str, provider: str = "") -> None:
    """Save the model, optionally scoped to a provider.

    When provider is given, writes both model_{provider} AND 'model'
    so old fallback code continues to work.
    """
    data: dict[str, str] = {"model": model}
    if provider:
        data[f"model_{provider}"] = model
    save_config(data)


def get_os_system() -> str:
    cfg = load_config()
    return cfg.get("os_system", "windows")


def set_selected_provider(provider: str) -> None:
    save_config({"selected_provider": provider})


def is_configured() -> bool:
    """Check if the selected provider has the necessary config."""
    cfg = load_config()
    provider = cfg.get("selected_provider", "gemini")

    if provider == "gemini":
        key = cfg.get("gemini_api_key", "")
        return bool(key and len(key) > 15)

    elif provider == "ollama":
        url = cfg.get("ollama_url", "")
        return bool(url)

    elif provider == "openrouter":
        key = cfg.get("openrouter_api_key", "")
        return bool(key and len(key) > 8)

    elif provider == "lmstudio":
        url = cfg.get("lmstudio_url", "")
        return bool(url)

    return False
