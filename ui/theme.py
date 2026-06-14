from PyQt6.QtGui import QColor

class Theme:
    # ── Core backgrounds ────────────────────────────────────────────────
    BG        = "#1e1e1e"   # macOS Dark Mode background
    PANEL     = "#252526"   # Dark panel
    PANEL2    = "#2d2d30"   # Slightly lighter panel
    DARK      = "#181818"   # Deepest dark (header/footer)

    # ── Borders ─────────────────────────────────────────────────────────
    BORDER    = "#3e3e42"   # Subtle border
    BORDER_B  = "#007acc55" # Glowing border (semi-transparent)
    BORDER_A  = "#454545"   # Mid-tone border

    # ── Primary accent (Dynamic) ─────────────────────────────────────────
    PRI       = "#007acc"   # Default macOS Blue
    PRI_DIM   = "#005a9e"   # Dimmed primary
    PRI_GHO   = "#003355"   # Ghost primary (hover background)

    # ── Secondary accents ───────────────────────────────────────────────
    ACC       = "#ff8c00"   # Gold-orange
    ACC2      = "#cc3300"   # Deep red accent

    # ── Status colors ───────────────────────────────────────────────────
    GREEN     = "#00c853"   # macOS/Neon green
    GREEN_D   = "#007744"   # Dark green
    RED       = "#ff3b30"   # macOS red
    MUTED_C   = "#441122"   # Muted red

    # ── Text ─────────────────────────────────────────────────────────────
    TEXT      = "#ffffff"   # White text
    TEXT_DIM  = "#a0a0a5"   # Dimmed text
    TEXT_MED  = "#cccccc"   # Medium text
    WHITE     = "#ffffff"

    # ── Misc ─────────────────────────────────────────────────────────────
    BAR_BG    = "#1a1a1a"   # Progress bar background

    @classmethod
    def set_provider_theme(cls, provider: str):
        """Update the theme's primary accent color based on the active provider."""
        if provider == "gemini":
            cls.PRI       = "#4db8ff" # Light Blue
            cls.PRI_DIM   = "#1f80c2"
            cls.PRI_GHO   = "#002a4d"
            cls.BORDER_B  = "#4db8ff55"
        elif provider == "ollama":
            cls.PRI       = "#00e5ff" # Cyan/Teal (Cyberpunk)
            cls.PRI_DIM   = "#0099ab"
            cls.PRI_GHO   = "#003b42"
            cls.BORDER_B  = "#00e5ff55"
        elif provider == "openrouter":
            cls.PRI       = "#00ff88" # Neon Green
            cls.PRI_DIM   = "#00a855"
            cls.PRI_GHO   = "#00331a"
            cls.BORDER_B  = "#00ff8855"
        elif provider == "lmstudio":
            cls.PRI       = "#ffb300" # Amber/Yellow
            cls.PRI_DIM   = "#cc8c00"
            cls.PRI_GHO   = "#4d3500"
            cls.BORDER_B  = "#ffb30055"
        else:
            cls.PRI       = "#ff5500" # Iron Man Orange fallback
            cls.PRI_DIM   = "#7a2800"
            cls.PRI_GHO   = "#1a0800"
            cls.BORDER_B  = "#ff550055"


def qcol(h: str, a: int = 255) -> QColor:
    c = QColor(h)
    c.setAlpha(a)
    return c


PROVIDER_COLORS = {
    "gemini":     {"primary": "#4db8ff", "bg": "#001833", "name": "Gemini"},
    "ollama":     {"primary": "#00e5ff", "bg": "#002b33", "name": "Ollama"},
    "openrouter": {"primary": "#00ff88", "bg": "#00221a", "name": "OpenRouter"},
    "lmstudio":   {"primary": "#ffb300", "bg": "#1a1100", "name": "LM Studio"},
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
