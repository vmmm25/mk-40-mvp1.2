#!/usr/bin/env python3
"""MARK XL — Cross-platform bootstrap installer.

Verifies and installs all required and optional dependencies.
Run once after cloning or when switching branches.

Usage:
    python scripts/bootstrap.py          # full install
    python scripts/bootstrap.py --check  # dry-run: report what's missing
    python scripts/bootstrap.py --venv   # create venv first then install
"""

import argparse
import importlib.util
import os
import platform
import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
REQUIREMENTS = BASE_DIR / "requirements.txt"
REQUIREMENTS_DEV = BASE_DIR / "requirements-dev.txt"

PIP_INSTALL = [sys.executable, "-m", "pip", "install", "--upgrade"]

# ── Dependency map: module → pip package name ─────────────────────────────

CORE_DEPS: dict[str, str] = {
    "PyQt6": "PyQt6>=6.6.0",
    "sounddevice": "sounddevice>=0.4.6",
    "numpy": "numpy>=1.26.0",
}

OPTIONAL_DEPS: dict[str, str] = {
    "edge_tts": "edge-tts>=6.0.0",
    "kokoro": "kokoro>=0.9",
    "miniaudio": "miniaudio>=2.0.0",
    "chromadb": "chromadb>=0.5.0",
    "sentence_transformers": "sentence-transformers>=2.2.0",
    "cryptography": "cryptography>=42.0.0",
    "playwright": "playwright>=1.40.0",
}

EXTRA_NOTES: dict[str, str] = {
    "edge_tts": "EdgeTTS — Microsoft speech synthesis (internet required)",
    "kokoro": "Kokoro — offline neural TTS (~330 MB model download)",
    "miniaudio": "miniaudio — audio decoding for EdgeTTS/ElevenLabs",
    "chromadb": "ChromaDB — RAG vector store",
    "sentence_transformers": "sentence-transformers — embeddings for RAG",
    "cryptography": "cryptography — Fernet API key encryption at rest",
    "playwright": "Playwright — browser automation tools",
}


# ── Utilities ─────────────────────────────────────────────────────────────


def _green(t: str) -> str:
    return f"\033[92m{t}\033[0m" if sys.stdout.isatty() else t


def _yellow(t: str) -> str:
    return f"\033[93m{t}\033[0m" if sys.stdout.isatty() else t


def _red(t: str) -> str:
    return f"\033[91m{t}\033[0m" if sys.stdout.isatty() else t


def _cyan(t: str) -> str:
    return f"\033[96m{t}\033[0m" if sys.stdout.isatty() else t


def _check_module(name: str) -> bool:
    """Return True if a module is importable."""
    return importlib.util.find_spec(name) is not None


def _run(cmd: list[str], desc: str = "") -> bool:
    """Run a command, print status, return success."""
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"  {_green('✓')} {desc}")
        return True
    except subprocess.CalledProcessError as e:
        msg = e.stderr.decode(errors="replace").strip()[:200] if e.stderr else str(e)
        print(f"  {_red('✗')} {desc}: {msg}")
        return False


# ── Steps ─────────────────────────────────────────────────────────────────


def step_venv():
    """Create .venv if it doesn't exist."""
    venv_path = BASE_DIR / ".venv"
    if venv_path.exists():
        print(f"  {_green('✓')} Virtual environment already exists at {venv_path}")
        return

    print(f"  {_yellow('…')} Creating virtual environment…")
    ok = _run(
        [sys.executable, "-m", "venv", str(venv_path)],
        "python -m venv .venv",
    )
    if ok:
        # Re-execute bootstrap with venv Python
        venv_python = venv_path / "Scripts" / "python.exe" if platform.system() == "Windows" else venv_path / "bin" / "python"
        if venv_python.exists():
            print(f"  {_green('✓')} Re-running bootstrap inside .venv…")
            subprocess.run([str(venv_python), __file__] + sys.argv[1:])
            sys.exit(0)


def step_upgrade_pip():
    """Upgrade pip to latest."""
    _run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        "pip upgrade",
    )


