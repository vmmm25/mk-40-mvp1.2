"""MARK XL — LM Studio Control Module.

Discovers LM Studio installation, manages the application lifecycle,
reads downloaded models from disk, and checks server health.

NOTE: This module uses requests (synchronous) for server checks because
it is called from PyQt6 UI code which may not have an event loop running.
The actual provider (lmstudio_provider.py) uses aiohttp (async) for chat.

Usage:
    from lmstudio_control import (
        find_lmstudio_path,
        get_downloaded_models,
        launch_lmstudio,
        quit_lmstudio,
        is_server_running,
    )
"""
import os
import logging
import platform
import subprocess
import time
from pathlib import Path
from typing import Optional

import requests

from memory.config_manager import get_lmstudio_url

logger = logging.getLogger("lmstudio_control")


# ── Common LM Studio installation paths ───────────────────────────────

def _common_paths() -> list[Path]:
    """Return common LM Studio installation paths for the current OS."""
    system = platform.system()
    paths: list[Path] = []

    if system == "Windows":
        base = Path(os.environ.get("LOCALAPPDATA", ""))
        if base:
            paths.append(base / "Programs" / "LM Studio")
            paths.append(base / "LM Studio")
        # Also check %APPDATA%
        appdata = Path(os.environ.get("APPDATA", ""))
        if appdata:
            paths.append(appdata / "LM Studio")
        # Common install locations
        paths.append(Path("C:\\Program Files\\LM Studio"))
        paths.append(Path("C:\\Program Files (x86)\\LM Studio"))
        # User's home
        home = Path.home()
        paths.append(home / "AppData" / "Local" / "Programs" / "LM Studio")
        paths.append(home / "AppData" / "Local" / "LM Studio")

    elif system == "Darwin":
        paths.append(Path("/Applications/LM Studio.app"))
        paths.append(Path.home() / "Applications" / "LM Studio.app")

    else:  # Linux
        paths.append(Path("/usr/bin/lm-studio"))
        paths.append(Path("/usr/local/bin/lm-studio"))
        paths.append(Path.home() / ".lmstudio")

    return paths


def find_lmstudio_path() -> Optional[Path]:
    """Find the LM Studio executable path.

    Returns the path to the main executable, or None if not found.
    """
    system = platform.system()

    for p in _common_paths():
        if system == "Windows":
            # Check for LM Studio.exe in the directory
            exe = p / "LM Studio.exe"
            if exe.exists():
                return exe
            # Or directly in AppData\Local\LM Studio\
            exe2 = p / "LM Studio" / "LM Studio.exe"
            if exe2.exists():
                return exe2

        elif system == "Darwin":
            # macOS .app bundle
            bundle = p / "Contents" / "MacOS" / "LM Studio"
            if bundle.exists():
                return bundle
            if p.exists() and p.suffix == ".app":
                alt = p / "Contents" / "MacOS" / "LM Studio"
                if alt.exists():
                    return alt

        else:  # Linux
            if p.exists():
                if p.is_file() and os.access(p, os.X_OK):
                    return p
                # Check for lm-studio binary inside
                for name in ("lm-studio", "LM Studio", "lmstudio"):
                    candidate = p / name
                    if candidate.exists() and os.access(candidate, os.X_OK):
                        return candidate

    # Fallback: try `which` / `where`
    try:
        if system == "Windows":
            result = subprocess.run(
                ["where", "LM Studio"],
                capture_output=True, text=True, timeout=5,
            )
        else:
            result = subprocess.run(
                ["which", "lm-studio"],
                capture_output=True, text=True, timeout=5,
            )
        if result.returncode == 0 and result.stdout.strip():
            p = Path(result.stdout.strip())
            if p.exists():
                return p
    except Exception:
        pass

    return None


# ── LMS CLI path lookup and parsing helpers ────────────────────────────

