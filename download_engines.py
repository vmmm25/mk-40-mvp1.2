import os
import sys
import zipfile
import urllib.request
import json
from pathlib import Path

# Force UTF-8 encoding on Windows to prevent UnicodeEncodeError
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# URLs for stable Windows engines and Spanish models
WHISPER_ZIP_URL = "https://github.com/ggerganov/whisper.cpp/releases/download/v1.5.4/whisper-bin-x64.zip"
WHISPER_MODEL_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin"

PIPER_ZIP_URL = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_windows_amd64.zip"
PIPER_MODEL_ONNX_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx"
PIPER_MODEL_JSON_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx.json"

BASE_DIR = Path(__file__).resolve().parent
BIN_DIR = BASE_DIR / "bin"
WHISPER_DIR = BIN_DIR / "whisper"
PIPER_DIR = BIN_DIR / "piper"
CONFIG_FILE = BASE_DIR / "config" / "api_keys.json"

def download_file(url: str, dest_path: Path):
    """Download a file with a tactical progress bar."""
    print(f"[DOWNLOAD] {url}")
    print(f"[PATH]     {dest_path}")
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    def progress_hook(count, block_size, total_size):
        if total_size <= 0:
            return
        percent = int(count * block_size * 100 / total_size)
        percent = min(100, percent)
        downloaded = count * block_size / (1024 * 1024)
        total_mb = total_size / (1024 * 1024)
        sys.stdout.write(f"\r   [PROG] [{'#' * (percent // 5)}{'.' * (20 - percent // 5)}] {percent}% ({downloaded:.1f}/{total_mb:.1f} MB)")
        sys.stdout.flush()

    try:
        urllib.request.urlretrieve(url, str(dest_path), reporthook=progress_hook)
        print("\n   [OK] Download complete.")
    except Exception as e:
        print(f"\n   [ERR] Download failed: {e}")
        raise

def extract_zip(zip_path: Path, dest_dir: Path):
    """Extract a ZIP archive to a destination directory."""
    print(f"[UNZIP] Extracting {zip_path.name} to {dest_dir}")
    dest_dir.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(str(dest_dir))
        print("   [OK] Extraction complete.")
    except Exception as e:
        print(f"   [ERR] Extraction failed: {e}")
        raise

def locate_file(dir_path: Path, filename: str) -> Path | None:
    """Recursively search for a file in a directory and return its path."""
    for path in dir_path.rglob(filename):
        if path.is_file():
            return path
    return None

def main():
    print("=======================================================")
    print("      JARVIS VOICES INSTALLER - MARK 40 LOCAL")
    print("=======================================================")
    
    # Create main folders
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Download and configure Whisper.cpp
    whisper_zip = BIN_DIR / "whisper.zip"
    if not locate_file(WHISPER_DIR, "main.exe"):
        print("\n--- [SETUP] WHISPER.CPP (LOCAL STT ENGINE) ---")
        download_file(WHISPER_ZIP_URL, whisper_zip)
        extract_zip(whisper_zip, WHISPER_DIR)
        # Cleanup ZIP
        if whisper_zip.exists():
            os.remove(whisper_zip)
    else:
        print("\n[OK] Whisper.cpp already installed.")

    whisper_model = WHISPER_DIR / "ggml-base.bin"
    if not whisper_model.exists():
        print("\n--- [MODEL] WHISPER.CPP SPANISH MODEL ---")
        download_file(WHISPER_MODEL_URL, whisper_model)
    else:
        print("[OK] Whisper ggml-base.bin model already exists.")

    # 2. Download and configure Piper
    piper_zip = BIN_DIR / "piper.zip"
    if not locate_file(PIPER_DIR, "piper.exe"):
        print("\n--- [SETUP] PIPER (LOCAL TTS ENGINE) ---")
        download_file(PIPER_ZIP_URL, piper_zip)
        extract_zip(piper_zip, PIPER_DIR)
        # Cleanup ZIP
        if piper_zip.exists():
            os.remove(piper_zip)
    else:
        print("\n[OK] Piper already installed.")

    piper_model_onnx = PIPER_DIR / "es_ES-sharvard-medium.onnx"
    piper_model_json = PIPER_DIR / "es_ES-sharvard-medium.onnx.json"
    
    if not piper_model_onnx.exists():
        print("\n--- [MODEL] PIPER SPANISH VOICE MODEL (ONNX) ---")
        download_file(PIPER_MODEL_ONNX_URL, piper_model_onnx)
    else:
        print("[OK] Piper Spanish ONNX model already exists.")

    if not piper_model_json.exists():
        print("\n--- [CONFIG] PIPER VOICE CONFIGURATION (JSON) ---")
        download_file(PIPER_MODEL_JSON_URL, piper_model_json)
    else:
        print("[OK] Piper voice JSON config already exists.")

    # Locate executable files absolute paths
    whisper_exec = locate_file(WHISPER_DIR, "main.exe")
    piper_exec = locate_file(PIPER_DIR, "piper.exe")

    if not whisper_exec or not piper_exec:
        print("\n[ERR] Executables not found after installation.")
        sys.exit(1)

    print("\n--- [CONFIG] SAVING api_keys.json PATHS ---")
    
    # Read existing config
    config_data = {}
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except Exception:
            config_data = {}

    # Update config values
    config_data["whisper_path"] = str(whisper_exec.resolve())
    config_data["whisper_model"] = str(whisper_model.resolve())
    config_data["piper_path"] = str(piper_exec.resolve())
    config_data["piper_model"] = str(piper_model_onnx.resolve())
    
    # Enable voice options by default
    config_data["voice_wrapper_enabled"] = True
    config_data["stt_engine"] = "whisper"
    config_data["tts_engine"] = "piper"

    # Write config
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)

    print(f"[OK] Configuration saved in: {CONFIG_FILE.resolve()}")
    print("\n=======================================================")
    print("  [SUCCESS] LOCAL AUDIO ENGINES INSTALLED SUCCESSFULLY ")
    print("=======================================================")
    print(f"Whisper Exec: {whisper_exec.resolve()}")
    print(f"Whisper Mod:  {whisper_model.resolve()}")
    print(f"Piper Exec:   {piper_exec.resolve()}")
    print(f"Piper Mod:    {piper_model_onnx.resolve()}")
    print("=======================================================")

if __name__ == "__main__":
    main()
