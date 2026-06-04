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

def check_and_autostart_lmstudio(ui: Any):
    """Check if LM Studio is selected, and automatically start the server and load the model if offline."""
    try:
        cfg = load_config()
        selected = cfg.get("selected_provider", "gemini")
        if selected != "lmstudio":
            return
            
        from lmstudio_control import is_server_running, launch_lmstudio, wait_for_server, load_model, get_server_status
        
        # 1. Start server if offline
        if not is_server_running():
            logger.info("[LM Studio] Auto-start triggered. Server is offline.")
            ui.write_log("SYS: LM Studio offline. Iniciando servidor mediante CLI...")
            success = launch_lmstudio()
            if success:
                logger.info("[LM Studio] Server started. Waiting for response...")
                wait_for_server(timeout=15.0)
            else:
                logger.error("[LM Studio] Auto-start server failed.")
                ui.write_log("SYS: Error al iniciar el servidor de LM Studio.")
                return

        # 2. Check and load the configured model
        if is_server_running():
            configured_model = get_model("lmstudio")
            if not configured_model or configured_model == "local-model":
                # Check if at least one model is loaded in memory
                status = get_server_status()
                if not status.get("models"):
                    logger.warning("[LM Studio] Server is running but no model is loaded.")
                    ui.write_log("SYS: Servidor LM Studio activo, pero no hay ningún modelo cargado.")
                return
                
            status = get_server_status()
            loaded_ids = [m["id"] for m in status.get("models", [])]
            if configured_model not in loaded_ids:
                logger.info(f"[LM Studio] Auto-loading model: {configured_model}")
                ui.write_log(f"SYS: Cargando modelo en memoria: {configured_model}...")
                success, msg = load_model(configured_model)
                if success:
                    logger.info(f"[LM Studio] Model auto-loaded: {msg}")
                    ui.write_log(f"SYS: Modelo {configured_model} cargado y activo.")
                else:
                    logger.error(f"[LM Studio] Model auto-load failed: {msg}")
                    ui.write_log(f"SYS: Error al cargar modelo: {msg}")
            else:
                logger.info(f"[LM Studio] Configured model is already loaded: {configured_model}")
                ui.write_log(f"SYS: Modelo {configured_model} ya está cargado y listo.")
    except Exception as e:
        logger.exception(f"[LM Studio] Error in autostart: {e}")
        ui.write_log(f"SYS: Error en auto-inicio de LM Studio: {e}")


def create_engine(ui: Any):
    """Create the appropriate engine based on the saved provider config."""
    selected = load_config().get("selected_provider", "gemini")
    
    if selected == "lmstudio":
        # Run autostart checks
        check_and_autostart_lmstudio(ui)

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
