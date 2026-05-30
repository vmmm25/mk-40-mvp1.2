from PyQt6.QtGui import QColor

class Theme:
    # ── Core backgrounds ────────────────────────────────────────────────
    BG        = "#020408"   # Black-void background
    PANEL     = "#07090f"   # Dark panel
    PANEL2    = "#0a0c14"   # Slightly lighter panel
    DARK      = "#04060b"   # Deepest dark (header/footer)

    # ── Borders ─────────────────────────────────────────────────────────
    BORDER    = "#1a0a04"   # Subtle dark-red border
    BORDER_B  = "#ff3c0055" # Glowing red border (semi-transparent)
    BORDER_A  = "#2a1008"   # Mid-tone border

    # ── Primary accent — Iron Man Orange-Red ────────────────────────────
    PRI       = "#ff5500"   # Arc reactor orange
    PRI_DIM   = "#7a2800"   # Dimmed orange
    PRI_GHO   = "#1a0800"   # Ghost orange (hover background)

    # ── Secondary accents ───────────────────────────────────────────────
    ACC       = "#ff8c00"   # Gold-orange (secondary)
    ACC2      = "#cc3300"   # Deep red accent

    # ── Status colors ───────────────────────────────────────────────────
    GREEN     = "#00ff88"   # Neon green (online / active)
    GREEN_D   = "#007744"   # Dark green
    RED       = "#ff0040"   # Alarm red
    MUTED_C   = "#441122"   # Muted/dimmed red

    # ── Text ─────────────────────────────────────────────────────────────
    TEXT      = "#f0e0d0"   # Warm off-white text
    TEXT_DIM  = "#7a5040"   # Dimmed text
    TEXT_MED  = "#c8a090"   # Medium text
    WHITE     = "#ffffff"

    # ── Misc ─────────────────────────────────────────────────────────────
    BAR_BG    = "#0f0604"   # Progress bar background


def qcol(h: str, a: int = 255) -> QColor:
    c = QColor(h)
    c.setAlpha(a)
    return c


PROVIDER_COLORS = {
    "gemini":     {"primary": "#4db8ff", "bg": "#001833", "name": "Gemini"},
    "ollama":     {"primary": "#e0e0e0", "bg": "#111111", "name": "Ollama"},
    "openrouter": {"primary": "#00e5a0", "bg": "#00221a", "name": "OpenRouter"},
    "lmstudio":   {"primary": "#ff8c00", "bg": "#1a0e00", "name": "LM Studio"},
}


def get_openrouter_color(model: str) -> str:
    """Return a distinctive color based on the selected OpenRouter model family."""
    m = model.lower()
    if "llama" in m or "meta" in m:
        return "#4db8ff"
    if "gemini" in m or "google" in m or "gemma" in m:
        return "#4285f4"
    if "gpt" in m or "openai" in m:
        return "#10a37f"
    if "deepseek" in m:
        return "#ff6b35"
    if "qwen" in m or "alibaba" in m:
        return "#ff4500"
    if "mistral" in m:
        return "#ff7700"
    if "claude" in m or "anthropic" in m:
        return "#cc785c"
    if "nvidia" in m or "nemotron" in m:
        return "#76b900"
    if "moonshot" in m or "kimi" in m:
        return "#7b68ee"
    if "liquid" in m:
        return "#00bcd4"
    return "#ff5500"   # Default: arc reactor orange
