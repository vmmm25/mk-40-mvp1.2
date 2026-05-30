from __future__ import annotations

import os
import platform
import subprocess
import sys
import time
from pathlib import Path

import sounddevice as sd

from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSlider, QTabWidget, QVBoxLayout, QWidget,
    QCheckBox, QFileDialog,
)

from memory.config_manager import load_config, save_config, get_model, set_model
from ui.theme import Theme as C, PROVIDER_COLORS, get_openrouter_color as _get_openrouter_color
from lmstudio_control import (
    find_lmstudio_path, get_downloaded_models,
    launch_lmstudio, quit_lmstudio,
    is_server_running, get_server_status,
)


_OS = platform.system()  # "Windows" | "Darwin" | "Linux"


# ── Shared OpenRouter free-model catalogue ─────────────────────────────────
# Single source of truth used by BOTH the config tab and the right-panel combo.
# Tuple layout: (model_id, display_name)
_OR_FREE_MODELS: list[tuple[str, str]] = [
    ("nvidia/nemotron-3-super-120b-a12b:free",               "Nvidia Nemotron 3 Super 120B"),
    ("nvidia/nemotron-3-nano-30b-a3b:free",                  "Nvidia Nemotron 3 Nano 30B"),
    ("nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",   "Nvidia Nemotron 3 Nano Omni"),
    ("nvidia/nemotron-nano-12b-v2-vl:free",                  "Nvidia Nemotron Nano 12B VL"),
    ("nvidia/nemotron-nano-9b-v2:free",                      "Nvidia Nemotron Nano 9B"),
    ("google/gemma-4-31b-it:free",                           "Google Gemma 4 31B"),
    ("google/gemma-4-26b-a4b-it:free",                       "Google Gemma 4 26B A4B"),
    ("openai/gpt-oss-120b:free",                             "GPT-OSS 120B"),
    ("openai/gpt-oss-20b:free",                              "GPT-OSS 20B"),
    ("deepseek/deepseek-v4-flash:free",                      "DeepSeek V4 Flash"),
    ("deepseek/deepseek-r1:free",                            "DeepSeek R1"),
    ("meta-llama/llama-3.3-70b-instruct:free",               "Llama 3.3 70B"),
    ("meta-llama/llama-3.2-3b-instruct:free",                "Llama 3.2 3B"),
    ("qwen/qwen3-coder:free",                                "Qwen 3 Coder"),
    ("qwen/qwen3-next-80b-a3b-instruct:free",                "Qwen 3 Next 80B"),
    ("mistralai/mistral-small-3.1-24b-instruct:free",        "Mistral Small 3.1 24B"),
    ("mistralai/mistral-7b-instruct:free",                   "Mistral 7B"),
    ("liquid/lfm-2.5-1.2b-instruct:free",                   "Liquid LFM 2.5 1.2B"),
    ("liquid/lfm-2.5-1.2b-thinking:free",                   "Liquid LFM 2.5 1.2B Think"),
    ("minimax/minimax-m2.5:free",                            "MiniMax M2.5"),
    ("moonshotai/kimi-k2.6:free",                            "Moonshot Kimi K2.6"),
    ("nousresearch/hermes-3-llama-3.1-405b:free",            "Nous Hermes 3 405B"),
    ("cognitivecomputations/dolphin-mistral-24b-venice-edition:free", "Dolphin Mistral 24B"),
    ("poolside/laguna-m.1:free",                             "Poolside Laguna M.1"),
    ("poolside/laguna-xs.2:free",                            "Poolside Laguna XS.2"),
    ("z-ai/glm-4.5-air:free",                               "GLM 4.5 Air"),
]


def _populate_or_combo(combo: "QComboBox", saved_model: str) -> None:
    """Fill a QComboBox with _OR_FREE_MODELS and pre-select the saved model."""
    combo.blockSignals(True)
    combo.clear()
    for mid, desc in _OR_FREE_MODELS:
        combo.addItem(desc, mid)
    # Pre-select saved model (or first entry if not found)
    for i in range(combo.count()):
        if combo.itemData(i) == saved_model:
            combo.setCurrentIndex(i)
            break
    combo.blockSignals(False)


# ── Shared style sheets ──────────────────────────────────────────
_INPUT_STYLE = (
    "QLineEdit { background: #000d14; color: #d8f8ff; border: 1px solid #0d3347;"
    " border-radius: 3px; padding: 2px 6px; }"
    "QLineEdit:focus { border: 1px solid #00d4ff; }"
)
_COMBO_STYLE = (
    "QComboBox { background: #000d12; color: #8ffcff;"
    " border: 1px solid #0d3347; border-radius: 4px; padding: 2px 8px; }"
    "QComboBox:hover { border: 1px solid #1a5c7a; }"
    "QComboBox::drop-down { border: none; width: 20px; }"
    "QComboBox QAbstractItemView { background: #000d12; color: #8ffcff;"
    " border: 1px solid #0d3347; selection-background-color: #007a99; }"
)
_TAB_STYLE = (
    "QTabWidget::pane { border: none; background: transparent; }"
    "QTabBar::tab { background: #010f18; color: #3a8a9a;"
    " border: 1px solid #0d3347; border-bottom: none;"
    " padding: 6px 16px; font: bold 10pt 'Segoe UI'; }"
    "QTabBar::tab:selected { background: #011520; color: #00d4ff; }"
    "QTabBar::tab:hover { color: #5ab8cc; }"
)


