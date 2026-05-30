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


# ── Model discovery ────────────────────────────────────────────────────

def get_downloaded_models() -> list[dict]:
    """Scan LM Studio's model directories for downloaded models.

    Returns a list of dicts with 'id' and 'name' keys.
    """
    models: list[dict] = []
    system = platform.system()

    # LM Studio stores models in these locations
    model_dirs: list[Path] = []

    if system == "Windows":
        home = Path.home()
        model_dirs.append(home / ".lmstudio" / "models")
        model_dirs.append(home / ".cache" / "lm-studio" / "models")

        # Also check the app's data dir
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
        for item in d.iterdir():
            if item.is_dir():
                for f in item.iterdir():
                    # Look for .gguf files or subdirectories with model files
                    if f.suffix.lower() in (".gguf", ".bin", ".pt", ".pth", ".safetensors"):
                        model_id = f"{item.name}/{f.stem}"
                        if model_id not in seen:
                            seen.add(model_id)
                            models.append({"id": model_id, "name": f"{item.name} - {f.stem}"})
                    elif f.is_dir():
                        # HuggingFace-style: publisher/model-name
                        model_id = f"{item.name}/{f.name}"
                        if model_id not in seen:
                            seen.add(model_id)
                            models.append({"id": model_id, "name": f"{item.name}/{f.name}"})
            elif item.suffix.lower() in (".gguf",):
                # Single .gguf file directly in models dir
                model_id = item.stem
                if model_id not in seen:
                    seen.add(model_id)
                    models.append({"id": model_id, "name": item.stem})

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
        # Provide sensible defaults if nothing found
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
    except requests.RequestException:
        pass
    except Exception:
        pass
    return []


# ── Application lifecycle ──────────────────────────────────────────────

def launch_lmstudio() -> bool:
    """Launch LM Studio application.

    Returns True if the process was started successfully.
    """
    path = find_lmstudio_path()
    if not path:
        logger.error("[LM Studio] Cannot launch — installation not found.")
        return False

    try:
        system = platform.system()
        if system == "Windows":
            subprocess.Popen(
                [str(path)],
                creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
            )

        elif system == "Darwin":
            subprocess.Popen(["open", str(path.parent.parent)])
        else:
            subprocess.Popen([str(path)], start_new_session=True)

        logger.info(f"[LM Studio] Launched: {path}")
        return True

    except Exception as e:
        logger.error(f"[LM Studio] Failed to launch: {e}")
        return False


def quit_lmstudio() -> bool:
    """Quit LM Studio application gracefully.

    Returns True if the process was terminated.
    """
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.run(
                ["taskkill", "/f", "/im", "LM Studio.exe"],
                capture_output=True, timeout=5,
            )
        elif system == "Darwin":
            subprocess.run(
                ["pkill", "-x", "LM Studio"],
                capture_output=True, timeout=5,
            )
        else:
            subprocess.run(
                ["pkill", "-x", "lm-studio"],
                capture_output=True, timeout=5,
            )
        logger.info("[LM Studio] Quit signal sent.")
        return True
    except Exception as e:
        logger.error(f"[LM Studio] Failed to quit: {e}")
        return False


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
        result["error"] = "Connection refused"
    except requests.Timeout:
        result["error"] = "Timeout"
    except Exception as e:
        result["error"] = str(e)
    return result