def step_core_requirements():
    """Install core requirements.txt."""
    if REQUIREMENTS.exists():
        _run(
            PIP_INSTALL + ["-r", str(REQUIREMENTS)],
            "pip install -r requirements.txt",
        )


def step_dev_requirements():
    """Install dev requirements."""
    if REQUIREMENTS_DEV.exists():
        _run(
            PIP_INSTALL + ["-r", str(REQUIREMENTS_DEV)],
            "pip install -r requirements-dev.txt",
        )


def step_verify_core():
    """Verify core dependencies are importable."""
    all_ok = True
    for mod, pkg in CORE_DEPS.items():
        ok = _check_module(mod)
        if ok:
            print(f"  {_green('✓')} {mod}")
        else:
            print(f"  {_red('✗')} {mod} — run: pip install {pkg}")
            all_ok = False
    return all_ok


def step_optional_deps(install: bool = False):
    """Check optional deps and optionally install them."""
    missing: list[str] = []
    for mod, pkg in OPTIONAL_DEPS.items():
        ok = _check_module(mod)
        note = EXTRA_NOTES.get(mod, "")
        label = f"{mod} ({note})" if note else mod
        if ok:
            print(f"  {_green('✓')} {label}")
        else:
            print(f"  {_yellow('○')} {label} — NOT INSTALLED")
            missing.append(pkg)

    if install and missing:
        print(f"\n  {_cyan('→')} Installing {len(missing)} optional packages…")
        # Install one by one for better error reporting
        for pkg in missing:
            _run(PIP_INSTALL + [pkg], f"pip install {pkg.split('>=')[0]}")


def step_playwright():
    """Install Playwright browsers if playwright is available."""
    if _check_module("playwright"):
        _run(
            [sys.executable, "-m", "playwright", "install", "--with-deps"],
            "playwright install",
        )


def step_edgetts_audio():
    """Install Windows Media Feature for EdgeTTS on Windows."""
    if platform.system() == "Windows":
        # Check if WebView2 / Media Foundation is available
        try:
            import edge_tts  # noqa: F401
            # EdgeTTS works — skip
        except ImportError:
            pass
        except Exception:
            # Media Foundation may be missing
            print(f"  {_yellow('○')} EdgeTTS may need Windows Media Feature — see:")
            print(f"     https://learn.microsoft.com/en-us/windows/win32/medfound/media-foundation-programming-guide")


# ── Main ──────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="MARK XL bootstrap installer")
    parser.add_argument("--check", action="store_true", help="Dry-run: report what's missing without installing")
    parser.add_argument("--venv", action="store_true", help="Create .venv first and re-run inside it")
    args = parser.parse_args()

    print()
    print(_cyan("╔══════════════════════════════════════╗"))
    print(_cyan("║   MARK XL — Bootstrap Installer     ║"))
    print(_cyan("╚══════════════════════════════════════╝"))
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  Platform: {platform.system()} {platform.release()}")
    print(f"  Path: {BASE_DIR}")
    print()

    # ── Phase 0: venv ──
    if args.venv:
        step_venv()
    print()

    # ── Phase 1: pip & core ──
    print(_cyan("── Phase 1: Core dependencies ──"))
    if not args.check:
        step_upgrade_pip()
        step_core_requirements()
    core_ok = step_verify_core()
    if not core_ok and not args.check:
        print(f"\n  {_red('ERROR: Core dependencies missing. Run without --check to auto-install.')}")
        sys.exit(1)
    print()

    # ── Phase 2: Optional ──
    print(_cyan("── Phase 2: Optional dependencies ──"))
    step_optional_deps(install=not args.check)
    print()

    # ── Phase 3: Dev ──
    if not args.check:
        print(_cyan("── Phase 3: Dev dependencies ──"))
        step_dev_requirements()
        print()

    # ── Phase 4: Post-install ──
    if not args.check:
        print(_cyan("── Phase 4: Post-install ──"))
        step_playwright()
        step_edgetts_audio()
        print()

    # ── Summary ──
    print(_green("── Bootstrap complete ──"))
    print(f"  Run 'python main.py' to start J.A.R.V.I.S.")
    print()


if __name__ == "__main__":
    main()
