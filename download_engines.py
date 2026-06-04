import os
import sys
import zipfile
import tarfile
import urllib.request
import json
import subprocess
from pathlib import Path

# Force UTF-8 encoding on Windows to prevent UnicodeEncodeError
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Platform detection
IS_WINDOWS = sys.platform == "win32"
exec_suffix = ".exe" if IS_WINDOWS else ""

# Shared URLs
WHISPER_MODEL_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin"
PIPER_MODEL_ONNX_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_MX/claude/high/es_MX-claude-high.onnx"
PIPER_MODEL_JSON_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_MX/claude/high/es_MX-claude-high.onnx.json"

# Platform specific URLs and Archive paths
if IS_WINDOWS:
    WHISPER_ZIP_URL = "https://github.com/ggerganov/whisper.cpp/releases/download/v1.5.4/whisper-bin-x64.zip"
    PIPER_ZIP_URL = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_windows_amd64.zip"
    whisper_archive = Path("bin/whisper.zip")
    piper_archive = Path("bin/piper.zip")
else:
    # Linux (Ubuntu/Debian) and macOS
    WHISPER_ZIP_URL = "https://github.com/ggerganov/whisper.cpp/archive/refs/tags/v1.5.4.zip" # Source code
    PIPER_ZIP_URL = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_x86_64.tar.gz" # Prebuilt binary
    whisper_archive = Path("bin/whisper.zip")
    piper_archive = Path("bin/piper.tar.gz")

BASE_DIR = Path(__file__).resolve().parent
BIN_DIR = BASE_DIR / "bin"
WHISPER_DIR = BIN_DIR / "whisper"
PIPER_DIR = BIN_DIR / "piper"
CONFIG_FILE = BASE_DIR / "config" / "api_keys.json"

whisper_archive = BIN_DIR / whisper_archive.name
piper_archive = BIN_DIR / piper_archive.name

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

def extract_tar_gz(tar_path: Path, dest_dir: Path):
    """Extract a tar.gz archive to a destination directory."""
    print(f"[UNTAR] Extracting {tar_path.name} to {dest_dir}")
    dest_dir.mkdir(parents=True, exist_ok=True)
    try:
        with tarfile.open(tar_path, 'r:gz') as tar_ref:
            tar_ref.extractall(path=str(dest_dir))
        print("   [OK] Extraction complete.")
    except Exception as e:
        print(f"   [ERR] Extraction failed: {e}")
        raise

def compile_whisper(whisper_src_dir: Path) -> Path | None:
    """Compile Whisper.cpp source code using make command on Linux/macOS."""
    print(f"[COMPILE] Compiling whisper.cpp in {whisper_src_dir}...")
    try:
        # Run make command
        result = subprocess.run(
            ["make"],
            cwd=str(whisper_src_dir),
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"   [ERR] Compilation failed:\n{result.stderr}")
            return None
        print("   [OK] Compilation successful.")
        binary = whisper_src_dir / "main"
        if binary.exists():
            return binary
    except Exception as e:
        print(f"   [ERR] Compilation failed with exception: {e}")
    return None

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
    binary_name = f"main{exec_suffix}"
    if not locate_file(WHISPER_DIR, binary_name):
        print("\n--- [SETUP] WHISPER.CPP (LOCAL STT ENGINE) ---")
        download_file(WHISPER_ZIP_URL, whisper_archive)
        extract_zip(whisper_archive, WHISPER_DIR)
        # Cleanup ZIP
        if whisper_archive.exists():
            os.remove(whisper_archive)
            
        # Compile Whisper on non-Windows platforms
        if not IS_WINDOWS:
            src_dirs = [d for d in WHISPER_DIR.iterdir() if d.is_dir() and "whisper.cpp" in d.name]
            if src_dirs:
                compiled_binary = compile_whisper(src_dirs[0])
                if not compiled_binary:
                    print("\n[ERR] Could not compile Whisper.cpp. Please make sure build-essential is installed.")
                    sys.exit(1)
            else:
                print("\n[ERR] Whisper.cpp source folder not found after extraction.")
                sys.exit(1)
    else:
        print(f"\n[OK] Whisper.cpp already installed ({binary_name}).")

    whisper_model = WHISPER_DIR / "ggml-base.bin"
    if not whisper_model.exists():
        print("\n--- [MODEL] WHISPER.CPP SPANISH MODEL ---")
        download_file(WHISPER_MODEL_URL, whisper_model)
    else:
        print("[OK] Whisper ggml-base.bin model already exists.")

    # 2. Download and configure Piper
    piper_binary = f"piper{exec_suffix}"
    if not locate_file(PIPER_DIR, piper_binary):
        print("\n--- [SETUP] PIPER (LOCAL TTS ENGINE) ---")
        download_file(PIPER_ZIP_URL, piper_archive)
        if IS_WINDOWS:
            extract_zip(piper_archive, PIPER_DIR)
        else:
            extract_tar_gz(piper_archive, PIPER_DIR)
        # Cleanup archive
        if piper_archive.exists():
            os.remove(piper_archive)
    else:
        print(f"\n[OK] Piper already installed ({piper_binary}).")

    piper_model_onnx = PIPER_DIR / "es_MX-claude-high.onnx"
    piper_model_json = PIPER_DIR / "es_MX-claude-high.onnx.json"
    
    if not piper_model_onnx.exists():
        print("\n--- [MODEL] PIPER SPANISH VOICE MODEL (ONNX - HIGH QUALITY) ---")
        download_file(PIPER_MODEL_ONNX_URL, piper_model_onnx)
    else:
        print("[OK] Piper Spanish ONNX model already exists.")

    if not piper_model_json.exists():
        print("\n--- [CONFIG] PIPER VOICE CONFIGURATION (JSON) ---")
        download_file(PIPER_MODEL_JSON_URL, piper_model_json)
    else:
        print("[OK] Piper voice JSON config already exists.")

    # Locate executable files absolute paths
    whisper_exec = locate_file(WHISPER_DIR, binary_name)
    piper_exec = locate_file(PIPER_DIR, piper_binary)

    if not whisper_exec or not piper_exec:
        print("\n[ERR] Executables not found after installation.")
        sys.exit(1)

    # Set executable permissions on non-Windows platforms
    if not IS_WINDOWS:
        try:
            os.chmod(whisper_exec, 0o755)
            os.chmod(piper_exec, 0o755)
            print("[OK] Set executable permissions (+x).")
        except Exception as e:
            print(f"[WARN] Failed to set execution permissions: {e}")

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