class ConfigToolbar(QWidget):
    """Compact top toolbar for provider management."""

    provider_changed = pyqtSignal(str)

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self._main_win = main_window
        self.setStyleSheet(f"background: {C.DARK}; border-bottom: 1px solid {C.BORDER_B};")
        self._expanded = False
        self._setup_ui()

    def _build_lbl(self, txt, sz=10, bold=False, color=None, align=None, pad=False):
        w = QLabel(txt)
        if align:
            w.setAlignment(align)
        w.setFont(QFont("Segoe UI", sz, QFont.Weight.Bold if bold else QFont.Weight.Normal))
        w.setStyleSheet(
            f"color: {color or C.TEXT_MED}; background: transparent;"
            f"{'padding: 2px 6px;' if pad else ''}"
        )
        return w

    def _build_btn(self, txt, color=C.PRI, h=30, w=None, bold=True):
        btn = QPushButton(txt)
        btn.setFont(QFont("Segoe UI", 10 if bold else 9, QFont.Weight.Bold if bold else QFont.Weight.Normal))
        if w:
            btn.setFixedWidth(w)
        btn.setFixedHeight(h)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {C.DARK}; color: {color};
                border: 1px solid {C.BORDER_B}; border-radius: 4px;
                padding: 2px 10px;
            }}
            QPushButton:hover {{
                background: {color}22; color: {color};
                border: 1px solid {color};
            }}
            QPushButton:pressed {{
                background: {color}44;
            }}
            QPushButton:disabled {{
                color: {C.TEXT_DIM}; border-color: {C.BORDER};
                background: transparent;
            }}
        """)
        return btn

    def _setup_ui(self):
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        # ── Settings Tab Widget (Pure Static Panel) ──
        self._settings_tabs = QTabWidget()
        self._settings_tabs.setStyleSheet(_TAB_STYLE)
        
        # We use compact labels to fit beautifully in 340px
        self._settings_tabs.addTab(self._build_gemini_tab(), "🧠 GEM")
        self._settings_tabs.addTab(self._build_openrouter_tab(), "🔗 OR")
        self._settings_tabs.addTab(self._build_ollama_tab(), "🤖 OLL")
        self._settings_tabs.addTab(self._build_lmstudio_tab(), "🟠 LM")
        self._settings_tabs.addTab(self._build_audio_tab(), "🎙 VOZ")
        
        self._main_layout.addWidget(self._settings_tabs)

    def update_status(self, provider: str):
        """No-op status updater, compatibility fallback."""
        pass

    def _on_provider_clicked(self, provider: str):
        """Emit provider signal, compatibility fallback."""
        self.provider_changed.emit(provider)

    # ── Tab: Gemini ────────────────────────────────────────────────
    def _build_gemini_tab(self) -> QWidget:
        w = QWidget(); lay = QVBoxLayout(w)
        lay.setContentsMargins(20, 14, 20, 14)
        lay.setSpacing(8)

        lay.addWidget(self._build_lbl(
            "Ingresa tu API Key de Google Gemini para activar el asistente de voz.\n"
            "Paso 1: Ve a https://aistudio.google.com/app/apikey\n"
            "Paso 2: Crea una API Key (es gratis con cuota generosa)\n"
            "Paso 3: Cópiala y pégala aquí abajo.",
            7, color=C.TEXT_DIM)
        )
        lay.addSpacing(4)

        cfg = load_config()
        lay.addWidget(self._build_lbl("Gemini API Key", 8, True, C.TEXT_MED))
        self._gemini_key_input = QLineEdit()
        self._gemini_key_input.setFont(QFont("Segoe UI", 11))
        self._gemini_key_input.setFixedHeight(26)
        self._gemini_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._gemini_key_input.setText(cfg.get("gemini_api_key", ""))
        self._gemini_key_input.setStyleSheet(_INPUT_STYLE)
        lay.addWidget(self._gemini_key_input)
        lay.addSpacing(8)

        # Save
        save_row = QHBoxLayout(); save_row.setSpacing(8)
        self._save_gemini_btn = self._build_btn("💾  GUARDAR API KEY", C.GREEN, h=30)
        self._save_gemini_btn.clicked.connect(self._save_gemini_key)
        save_row.addWidget(self._save_gemini_btn)
        self._gemini_status = self._build_lbl("", 7, color=C.TEXT_DIM)
        save_row.addWidget(self._gemini_status)
        save_row.addStretch()
        lay.addLayout(save_row)

        lay.addStretch()
        return w

    # ── Tab: OpenRouter ────────────────────────────────────────────
    def _build_openrouter_tab(self) -> QWidget:
        w = QWidget(); lay = QVBoxLayout(w)
        lay.setContentsMargins(20, 14, 20, 14)
        lay.setSpacing(8)

        lay.addWidget(self._build_lbl(
            "Ingresa tu API Key de OpenRouter para usar modelos en la nube.\n"
            "Paso 1: Ve a https://openrouter.ai/keys\n"
            "Paso 2: Crea una cuenta y genera una API Key\n"
            "Paso 3: Cópiala y pégala aquí abajo.",
            7, color=C.TEXT_DIM)
        )
        lay.addSpacing(4)

        cfg = load_config()
        lay.addWidget(self._build_lbl("OpenRouter API Key", 8, True, C.TEXT_MED))
        self._openrouter_key_input = QLineEdit()
        self._openrouter_key_input.setFont(QFont("Segoe UI", 11))
        self._openrouter_key_input.setFixedHeight(26)
        self._openrouter_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._openrouter_key_input.setText(cfg.get("openrouter_api_key", ""))
        self._openrouter_key_input.setStyleSheet(_INPUT_STYLE)
        lay.addWidget(self._openrouter_key_input)
        lay.addSpacing(8)

        # Save
        save_row = QHBoxLayout(); save_row.setSpacing(8)
        self._save_or_btn = self._build_btn("💾  GUARDAR API KEY", C.GREEN, h=30)
        self._save_or_btn.clicked.connect(self._save_openrouter_key)
        save_row.addWidget(self._save_or_btn)
        self._or_status = self._build_lbl("", 7, color=C.TEXT_DIM)
        save_row.addWidget(self._or_status)
        save_row.addStretch()
        lay.addLayout(save_row)

        lay.addSpacing(12)

        # ── Free model selector ──
        lay.addWidget(self._build_lbl("FREE MODELS (OpenRouter)", 8, True, C.GREEN))
        lay.addWidget(self._build_lbl(
            "Selecciona un modelo gratuito. Todos usan el sufijo :free "
            "y no tienen costo por token.",
            7, color=C.TEXT_DIM)
        )
        lay.addSpacing(4)

        self._or_model_combo = QComboBox()
        self._or_model_combo.setFont(QFont("Segoe UI", 11))
        self._or_model_combo.setFixedHeight(26)
        self._or_model_combo.setStyleSheet(_COMBO_STYLE)
        # Use the shared catalogue so both combos always show the same list
        _populate_or_combo(self._or_model_combo, get_model("openrouter"))
        lay.addWidget(self._or_model_combo)

        save_model_row = QHBoxLayout(); save_model_row.setSpacing(8)
        self._save_or_model_btn = self._build_btn("💾  GUARDAR MODELO", C.GREEN, h=28)
        self._save_or_model_btn.clicked.connect(self._save_or_model)
        save_model_row.addWidget(self._save_or_model_btn)
        self._or_model_status = self._build_lbl("", 7, color=C.TEXT_DIM)
        save_model_row.addWidget(self._or_model_status)
        save_model_row.addStretch()
        lay.addLayout(save_model_row)

        lay.addStretch()
        return w

    def _save_or_model(self):
        """Save selected OpenRouter free model to config, sync right-panel, restart engine."""
        model_id = self._or_model_combo.currentData()
        if model_id:
            set_model(model_id, "openrouter")
            self._or_model_status.setText(f"✅ Guardado: {model_id.split('/')[1].split(':')[0]}")
            self._or_model_status.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
            # Keep the right-panel combo in sync
            right_combo = self._main_win._right_model_combo
            _populate_or_combo(right_combo, model_id)
            # Trigger engine restart so the new model takes effect
            cfg = load_config()
            provider = cfg.get("selected_provider", "gemini")
            if hasattr(self._main_win, '_on_provider_changed') and self._main_win._on_provider_changed:
                self._main_win._on_provider_changed(provider)
        else:
            self._or_model_status.setText("❌ No se seleccionó modelo")
            self._or_model_status.setStyleSheet(f"color: {C.RED}; background: transparent;")

    # ── Tab: Audio Settings ──────────────────────────────────────────
    def _build_audio_tab(self) -> QWidget:
        w = QWidget(); lay = QVBoxLayout(w)
        lay.setContentsMargins(20, 14, 20, 14)
        lay.setSpacing(8)

        cfg = load_config()

        lay.addWidget(self._build_lbl("Select your audio input and output devices.", 7, color=C.TEXT_DIM))
        lay.addSpacing(4)

        # Microphone
        lay.addWidget(self._build_lbl("Microphone (Input Device)", 8, True, C.TEXT_MED))
        self._mic_combo = QComboBox()
        self._mic_combo.setFont(QFont("Segoe UI", 11))
        self._mic_combo.setFixedHeight(26)
        self._mic_combo.setStyleSheet(_COMBO_STYLE)
        lay.addWidget(self._mic_combo)
        lay.addSpacing(4)

        # Speaker
        lay.addWidget(self._build_lbl("Speaker (Output Device)", 8, True, C.TEXT_MED))
        self._speaker_combo = QComboBox()
        self._speaker_combo.setFont(QFont("Segoe UI", 11))
        self._speaker_combo.setFixedHeight(26)
        self._speaker_combo.setStyleSheet(_COMBO_STYLE)
        lay.addWidget(self._speaker_combo)
        lay.addSpacing(8)

        # Volume
        lay.addWidget(self._build_lbl("Master Volume", 8, True, C.TEXT_MED))
        vol_row = QHBoxLayout(); vol_row.setSpacing(8)
        self._volume_slider = QSlider(Qt.Orientation.Horizontal)
        self._volume_slider.setFixedHeight(22)
        self._volume_slider.setMinimum(0)
        self._volume_slider.setMaximum(100)
        saved_vol = cfg.get("audio_volume", 80)
        self._volume_slider.setValue(saved_vol)
        self._volume_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background: {C.BORDER}; height: 4px; border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {C.PRI}; width: 14px; height: 14px;
                margin: -5px 0; border-radius: 7px;
            }}
            QSlider::sub-page:horizontal {{
                background: {C.PRI_DIM}; border-radius: 2px;
            }}
        """)
        self._volume_slider.valueChanged.connect(self._on_volume_changed)
        vol_row.addWidget(self._volume_slider, stretch=1)
        self._vol_label = self._build_lbl(f"{saved_vol}%", 8, bold=True, color=C.PRI)
        self._vol_label.setFixedWidth(40)
        vol_row.addWidget(self._vol_label)
        lay.addLayout(vol_row)

        # Populate device lists
        self._populate_audio_devices()

        # ── Divider Line ──
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {C.BORDER}; margin: 8px 0;")
        lay.addWidget(sep)

        # ── Title Label ──
        lay.addWidget(self._build_lbl("🎙  MODO DE VOZ SINCRÓNICO (OLLAMA / LM STUDIO / OR)", 8, True, C.PRI))

        # Checkbox Enable Voice
        self._voice_enabled_chk = QCheckBox("Activar modo de voz en proveedores de texto")
        self._voice_enabled_chk.setFont(QFont("Segoe UI", 10))
        self._voice_enabled_chk.setStyleSheet(f"color: {C.TEXT};")
        self._voice_enabled_chk.setChecked(cfg.get("voice_wrapper_enabled", False))
        self._voice_enabled_chk.toggled.connect(self._on_voice_settings_changed)
        lay.addWidget(self._voice_enabled_chk)

        # Engines Layout (STT and TTS side by side)
        eng_lay = QHBoxLayout()
        eng_lay.setSpacing(10)

        # STT Engine
        stt_box = QVBoxLayout()
        stt_box.addWidget(self._build_lbl("Motor de Transcripción (STT)", 8, True, C.TEXT_MED))
        self._stt_engine_combo = QComboBox()
        self._stt_engine_combo.setFont(QFont("Segoe UI", 10))
        self._stt_engine_combo.setFixedHeight(26)
        self._stt_engine_combo.setStyleSheet(_COMBO_STYLE)
        self._stt_engine_combo.addItem("Gemini Cloud", "gemini")
        self._stt_engine_combo.addItem("Whisper.cpp Local", "whisper")
        saved_stt = cfg.get("stt_engine", "gemini")
        for i in range(self._stt_engine_combo.count()):
            if self._stt_engine_combo.itemData(i) == saved_stt:
                self._stt_engine_combo.setCurrentIndex(i)
                break
        self._stt_engine_combo.currentIndexChanged.connect(self._on_voice_settings_changed)
        stt_box.addWidget(self._stt_engine_combo)
        eng_lay.addLayout(stt_box, stretch=1)

        # TTS Engine
        tts_box = QVBoxLayout()
        tts_box.addWidget(self._build_lbl("Motor de Voz (TTS)", 8, True, C.TEXT_MED))
        self._tts_engine_combo = QComboBox()
        self._tts_engine_combo.setFont(QFont("Segoe UI", 10))
        self._tts_engine_combo.setFixedHeight(26)
        self._tts_engine_combo.setStyleSheet(_COMBO_STYLE)
        self._tts_engine_combo.addItem("Gemini Cloud", "gemini")
        self._tts_engine_combo.addItem("Piper Local", "piper")
        saved_tts = cfg.get("tts_engine", "gemini")
        for i in range(self._tts_engine_combo.count()):
            if self._tts_engine_combo.itemData(i) == saved_tts:
                self._tts_engine_combo.setCurrentIndex(i)
                break
        self._tts_engine_combo.currentIndexChanged.connect(self._on_voice_settings_changed)
        tts_box.addWidget(self._tts_engine_combo)
        eng_lay.addLayout(tts_box, stretch=1)

        lay.addLayout(eng_lay)

        # ── Gemini Cloud Settings ──
        self._gemini_voice_container = QWidget()
        ge_lay = QVBoxLayout(self._gemini_voice_container)
        ge_lay.setContentsMargins(0, 0, 0, 0)
        ge_lay.setSpacing(4)

        ge_lay.addWidget(self._build_lbl("🔑  API Key de Google Gemini (Cloud STT / TTS)", 8, True, C.TEXT_DIM))
        self._gemini_voice_key_edit = QLineEdit(cfg.get("gemini_api_key", ""))
        self._gemini_voice_key_edit.setFixedHeight(24)
        self._gemini_voice_key_edit.setFont(QFont("Segoe UI", 9))
        self._gemini_voice_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._gemini_voice_key_edit.setStyleSheet(_INPUT_STYLE)
        self._gemini_voice_key_edit.textChanged.connect(self._on_voice_settings_changed)
        ge_lay.addWidget(self._gemini_voice_key_edit)

        lay.addWidget(self._gemini_voice_container)

        # ── Whisper Paths (collapsible) ──
        self._whisper_container = QWidget()
        wh_lay = QVBoxLayout(self._whisper_container)
        wh_lay.setContentsMargins(0, 0, 0, 0)
        wh_lay.setSpacing(4)

        wh_lay.addWidget(self._build_lbl("🎙  Ruta de whisper-cli.exe / main.exe (Local STT)", 8, True, C.TEXT_DIM))
        wh_exec_row = QHBoxLayout()
        self._whisper_path_edit = QLineEdit(cfg.get("whisper_path", ""))
        self._whisper_path_edit.setFixedHeight(24)
        self._whisper_path_edit.setFont(QFont("Segoe UI", 9))
        self._whisper_path_edit.setStyleSheet(_INPUT_STYLE)
        self._whisper_path_edit.textChanged.connect(self._on_voice_settings_changed)
        wh_exec_row.addWidget(self._whisper_path_edit)
        self._whisper_path_btn = self._build_btn("Buscar", C.PRI, h=24, bold=False)
        self._whisper_path_btn.clicked.connect(self._browse_whisper_path)
        wh_exec_row.addWidget(self._whisper_path_btn)
        wh_lay.addLayout(wh_exec_row)

        wh_lay.addWidget(self._build_lbl("📦  Ruta del Modelo GGML (.bin)", 8, True, C.TEXT_DIM))
        wh_mod_row = QHBoxLayout()
        self._whisper_model_edit = QLineEdit(cfg.get("whisper_model", ""))
        self._whisper_model_edit.setFixedHeight(24)
        self._whisper_model_edit.setFont(QFont("Segoe UI", 9))
        self._whisper_model_edit.setStyleSheet(_INPUT_STYLE)
        self._whisper_model_edit.textChanged.connect(self._on_voice_settings_changed)
        wh_mod_row.addWidget(self._whisper_model_edit)
        self._whisper_model_btn = self._build_btn("Buscar", C.PRI, h=24, bold=False)
        self._whisper_model_btn.clicked.connect(self._browse_whisper_model)
        wh_mod_row.addWidget(self._whisper_model_btn)
        wh_lay.addLayout(wh_mod_row)

        lay.addWidget(self._whisper_container)

        # ── Piper Paths (collapsible) ──
        self._piper_container = QWidget()
        pi_lay = QVBoxLayout(self._piper_container)
        pi_lay.setContentsMargins(0, 0, 0, 0)
        pi_lay.setSpacing(4)

        pi_lay.addWidget(self._build_lbl("🗣  Ruta de piper.exe (Local TTS)", 8, True, C.TEXT_DIM))
        pi_exec_row = QHBoxLayout()
        self._piper_path_edit = QLineEdit(cfg.get("piper_path", ""))
        self._piper_path_edit.setFixedHeight(24)
        self._piper_path_edit.setFont(QFont("Segoe UI", 9))
        self._piper_path_edit.setStyleSheet(_INPUT_STYLE)
        self._piper_path_edit.textChanged.connect(self._on_voice_settings_changed)
        pi_exec_row.addWidget(self._piper_path_edit)
        self._piper_path_btn = self._build_btn("Buscar", C.PRI, h=24, bold=False)
        self._piper_path_btn.clicked.connect(self._browse_piper_path)
        pi_exec_row.addWidget(self._piper_path_btn)
        pi_lay.addLayout(pi_exec_row)

        pi_lay.addWidget(self._build_lbl("🗣  Ruta de Voz Piper (.onnx)", 8, True, C.TEXT_DIM))
        pi_mod_row = QHBoxLayout()
        self._piper_model_edit = QLineEdit(cfg.get("piper_model", ""))
        self._piper_model_edit.setFixedHeight(24)
        self._piper_model_edit.setFont(QFont("Segoe UI", 9))
        self._piper_model_edit.setStyleSheet(_INPUT_STYLE)
        self._piper_model_edit.textChanged.connect(self._on_voice_settings_changed)
        pi_mod_row.addWidget(self._piper_model_edit)
        self._piper_model_btn = self._build_btn("Buscar", C.PRI, h=24, bold=False)
        self._piper_model_btn.clicked.connect(self._browse_piper_model)
        pi_mod_row.addWidget(self._piper_model_btn)
        pi_lay.addLayout(pi_mod_row)

        lay.addWidget(self._piper_container)

        # Set initial dynamic visibilities
        self._update_voice_visibility()

        lay.addStretch()
        return w

    def _on_voice_settings_changed(self):
        """Save the updated voice settings to config and update visibility."""
        if not hasattr(self, "_voice_enabled_chk"):
            return

        enabled = self._voice_enabled_chk.isChecked()
        stt = self._stt_engine_combo.currentData()
        tts = self._tts_engine_combo.currentData()
        gemini_k = self._gemini_voice_key_edit.text().strip()
        whisper_p = self._whisper_path_edit.text().strip()
        whisper_m = self._whisper_model_edit.text().strip()
        piper_p = self._piper_path_edit.text().strip()
        piper_m = self._piper_model_edit.text().strip()

        save_config({
            "voice_wrapper_enabled": enabled,
            "stt_engine": stt,
            "tts_engine": tts,
            "gemini_api_key": gemini_k,
            "whisper_path": whisper_p,
            "whisper_model": whisper_m,
            "piper_path": piper_p,
            "piper_model": piper_m,
        })

        if hasattr(self, "_gemini_key_input") and self._gemini_key_input.text() != gemini_k:
            self._gemini_key_input.blockSignals(True)
            self._gemini_key_input.setText(gemini_k)
            self._gemini_key_input.blockSignals(False)

        self._update_voice_visibility()

    def _update_voice_visibility(self):
        """Update visibility of Gemini/Whisper/Piper configuration blocks based on whether voice wrapper is enabled."""
        if not hasattr(self, "_voice_enabled_chk"):
            return
        enabled = self._voice_enabled_chk.isChecked()

        self._gemini_voice_container.setVisible(enabled)
        self._whisper_container.setVisible(enabled)
        self._piper_container.setVisible(enabled)

    def _browse_whisper_path(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar ejecutable de Whisper.cpp", "", 
            "Ejecutable (*.exe *.exe);;Todos los archivos (*)"
        )
        if file_path:
            self._whisper_path_edit.setText(os.path.normpath(file_path))
            self._on_voice_settings_changed()

    def _browse_whisper_model(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar modelo GGML de Whisper (.bin)", "", 
            "Modelos GGML (*.bin);;Todos los archivos (*)"
        )
        if file_path:
            self._whisper_model_edit.setText(os.path.normpath(file_path))
            self._on_voice_settings_changed()

    def _browse_piper_path(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar ejecutable de Piper", "", 
            "Ejecutable (*.exe *.exe);;Todos los archivos (*)"
        )
        if file_path:
            self._piper_path_edit.setText(os.path.normpath(file_path))
            self._on_voice_settings_changed()

    def _browse_piper_model(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar modelo de voz Piper (.onnx)", "", 
            "Modelos ONNX (*.onnx);;Todos los archivos (*)"
        )
        if file_path:
            self._piper_model_edit.setText(os.path.normpath(file_path))
            self._on_voice_settings_changed()

    # ── Tab: Ollama Tools + Commands ─────────────────────────────────
    def _build_ollama_tab(self) -> QWidget:
        w = QWidget(); lay = QHBoxLayout(w)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(24)

        # Left: Command Reference
        left = QVBoxLayout(); left.setSpacing(4)
        left.addWidget(self._build_lbl("▸  COMMAND REFERENCE", 9, True, C.ACC2, pad=True))
        cmd_list = [
            ("ollama pull [model]",  "Download a model (e.g. llama3.2, mistral)"),
            ("ollama serve",         "Start the Ollama background server"),
            ("ollama list",          "List all downloaded models"),
            ("ollama run [model]",   "Run a model in interactive terminal"),
            ("ollama rm [model]",    "Remove a downloaded model"),
            ("ollama stop",          "Stop the running model"),
            ("ollama ps",            "Show currently running models"),
        ]
        for cmd, desc in cmd_list:
            row = QHBoxLayout(); row.setSpacing(8)
            c = self._build_lbl(cmd, 8, True, C.PRI)
            c.setFixedWidth(200)
            row.addWidget(c)
            row.addWidget(self._build_lbl(desc, 7, color=C.TEXT_DIM))
            row.addStretch()
            left.addLayout(row)
        left.addStretch()
        lay.addLayout(left, stretch=3)

        # Vertical separator
        sep_v = QFrame(); sep_v.setFrameShape(QFrame.Shape.VLine)
        sep_v.setStyleSheet(f"color: {C.BORDER};")
        lay.addWidget(sep_v)

        # Right: Ollama Manager
        right = QVBoxLayout(); right.setSpacing(6)
        right.addWidget(self._build_lbl("▸  MODEL MANAGER", 9, True, C.ACC2, pad=True))

        # Model dropdown + reload
        right.addWidget(self._build_lbl("Select model:", 7, color=C.TEXT_MED))
        combo_row = QHBoxLayout(); combo_row.setSpacing(6)
        self._model_combo = QComboBox()
        self._model_combo.setEditable(True)
        self._model_combo.setFont(QFont("Segoe UI", 12))
        self._model_combo.setFixedHeight(28)
        self._model_combo.setMinimumWidth(240)
        self._model_combo.setStyleSheet(_COMBO_STYLE)
        combo_row.addWidget(self._model_combo)
        self._reload_btn = self._build_btn("↻", C.PRI, h=28, w=32, bold=False)
        self._reload_btn.setToolTip("Refresh model list from ollama list")
        self._reload_btn.clicked.connect(self._refresh_model_list)
        combo_row.addWidget(self._reload_btn)
        combo_row.addStretch()
        right.addLayout(combo_row)
        self._refresh_model_list()

        # Pull button
        pull_row = QHBoxLayout(); pull_row.setSpacing(8)
        self._pull_btn = self._build_btn("⬇  PULL MODEL", C.PRI, h=30)
        self._pull_btn.clicked.connect(self._on_pull_model)
        pull_row.addWidget(self._pull_btn)
        self._pull_status = self._build_lbl("Ready", 7, color=C.TEXT_DIM)
        pull_row.addWidget(self._pull_status)
        pull_row.addStretch()
        right.addLayout(pull_row)
        # Quick presets
        right.addWidget(self._build_lbl("Quick pull:", 7, color=C.TEXT_MED))
        presets_row = QHBoxLayout(); presets_row.setSpacing(4)
        for model_id, label in [
            ("llama3.2", "Llama 3.2"),
            ("mistral", "Mistral"),
            ("gemma2", "Gemma 2"),
            ("phi4", "Phi-4"),
            ("deepseek-r1", "DeepSeek R1"),
        ]:
            b = self._build_btn(label, C.ACC2, h=26, bold=False)
            b.clicked.connect(lambda checked, m=model_id: self._quick_pull(m))
            presets_row.addWidget(b)
        presets_row.addStretch()
        right.addLayout(presets_row)
        # Server controls
        right.addSpacing(2)
        right.addWidget(self._build_lbl("Server control:", 7, color=C.TEXT_MED))
        srv_row = QHBoxLayout(); srv_row.setSpacing(8)
        self._up_btn = self._build_btn("▲  UP SERVER  (ollama serve)", C.GREEN, h=30)
        self._up_btn.clicked.connect(self._on_up_server)
        srv_row.addWidget(self._up_btn)
        right.addLayout(srv_row)
        srv_row2 = QHBoxLayout(); srv_row2.setSpacing(8)
        self._down_btn = self._build_btn("▼  DOWN SERVER  (kill ollama)", C.RED, h=30)
        self._down_btn.clicked.connect(self._on_down_server)
        srv_row2.addWidget(self._down_btn)
        self._srv_status = self._build_lbl("Server: unknown", 7, color=C.TEXT_DIM)
        srv_row2.addWidget(self._srv_status)
        srv_row2.addStretch()
        right.addLayout(srv_row2)
        right.addStretch()
        lay.addLayout(right, stretch=2)

        # Check server on init
        self._check_server_status()
        return w

    # ── Tab: LM Studio ───────────────────────────────────────────────
    def _build_lmstudio_tab(self) -> QWidget:
        w = QWidget(); lay = QHBoxLayout(w)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(24)

        # Left: Installation & Path Info
        left = QVBoxLayout(); left.setSpacing(4)
        left.addWidget(self._build_lbl("▸  LM STUDIO SETUP", 9, True, C.ACC, pad=True))
        left.addWidget(self._build_lbl(
            "LM Studio proporciona un servidor local OpenAI-compatible.\n"
            "MARK XL se conecta automáticamente para usar modelos locales.",
            7, color=C.TEXT_DIM)
        )
        left.addSpacing(6)

        # Auto-detect path
        self._lm_path_lbl = self._build_lbl("🔍 Detectando instalación...", 7, color=C.TEXT_MED)
        left.addWidget(self._lm_path_lbl)
        left.addSpacing(4)

        # URL input
        left.addWidget(self._build_lbl("Server URL:", 8, True, C.TEXT_MED))
        cfg = load_config()
        url_row = QHBoxLayout(); url_row.setSpacing(6)
        self._lm_url_input = QLineEdit()
        self._lm_url_input.setFont(QFont("Segoe UI", 11))
        self._lm_url_input.setFixedHeight(26)
        self._lm_url_input.setText(cfg.get("lmstudio_url", "http://localhost:1234"))
        self._lm_url_input.setStyleSheet(_INPUT_STYLE)
        url_row.addWidget(self._lm_url_input, stretch=1)

        # Save URL button
        self._save_lm_url_btn = self._build_btn("💾", C.GREEN, h=26, w=32, bold=False)
        self._save_lm_url_btn.setToolTip("Save server URL")
        self._save_lm_url_btn.clicked.connect(self._save_lmstudio_url)
        url_row.addWidget(self._save_lm_url_btn)
        left.addLayout(url_row)
        left.addSpacing(4)

        # Auto-launch toggle
        auto_row = QHBoxLayout(); auto_row.setSpacing(8)
        auto_row.addWidget(self._build_lbl("Auto-launch LM Studio:", 8, color=C.TEXT_MED))
        self._lm_auto_toggle = self._build_btn("", C.GREEN, h=24, w=60)
        self._lm_auto_toggle.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        self._lm_auto_toggle.clicked.connect(self._toggle_lm_auto)
        self._update_lm_auto_btn(cfg.get("lmstudio_auto_launch", True))
        auto_row.addWidget(self._lm_auto_toggle)
        auto_row.addStretch()
        left.addLayout(auto_row)
        left.addSpacing(6)

        # App control buttons
        left.addWidget(self._build_lbl("App Control:", 8, True, C.TEXT_MED))
        ctrl_row = QHBoxLayout(); ctrl_row.setSpacing(8)
        self._lm_launch_btn = self._build_btn("▶  LAUNCH", C.GREEN, h=28)
        self._lm_launch_btn.clicked.connect(self._on_lm_launch)
        ctrl_row.addWidget(self._lm_launch_btn)
        self._lm_quit_btn = self._build_btn("■  QUIT", C.RED, h=28)
        self._lm_quit_btn.clicked.connect(self._on_lm_quit)
        ctrl_row.addWidget(self._lm_quit_btn)
        ctrl_row.addStretch()
        left.addLayout(ctrl_row)
        left.addSpacing(4)

        self._lm_install_lbl = self._build_lbl("", 7, color=C.TEXT_DIM)
        left.addWidget(self._lm_install_lbl)
        left.addStretch()
        lay.addLayout(left, stretch=3)

        # Vertical separator
        sep_v = QFrame(); sep_v.setFrameShape(QFrame.Shape.VLine)
        sep_v.setStyleSheet(f"color: {C.BORDER};")
        lay.addWidget(sep_v)

        # Right: Model Selection & Server Status
        right = QVBoxLayout(); right.setSpacing(6)
        right.addWidget(self._build_lbl("▸  MODEL & SERVER", 9, True, C.ACC, pad=True))

        # Server status indicator
        self._lm_server_lbl = self._build_lbl("● Server: checking...", 9, True, C.TEXT_DIM)
        self._lm_server_lbl.setStyleSheet(f"color: {C.TEXT_DIM}; background: transparent; padding: 2px 0;")
        right.addWidget(self._lm_server_lbl)

        # Refresh status button
        status_row = QHBoxLayout(); status_row.setSpacing(6)
        self._lm_refresh_btn = self._build_btn("↻  REFRESH STATUS", C.PRI, h=26, bold=False)
        self._lm_refresh_btn.clicked.connect(self._refresh_lmstudio_status)
        status_row.addWidget(self._lm_refresh_btn)
        status_row.addStretch()
        right.addLayout(status_row)
        right.addSpacing(6)

        # Model combo
        right.addWidget(self._build_lbl("Downloaded models:", 8, True, C.TEXT_MED))
        self._lm_model_combo = QComboBox()
        self._lm_model_combo.setFont(QFont("Segoe UI", 11))
        self._lm_model_combo.setFixedHeight(26)
        self._lm_model_combo.setStyleSheet(_COMBO_STYLE)
        right.addWidget(self._lm_model_combo)

        # Save + Sync model button
        save_model_row = QHBoxLayout(); save_model_row.setSpacing(6)
        self._save_lm_model_btn = self._build_btn("💾  GUARDAR MODELO", C.GREEN, h=28)
        self._save_lm_model_btn.clicked.connect(self._save_lm_model)
        save_model_row.addWidget(self._save_lm_model_btn)
        self._lm_model_status = self._build_lbl("", 7, color=C.TEXT_DIM)
        save_model_row.addWidget(self._lm_model_status)
        save_model_row.addStretch()
        right.addLayout(save_model_row)

        # Populate models AFTER status label exists
        self._populate_lm_models()
        right.addSpacing(6)

        # Refresh models button
        refresh_models_row = QHBoxLayout(); refresh_models_row.setSpacing(6)
        self._lm_refresh_models_btn = self._build_btn("↻  SCAN LOCAL MODELS", C.ACC, h=26, bold=False)
        self._lm_refresh_models_btn.clicked.connect(self._populate_lm_models)
        refresh_models_row.addWidget(self._lm_refresh_models_btn)
        refresh_models_row.addStretch()
        right.addLayout(refresh_models_row)

        right.addStretch()
        lay.addLayout(right, stretch=2)

        # Run initial checks
        self._check_lmstudio_path()
        self._refresh_lmstudio_status()
        return w

    def _check_lmstudio_path(self):
        """Find LM Studio installation and update UI."""
        path = find_lmstudio_path()
        if path:
            self._lm_path_lbl.setText(f"✅ Instalado en: {path.parent}")
            self._lm_path_lbl.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
        else:
            self._lm_path_lbl.setText("⚠️ LM Studio no encontrado. Instálalo desde lmstudio.ai")
            self._lm_path_lbl.setStyleSheet(f"color: {C.RED}; background: transparent;")

    def _refresh_lmstudio_status(self):
        """Check LM Studio server status and update UI."""
        running = is_server_running()
        if running:
            self._lm_server_lbl.setText("●  Server: RUNNING")
            self._lm_server_lbl.setStyleSheet(f"color: {C.GREEN}; background: transparent; padding: 2px 0;")
        else:
            self._lm_server_lbl.setText("●  Server: OFFLINE")
            self._lm_server_lbl.setStyleSheet(f"color: {C.RED}; background: transparent; padding: 2px 0;")

    def _populate_lm_models(self):
        """Scan for local models and populate the combo."""
        self._lm_model_combo.blockSignals(True)
        self._lm_model_combo.clear()

        saved_model = get_model("lmstudio")
        models = get_downloaded_models()

        if models:
            for m in models:
                self._lm_model_combo.addItem(m["name"], m["id"])

            # Pre-select saved model
            for i in range(self._lm_model_combo.count()):
                if self._lm_model_combo.itemData(i) == saved_model:
                    self._lm_model_combo.setCurrentIndex(i)
                    break
            else:
                # Default to first
                self._lm_model_combo.setCurrentIndex(0)
        else:
            self._lm_model_combo.addItem("Default (loaded model)", "local-model")

        self._lm_model_combo.blockSignals(False)

        # Update status tooltip
        count = self._lm_model_combo.count()
        if count > 0:
            self._lm_model_status.setText(f"📦 {count} modelo(s) encontrado(s)")
            self._lm_model_status.setStyleSheet(f"color: {C.TEXT_MED}; background: transparent;")
        else:
            self._lm_model_status.setText("⚠️ No se encontraron modelos locales")
            self._lm_model_status.setStyleSheet(f"color: {C.RED}; background: transparent;")

    def _save_lm_model(self):
        """Save LM Studio model selection, sync right-panel, restart engine."""
        model_id = self._lm_model_combo.currentData()
        if model_id:
            set_model(model_id, "lmstudio")
            short_name = model_id.split("/")[-1].split(":")[0]
            self._lm_model_status.setText(f"✅ Guardado: {short_name}")
            self._lm_model_status.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
            # Keep right-panel combo in sync
            right_combo = self._main_win._right_model_combo
            if hasattr(right_combo, 'blockSignals'):
                right_combo.blockSignals(True)
                right_combo.clear()
                # Re-populate with just models from combo
                for i in range(self._lm_model_combo.count()):
                    mid = self._lm_model_combo.itemData(i)
                    name = self._lm_model_combo.itemText(i)
                    right_combo.addItem(name, mid)
                # Select saved
                for i in range(right_combo.count()):
                    if right_combo.itemData(i) == model_id:
                        right_combo.setCurrentIndex(i)
                        break
                right_combo.blockSignals(False)
            # Trigger engine restart
            cfg = load_config()
            provider = cfg.get("selected_provider", "gemini")
            if hasattr(self._main_win, '_on_provider_changed') and self._main_win._on_provider_changed:
                self._main_win._on_provider_changed(provider)
        else:
            self._lm_model_status.setText("❌ No se seleccionó modelo")
            self._lm_model_status.setStyleSheet(f"color: {C.RED}; background: transparent;")

    def _save_lmstudio_url(self):
        """Save LM Studio URL to config."""
        url = self._lm_url_input.text().strip()
        if url:
            save_config({"lmstudio_url": url})
            self._save_lm_url_btn.setText("✓")
            self._save_lm_url_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {C.DARK}; color: {C.GREEN};
                    border: 1px solid {C.GREEN}; border-radius: 3px;
                    padding: 2px 8px;
                }}
            """)

    def _toggle_lm_auto(self):
        """Toggle auto-launch setting."""
        cfg = load_config()
        current = cfg.get("lmstudio_auto_launch", True)
        new_val = not current
        save_config({"lmstudio_auto_launch": new_val})
        self._update_lm_auto_btn(new_val)

    def _update_lm_auto_btn(self, enabled: bool):
        """Update auto-launch toggle button appearance."""
        if enabled:
            self._lm_auto_toggle.setText("ON")
            self._lm_auto_toggle.setStyleSheet(f"""
                QPushButton {{
                    background: {C.GREEN}22; color: {C.GREEN};
                    border: 1px solid {C.GREEN}; border-radius: 3px;
                }}
            """)
        else:
            self._lm_auto_toggle.setText("OFF")
            self._lm_auto_toggle.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; color: {C.TEXT_DIM};
                    border: 1px solid {C.BORDER}; border-radius: 3px;
                }}
            """)

    def _on_lm_launch(self):
        """Launch LM Studio application."""
        path = find_lmstudio_path()
        if not path:
            self._lm_install_lbl.setText("❌ LM Studio no está instalado.")
            self._lm_install_lbl.setStyleSheet(f"color: {C.RED}; background: transparent;")
            return

        success = launch_lmstudio()
        if success:
            self._lm_install_lbl.setText("✅ LM Studio iniciado. Esperando servidor...")
            self._lm_install_lbl.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
            # Wait for server then refresh
            QTimer.singleShot(1000, self._refresh_lmstudio_status)
        else:
            self._lm_install_lbl.setText("❌ Error al iniciar LM Studio.")
            self._lm_install_lbl.setStyleSheet(f"color: {C.RED}; background: transparent;")

    def _on_lm_quit(self):
        """Quit LM Studio application."""
        success = quit_lmstudio()
        if success:
            self._lm_install_lbl.setText("✅ LM Studio detenido.")
            self._lm_install_lbl.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
            QTimer.singleShot(500, self._refresh_lmstudio_status)
        else:
            self._lm_install_lbl.setText("⚠️ No se pudo detener LM Studio.")
            self._lm_install_lbl.setStyleSheet(f"color: {C.ACC}; background: transparent;")

    def _mk_sep(self) -> QFrame:
        f = QFrame(); f.setFrameShape(QFrame.Shape.HLine)
        f.setStyleSheet(f"color: {C.BORDER}; margin: 2px 0;")
        return f

    def _save_gemini_key(self):
        """Save Gemini API key to config."""
        gemini = self._gemini_key_input.text().strip()
        try:
            save_config({"gemini_api_key": gemini})
            self._gemini_status.setText("✅ Gemini key guardada")
            self._gemini_status.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
        except Exception as e:
            self._gemini_status.setText(f"❌ Error: {e}")
            self._gemini_status.setStyleSheet(f"color: {C.RED}; background: transparent;")

    def _save_openrouter_key(self):
        """Save OpenRouter API key to config."""
        openrouter = self._openrouter_key_input.text().strip()
        try:
            save_config({"openrouter_api_key": openrouter})
            self._or_status.setText("✅ OpenRouter key guardada")
            self._or_status.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
        except Exception as e:
            self._or_status.setText(f"❌ Error: {e}")
            self._or_status.setStyleSheet(f"color: {C.RED}; background: transparent;")

    def _populate_audio_devices(self):
        """Populate microphone/speaker dropdowns from sounddevice."""
        saved_mic = load_config().get("audio_input_device", None)
        saved_spk = load_config().get("audio_output_device", None)

        # Add "System Default" as the first / fallback option (stored as None)
        self._mic_combo.addItem("🎙  System Default", None)
        self._speaker_combo.addItem("🔊  System Default", None)

        _MAPPER_KEYWORDS = (
            "asignador de sonido",   # es-ES Windows mapper
            "microsoft sound mapper",
            "controlador primario",  # es-ES primary sound controller
            "primary sound",
        )

        def _is_mapper(name: str) -> bool:
            nl = name.lower()
            return any(kw in nl for kw in _MAPPER_KEYWORDS)

        try:
            devices = sd.query_devices()
            for i, dev in enumerate(devices):
                name = dev["name"]
                sr = dev.get("default_samplerate", 0)
                sr_str = f" {int(sr)}Hz" if sr else ""
                # Microphone - has input channels (skip mappers/virtual)
                if dev["max_input_channels"] > 0 and not _is_mapper(name):
                    label = f"[{i}] {name}{sr_str}"
                    self._mic_combo.addItem(label, i)
                # Speaker - has output channels (skip mappers/virtual)
                if dev["max_output_channels"] > 0 and not _is_mapper(name):
                    label = f"[{i}] {name}{sr_str}"
                    self._speaker_combo.addItem(label, i)
            # Select saved devices if found
            self._select_combo_by_data(self._mic_combo, saved_mic)
            self._select_combo_by_data(self._speaker_combo, saved_spk)
        except Exception:
            self._mic_combo.addItem("No audio devices found", -1)
            self._speaker_combo.addItem("No audio devices found", -1)

        # Connect save-on-change
        self._mic_combo.currentIndexChanged.connect(self._on_audio_dev_changed)
        self._speaker_combo.currentIndexChanged.connect(self._on_audio_dev_changed)

    def _select_combo_by_data(self, combo, data):
        """Select a QComboBox item by its user data."""
        for i in range(combo.count()):
            if combo.itemData(i) == data:
                combo.setCurrentIndex(i)
                return

    def _on_volume_changed(self, val: int):
        """Update volume label and save to config."""
        self._vol_label.setText(f"{val}%")
        try:
            save_config({"audio_volume": val})
            if hasattr(self, "_main_window") and self._main_window and hasattr(self._main_window, "_volume_slider"):
                self._main_window._volume_slider.blockSignals(True)
                self._main_window._volume_slider.setValue(val)
                self._main_window._vol_label.setText(f"{val}%")
                self._main_window._volume_slider.blockSignals(False)
        except Exception:
            pass

    def _on_audio_dev_changed(self):
        """Save selected audio devices to config."""
        try:
            mic_id = self._mic_combo.currentData()
            spk_id = self._speaker_combo.currentData()
            save_config({
                "audio_input_device": mic_id,
                "audio_output_device": spk_id,
            })
        except Exception:
            pass

    def _refresh_model_list(self):
        """Run 'ollama list' and populate the dropdown with actual installed models."""
        if not hasattr(self, '_model_combo') or not self._model_combo:
            return
        self._model_combo.blockSignals(True)
        self._model_combo.clear()
        self._reload_btn.setEnabled(False)
        self._reload_btn.setText("⏳")

        saved_model = get_model("ollama")
        models_found = 0

        try:
            r = subprocess.run(
                ["ollama", "list"],
                capture_output=True, text=True, timeout=10
            )
            if r.returncode == 0 and r.stdout.strip():
                lines = r.stdout.strip().split("\n")
                # Skip header line: NAME ID SIZE MODIFIED
                for line in lines[1:]:
                    if not line.strip():
                        continue
                    parts = line.split()
                    if parts:
                        model_id = parts[0].strip()
                        # Remove :latest suffix for cleaner display
                        display = model_id.replace(":latest", "")
                        self._model_combo.addItem(display, model_id)
                        models_found += 1
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass

        # Fallback: if no models found, add popular ones
        if models_found == 0:
            for model_id, model_name in [
                ("llama3.2", "Llama 3.2 (8B)"),
                ("llama3.1", "Llama 3.1 (70B)"),
                ("mistral", "Mistral (7B)"),
                ("phi4", "Phi-4"),
                ("deepseek-r1", "DeepSeek R1"),
                ("gemma2", "Gemma 2"),
            ]:
                self._model_combo.addItem(model_name, model_id)

        # Pre-select saved model
        for i in range(self._model_combo.count()):
            if self._model_combo.itemData(i) == saved_model or self._model_combo.itemText(i) == saved_model:
                self._model_combo.setCurrentIndex(i)
                break
        else:
            if self._model_combo.count() > 0:
                self._model_combo.setCurrentIndex(0)

        self._model_combo.blockSignals(False)
        self._reload_btn.setText("↻")
        self._reload_btn.setEnabled(True)

    def _quick_pull(self, model_id: str):
        """Quick pull a preset model in the Ollama tab."""
        self._model_combo.setCurrentText(model_id)
        self._pull_status.setText(f"⤵  Pulling {model_id}...")
        self._pull_status.setStyleSheet(f"color: {C.ACC2}; background: transparent;")
        self._pull_btn.setEnabled(False)
        try:
            cmd = f"ollama pull {model_id}"
            if _OS == "Windows":
                subprocess.Popen(["start", "cmd", "/k", cmd], shell=True, cwd=str(Path.home()))
            elif _OS == "Darwin":
                subprocess.Popen(["osascript", "-e", f'tell app "Terminal" to do script "{cmd}"'], cwd=str(Path.home()))
            else:
                subprocess.Popen(["x-terminal-emulator", "-e", cmd], cwd=str(Path.home()))
        except Exception as e:
            self._pull_status.setText(f"❌ Error: {e}")
            self._pull_status.setStyleSheet(f"color: {C.RED}; background: transparent;")
        QTimer.singleShot(3000, lambda: (
            self._pull_btn.setEnabled(True),
            self._pull_status.setText("✅ Pull started — check terminal"),
            self._pull_status.setStyleSheet(f"color: {C.GREEN}; background: transparent;"),
        ))

    def _on_pull_model(self):
        """Run ollama pull <model> in a terminal window."""
        model_id = self._model_combo.currentData()
        self._pull_status.setText(f"⬇  Pulling {model_id}...")
        self._pull_status.setStyleSheet(f"color: {C.ACC2}; background: transparent;")
        self._pull_btn.setEnabled(False)

        # Run ollama pull in a new terminal window
        try:
            cmd = f"ollama pull {model_id}"
            if _OS == "Windows":
                subprocess.Popen(
                    ["start", "cmd", "/k", cmd],
                    shell=True, cwd=str(Path.home())
                )
            elif _OS == "Darwin":
                subprocess.Popen(
                    ["osascript", "-e",
                     f'tell app "Terminal" to do script "{cmd}"'],
                    cwd=str(Path.home())
                )
            else:  # Linux
                subprocess.Popen(
                    ["x-terminal-emulator", "-e", cmd],
                    cwd=str(Path.home())
                )
        except Exception as e:
            self._pull_status.setText(f"❌ Error: {e}")
            self._pull_status.setStyleSheet(f"color: {C.RED}; background: transparent;")

        # Re-enable after a moment
        QTimer.singleShot(3000, lambda: (
            self._pull_btn.setEnabled(True),
            self._pull_status.setText("✅ Pull started — check terminal"),
            self._pull_status.setStyleSheet(f"color: {C.GREEN}; background: transparent;"),
        ))

    def _on_up_server(self):
        """Start ollama server in a terminal."""
        try:
            cmd = "ollama serve"
            if _OS == "Windows":
                subprocess.Popen(
                    ["start", "cmd", "/k", cmd],
                    shell=True, cwd=str(Path.home())
                )
            elif _OS == "Darwin":
                subprocess.Popen(
                    ["osascript", "-e",
                     f'tell app "Terminal" to do script "{cmd}"'],
                    cwd=str(Path.home())
                )
            else:
                subprocess.Popen(
                    ["x-terminal-emulator", "-e", cmd],
                    cwd=str(Path.home())
                )
            self._srv_status.setText("▲ Server starting...")
            self._srv_status.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
            QTimer.singleShot(3000, self._check_server_status)
        except Exception as e:
            self._srv_status.setText(f"❌ Error: {e}")
            self._srv_status.setStyleSheet(f"color: {C.RED}; background: transparent;")

    def _on_down_server(self):
        """Kill ollama server process."""
        try:
            if _OS == "Windows":
                subprocess.run(
                    ["taskkill", "/F", "/IM", "ollama.exe"],
                    capture_output=True, timeout=5
                )
            elif _OS == "Darwin":
                subprocess.run(["pkill", "-f", "ollama"], capture_output=True, timeout=5)
            else:
                subprocess.run(["pkill", "-f", "ollama"], capture_output=True, timeout=5)
            self._srv_status.setText("▼ Server stopped")
            self._srv_status.setStyleSheet(f"color: {C.RED}; background: transparent;")
        except Exception as e:
            self._srv_status.setText(f"❌ Error: {e}")
            self._srv_status.setStyleSheet(f"color: {C.RED}; background: transparent;")

    def _check_server_status(self):
        """Check if ollama server is running and update the status label."""
        try:
            if _OS == "Windows":
                r = subprocess.run(
                    ["tasklist", "/FI", "IMAGENAME eq ollama.exe"],
                    capture_output=True, text=True, timeout=3
                )
                if "ollama.exe" in r.stdout:
                    self._srv_status.setText("●  Server: RUNNING")
                    self._srv_status.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
                    return
            else:
                r = subprocess.run(
                    ["pgrep", "-f", "ollama"], capture_output=True, timeout=3
                )
                if r.returncode == 0:
                    self._srv_status.setText("●  Server: RUNNING")
                    self._srv_status.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
                    return
            self._srv_status.setText("○  Server: STOPPED")
            self._srv_status.setStyleSheet(f"color: {C.TEXT_DIM}; background: transparent;")
        except Exception:
            self._srv_status.setText("○  Server: unknown")
            self._srv_status.setStyleSheet(f"color: {C.TEXT_DIM}; background: transparent;")