def find_lms_cli_path() -> Optional[Path]:
    """Find the path of the lms CLI executable."""
    system = platform.system()
    binary_name = "lms.exe" if system == "Windows" else "lms"

    # 1. Check ~/.lmstudio/bin/lms
    home_lms = Path.home() / ".lmstudio" / "bin" / binary_name
    if home_lms.exists():
        return home_lms

    # 2. Check system PATH via where/which
    try:
        cmd = ["where", "lms"] if system == "Windows" else ["which", "lms"]
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=3
        )
        if result.returncode == 0 and result.stdout.strip():
            p = Path(result.stdout.strip().split("\n")[0].strip())
            if p.exists():
                return p
    except Exception:
        pass

    # 3. Check alternative common directories
    main_install_dir = find_lmstudio_path()
    if main_install_dir:
        parent_dir = main_install_dir.parent
        for root, dirs, files in os.walk(str(parent_dir)):
            if binary_name in files:
                return Path(root) / binary_name

    return None


def _parse_lms_ls(output: str) -> list[dict]:
    """Parse the output of 'lms ls' command.

    Example output:
    You have 12 models...
    LLM                                        PARAMS     ARCH          SIZE        DEVICE    
    deepseek-r1-distill-qwen-1.5b              1.5B       Qwen2         1.89 GB     Local     
    nvidia/nemotron-3-nano-4b (1 variant)      4.0B       nemotron_h    4.23 GB     Local     
    """
    import re
    models = []
    lines = output.strip().split("\n")
    in_llm_section = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect start of LLM section
        if line.startswith("LLM ") or re.match(r"^LLM\s+", line):
            in_llm_section = True
            continue

        if in_llm_section:
            # Detect end of LLM section
            if "EMBEDDING" in line or line.startswith("---"):
                in_llm_section = False
                break

            # Split line by 2 or more spaces
            parts = re.split(r'\s{2,}', line)
            if parts:
                model_key = parts[0].strip()
                if model_key in ("LLM", "PARAMS", "ARCH", "SIZE", "DEVICE"):
                    continue

                # Strip variant suffix: e.g. "nvidia/nemotron-3-nano-4b (1 variant)" -> "nvidia/nemotron-3-nano-4b"
                clean_key = re.sub(r'\s*\(\d+\s+variant\w*\)', '', model_key).strip()
                if clean_key:
                    name = clean_key
                    if "/" in clean_key:
                        parts_name = clean_key.split("/")
                        name = f"{parts_name[0]} - {parts_name[-1]}"
                    models.append({"id": clean_key, "name": name})

    return models


def _parse_lms_ps(output: str) -> list[dict]:
    """Parse the output of 'lms ps' command to find loaded models."""
    import re
    models = []
    lines = output.strip().split("\n")
    header_found = False

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if "IDENTIFIER" in line and "MODEL" in line:
            header_found = True
            continue
        if header_found:
            if "No models" in line or line.startswith("---"):
                break
            parts = re.split(r'\s{2,}', line)
            if parts:
                identifier = parts[0].strip()
                model_name = parts[1].strip() if len(parts) > 1 else identifier
                models.append({"id": identifier, "name": model_name})
    return models


# ── Model discovery ────────────────────────────────────────────────────

