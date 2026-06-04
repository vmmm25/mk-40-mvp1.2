import logging
from typing import Any

from memory.config_manager import load_config, get_model
from providers import create_provider, ProviderConfig
from engine.live import JarvisLive, _load_system_prompt
from engine.chat import JarvisChat

logger = logging.getLogger(__name__)

def build_provider_config() -> ProviderConfig:
    """Build a ProviderConfig from the saved config, fully provider-aware."""
    cfg = load_config()
    selected = cfg.get("selected_provider", "gemini")

    api_key = ""
    base_url = ""

    if selected == "gemini":
        api_key = cfg.get("gemini_api_key", "")
    elif selected == "openrouter":
        api_key = cfg.get("openrouter_api_key", "")
    elif selected == "ollama":
        base_url = cfg.get("ollama_url", "http://localhost:11434")
    elif selected == "lmstudio":
        base_url = cfg.get("lmstudio_url", "http://localhost:1234")

    return ProviderConfig(
        api_key=api_key,
        base_url=base_url,
        model=get_model(selected),
        system_prompt=_load_system_prompt(),
        temperature=0.7,
        max_tokens=4096,
        os_system=cfg.get("os_system", "windows"),
        extra={
            "openrouter_api_key": cfg.get("openrouter_api_key", ""),
        },
    )

def create_engine(ui: Any):
    """Create the appropriate engine based on the saved provider config."""
    selected = load_config().get("selected_provider", "gemini")
    pconfig = build_provider_config()

    provider = create_provider(selected, pconfig)
    prov_name = {"gemini": "Gemini", "ollama": "Ollama", "openrouter": "OpenRouter", "lmstudio": "LM Studio"}.get(selected, selected)
    
    logger.info(f"Initializing Engine: {prov_name}")
    logger.info(f"Model Configuration: {pconfig.model}")
    
    if selected == "gemini" and getattr(provider, "supports_live_audio", False):
        logger.info("Mode: Live Audio (Real-time streaming)")
    else:
        logger.info("Mode: Text Chat (with optional Voice Wrapper)")
        
    ui.write_log(f"SYS: Starting with provider: {prov_name} (Model: {pconfig.model})")

    if selected == "gemini" and getattr(provider, "supports_live_audio", False):
        return JarvisLive(ui, provider)

    return JarvisChat(ui, provider)
