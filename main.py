import logging
import sys
import threading
import asyncio
from pathlib import Path

from ui import JarvisUI
from memory.config_manager import save_config
from core.logging_config import setup_logging
from engine.factory import create_engine
from engine.events import engine_stop, engine_restart

logger = logging.getLogger(__name__)

"""MARK XL — Multi-Provider J.A.R.V.I.S.

Supports three AI providers:
- Gemini: Real-time audio with Live API (the original Mark 39 experience)
- Ollama: Local models via REST API
- OpenRouter: Cloud models via REST API

The engine auto-detects the configured provider and starts the appropriate mode.
Switching providers at runtime is supported via the UI.
"""

# ── Force UTF-8 console on Windows (prevents cp1252 emoji crashes) ──
if sys.platform == "win32":
    import io
    for _stream_name in ("stdout", "stderr"):
        _stream = getattr(sys, _stream_name)
        if hasattr(_stream, "buffer"):
            setattr(sys, _stream_name, io.TextIOWrapper(
                _stream.buffer, encoding="utf-8", errors="replace",
                line_buffering=_stream.line_buffering,
            ))

BASE_DIR = Path(__file__).resolve().parent

def _switch_provider(provider_name: str, ui: JarvisUI):
    """Switch provider at runtime — signals engine to stop and restart."""
    save_config({"selected_provider": provider_name})
    prov_name = {"gemini": "Gemini", "ollama": "Ollama", "openrouter": "OpenRouter", "lmstudio": "LM Studio"}.get(provider_name, provider_name)
    
    logger.info(f"Provider switch requested: {prov_name}")
    ui.write_log(f"SYS: Switching to {prov_name} provider...")
    engine_restart.set()
    engine_stop.set()


# ── Main ────────────────────────────────────────────────────────────

def main():
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    face_path = BASE_DIR / "face.png"
    if not face_path.exists():
        face_path = BASE_DIR / "face.jpg"
    if not face_path.exists():
        face_path = BASE_DIR / "core" / "face.png"
    if not face_path.exists():
        face_path = None
    ui = JarvisUI(face_path)

    # Connect provider switch callback
    ui.on_provider_changed = lambda p: _switch_provider(p, ui)

    def runner():
        ui.wait_for_api_key()
        
        # Initialize and load dynamic skills
        try:
            from services.skills.manager import SkillManager
            skill_manager = SkillManager(ui)
            skill_manager.scan_and_load()
            skill_manager.check_updates_background()
        except Exception as e:
            logger.exception("Error initializing Skills system")
            ui.write_log(f"SYS: Error al inicializar el sistema de habilidades: {e}")
            
        while True:
            engine_stop.clear()
            engine = create_engine(ui)
            try:
                async def run_engine():
                    try:
                        await engine.run()
                    finally:
                        if hasattr(engine, "provider") and hasattr(engine.provider, "close"):
                            await engine.provider.close()
                asyncio.run(run_engine())
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                break
            except Exception:
                # Handle asyncio proactor shutdown issues gracefully
                pass

            if not engine_restart.is_set():
                break

            engine_restart.clear()
            logger.info("Engine restarted with new provider.")
            ui.write_log("SYS: Engine restarted with new provider.")

    threading.Thread(target=runner, daemon=True).start()
    ui.root.mainloop()


if __name__ == "__main__":
    setup_logging()
    main()