def get_downloaded_models() -> list[dict]:
    """Scan LM Studio's model directories or query lms CLI for downloaded models.

    Returns a list of dicts with 'id' and 'name' keys.
    """
    # 1. Try lms CLI first
    cli_path = find_lms_cli_path()
    if cli_path:
        try:
            logger.info("[LM Studio] Listing models via CLI 'lms ls'...")
            result = subprocess.run(
                [str(cli_path), "ls"],
                capture_output=True, text=True, timeout=10, encoding="utf-8"
            )
            if result.returncode == 0:
                parsed_models = _parse_lms_ls(result.stdout)
                if parsed_models:
                    logger.info(f"[LM Studio] Found {len(parsed_models)} models via CLI.")
                    return parsed_models
            else:
                logger.error(f"[LM Studio] CLI 'lms ls' failed: {result.stderr.strip()}")
        except Exception as e:
            logger.exception(f"[LM Studio] CLI 'lms ls' error: {e}")

    # 2. Fallback to manual directory scanning
    logger.info("[LM Studio] Falling back to manual directory scanning for models...")
    models: list[dict] = []
    system = platform.system()
    model_dirs: list[Path] = []

    if system == "Windows":
        home = Path.home()
        model_dirs.append(home / ".lmstudio" / "models")
        model_dirs.append(home / ".cache" / "lm-studio" / "models")
        localappdata = Path(os.environ.get("LOCALAPPDATA", ""))
        if localappdata:
            model_dirs.append(localappdata / "LM Studio" / "models")
    elif system == "Darwin":
        home = Path.home()
        model_dirs.append(home / ".lmstudio" / "models")
        model_dirs.append(home / "Library" / "Application Support" / "LM Studio" / "models")
    else:  # Linux
        home = Path.home()
        model_dirs.append(home / ".lmstudio" / "models")
        model_dirs.append(home / ".cache" / "lm-studio" / "models")

    seen: set[str] = set()
    for d in model_dirs:
        if not d.exists():
            continue
        try:
            for item in d.iterdir():
                if item.is_dir():
                    for f in item.iterdir():
                        if f.suffix.lower() in (".gguf", ".bin", ".pt", ".pth", ".safetensors"):
                            model_id = f"{item.name}/{f.stem}"
                            if model_id not in seen:
                                seen.add(model_id)
                                models.append({"id": model_id, "name": f"{item.name} - {f.stem}"})
                        elif f.is_dir():
                            model_id = f"{item.name}/{f.name}"
                            if model_id not in seen:
                                seen.add(model_id)
                                models.append({"id": model_id, "name": f"{item.name}/{f.name}"})
                elif item.suffix.lower() in (".gguf",):
                    model_id = item.stem
                    if model_id not in seen:
                        seen.add(model_id)
                        models.append({"id": model_id, "name": item.stem})
        except Exception as e:
            logger.error(f"[LM Studio] Error scanning directory {d}: {e}")

    # Also query API for loaded models if server is running
    try:
        api_models = _fetch_api_loaded_models()
        for m in api_models:
            mid = m.get("id", "")
            if mid and mid not in seen:
                seen.add(mid)
                models.append(m)
    except Exception:
        pass

    if not models:
        models = [
            {"id": "local-model", "name": "Local Model (loaded in LM Studio)"},
        ]

    return models


def _fetch_api_loaded_models() -> list[dict]:
    """Fetch models currently loaded/available from LM Studio API."""
    base_url = get_lmstudio_url()
    try:
        resp = requests.get(
            f"{base_url}/v1/models",
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            return [
                {"id": m["id"], "name": m.get("id", "Unknown")}
                for m in data.get("data", [])
            ]
    except Exception:
        pass
    return []


def load_model(model_id: str) -> tuple[bool, str]:
    """Load a model into LM Studio using CLI or REST API."""
    # 1. Try lms CLI load first
    cli_path = find_lms_cli_path()
    if cli_path:
        try:
            logger.info(f"[LM Studio] Loading model '{model_id}' via CLI...")
            result = subprocess.run(
                [str(cli_path), "load", model_id, "--yes"],
                capture_output=True, text=True, timeout=60, encoding="utf-8"
            )
            if result.returncode == 0:
                return True, f"Modelo '{model_id}' cargado correctamente mediante CLI."
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                logger.error(f"[LM Studio] CLI model load failed: {error_msg}")
        except subprocess.TimeoutExpired:
            logger.error(f"[LM Studio] CLI model load timed out for '{model_id}'")
            return False, "Error: Tiempo de espera agotado al cargar el modelo."
        except Exception as e:
            logger.exception(f"[LM Studio] CLI model load error: {e}")

    # 2. Fallback to HTTP REST API
    base_url = get_lmstudio_url()
    try:
        logger.info(f"[LM Studio] Loading model '{model_id}' via REST API fallback...")
        resp = requests.post(
            f"{base_url}/api/v1/models/load",
            json={"model": model_id},
            timeout=60,
        )
        if resp.status_code == 200:
            return True, f"Modelo '{model_id}' cargado correctamente (API)."
        else:
            return False, f"Error HTTP {resp.status_code}: {resp.text}"
    except requests.ConnectionError:
        return False, "Error: LM Studio no está ejecutándose o no es accesible."
    except requests.Timeout:
        return False, "Error: Tiempo de espera agotado al cargar el modelo."
    except Exception as e:
        return False, f"Error inesperado: {str(e)}"


def unload_model(model_id: str) -> tuple[bool, str]:
    """Unload a model from LM Studio using CLI or REST API."""
    # 1. Try lms CLI unload first
    cli_path = find_lms_cli_path()
    if cli_path:
        try:
            logger.info(f"[LM Studio] Unloading model '{model_id}' via CLI...")
            result = subprocess.run(
                [str(cli_path), "unload", model_id],
                capture_output=True, text=True, timeout=15, encoding="utf-8"
            )
            if result.returncode == 0:
                return True, f"Modelo '{model_id}' descargado de memoria mediante CLI."
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                logger.error(f"[LM Studio] CLI model unload failed: {error_msg}")
        except subprocess.TimeoutExpired:
            return False, "Error: Tiempo de espera agotado al descargar el modelo."
        except Exception as e:
            logger.exception(f"[LM Studio] CLI model unload error: {e}")

    # 2. Fallback to HTTP REST API
    base_url = get_lmstudio_url()
    try:
        logger.info(f"[LM Studio] Unloading model '{model_id}' via REST API fallback...")
        resp = requests.post(
            f"{base_url}/api/v1/models/unload",
            json={"model": model_id},
            timeout=10,
        )
        if resp.status_code == 200:
            return True, f"Modelo '{model_id}' descargado de memoria (API)."
        else:
            return False, f"Error HTTP {resp.status_code}: {resp.text}"
    except requests.ConnectionError:
        return False, "Error: LM Studio no está ejecutándose o no es accesible."
    except requests.Timeout:
        return False, "Error: Tiempo de espera agotado."
    except Exception as e:
        return False, f"Error inesperado: {str(e)}"


# ── Application lifecycle ──────────────────────────────────────────────

def launch_lmstudio() -> bool:
    """Launch LM Studio local server and optionally the application GUI.

    Returns True if the server started successfully.
    """
    cli_path = find_lms_cli_path()
    server_success = False

    if cli_path:
        try:
            from urllib.parse import urlparse
            url = get_lmstudio_url()
            parsed = urlparse(url)
            port = parsed.port or 1234
        except Exception:
            port = 1234

        try:
            logger.info(f"[LM Studio] Starting server via CLI on port {port}...")
            result = subprocess.run(
                [str(cli_path), "server", "start", "--port", str(port)],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                logger.info(f"[LM Studio] Server started successfully via CLI: {result.stdout.strip()}")
                server_success = True
            else:
                logger.error(f"[LM Studio] CLI server start failed: {result.stderr.strip()}")
        except Exception as e:
            logger.exception(f"[LM Studio] Failed to start server via CLI: {e}")

    # Also launch GUI if found
    gui_path = find_lmstudio_path()
    if gui_path:
        try:
            logger.info(f"[LM Studio] Launching GUI: {gui_path}...")
            system = platform.system()
            if system == "Windows":
                subprocess.Popen(
                    [str(gui_path)],
                    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                )
            elif system == "Darwin":
                subprocess.Popen(["open", str(gui_path.parent.parent)])
            else:
                subprocess.Popen([str(gui_path)], start_new_session=True)
            if not cli_path:
                server_success = True
        except Exception as e:
            logger.error(f"[LM Studio] Failed to launch GUI: {e}")

    return server_success or is_server_running()


def quit_lmstudio() -> bool:
    """Quit LM Studio server and application.

    Returns True if the process was terminated.
    """
    cli_path = find_lms_cli_path()
    cli_success = False

    if cli_path:
        try:
            logger.info("[LM Studio] Stopping server via CLI...")
            result = subprocess.run(
                [str(cli_path), "server", "stop"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                logger.info("[LM Studio] Server stopped via CLI.")
                cli_success = True
            else:
                logger.error(f"[LM Studio] CLI server stop failed: {result.stderr.strip()}")
        except Exception as e:
            logger.exception(f"[LM Studio] Failed to stop server via CLI: {e}")

    # Also terminate the GUI processes to be thorough
    gui_success = False
    system = platform.system()
    try:
        if system == "Windows":
            result = subprocess.run(
                ["taskkill", "/f", "/im", "LM Studio.exe"],
                capture_output=True, timeout=5,
            )
            gui_success = (result.returncode == 0)
        elif system == "Darwin":
            result = subprocess.run(
                ["pkill", "-x", "LM Studio"],
                capture_output=True, timeout=5,
            )
            gui_success = (result.returncode == 0)
        else:
            result = subprocess.run(
                ["pkill", "-x", "lm-studio"],
                capture_output=True, timeout=5,
            )
            gui_success = (result.returncode == 0)
        logger.info("[LM Studio] GUI process terminate signal sent.")
    except Exception as e:
        logger.error(f"[LM Studio] Failed to quit GUI: {e}")

    return cli_success or gui_success


# ── Server health checks ───────────────────────────────────────────────

def is_server_running() -> bool:
    """Check if the LM Studio inference server is running and responsive."""
    base_url = get_lmstudio_url()
    try:
        resp = requests.get(f"{base_url}/v1/models", timeout=5)
        return resp.status_code == 200
    except requests.RequestException:
        return False


def wait_for_server(timeout: float = 30.0) -> bool:
    """Wait for the LM Studio server to become responsive.

    Polls every second until timeout. Returns True if server responds.
    """
    start = time.time()
    while time.time() - start < timeout:
        if is_server_running():
            logger.info(f"[LM Studio] Server ready after {time.time() - start:.1f}s")
            return True
        time.sleep(1)
    logger.warning(f"[LM Studio] Server not ready after {timeout}s")
    return False


def get_server_status() -> dict:
    """Get detailed LM Studio server status.

    Returns a dict with keys: running (bool), models (list), error (str).
    """
    result: dict = {"running": False, "models": [], "error": ""}
    base_url = get_lmstudio_url()
    try:
        resp = requests.get(f"{base_url}/v1/models", timeout=5)
        if resp.status_code == 200:
            result["running"] = True
            data = resp.json()
            result["models"] = [
                {"id": m["id"], "name": m.get("id", "Unknown")}
                for m in data.get("data", [])
            ]
        else:
            result["error"] = f"HTTP {resp.status_code}"
    except requests.ConnectionError:
        # Fallback to check via CLI status if connection error occurs
        cli_path = find_lms_cli_path()
        if cli_path:
            try:
                res = subprocess.run([str(cli_path), "status"], capture_output=True, text=True, timeout=5)
                if res.returncode == 0 and "Server: ON" in res.stdout:
                    result["running"] = True
                    # Let's list loaded models using lms ps
                    ps_res = subprocess.run([str(cli_path), "ps"], capture_output=True, text=True, timeout=5)
                    if ps_res.returncode == 0:
                        result["models"] = _parse_lms_ps(ps_res.stdout)
                    return result
            except Exception:
                pass
        result["error"] = "Connection refused"
    except requests.Timeout:
        result["error"] = "Timeout"
    except Exception as e:
        result["error"] = str(e)
    return result

