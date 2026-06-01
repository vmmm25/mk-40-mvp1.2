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


# ÔöÇÔöÇ Shared OpenRouter free-model catalogue ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ
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


# ÔöÇÔöÇ Shared style sheets ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ
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

        # ÔöÇÔöÇ Settings Tab Widget (Pure Static Panel) ÔöÇÔöÇ
        self._settings_tabs = QTabWidget()
        self._settings_tabs.setStyleSheet(_TAB_STYLE)
        
        # We use compact labels to fit beautifully in 340px
        self._settings_tabs.addTab(self._build_gemini_tab(), "­ƒºá GEM")
        self._settings_tabs.addTab(self._build_openrouter_tab(), "­ƒöù OR")
        self._settings_tabs.addTab(self._build_ollama_tab(), "­ƒñû OLL")
        self._settings_tabs.addTab(self._build_lmstudio_tab(), "­ƒƒá LM")
        self._settings_tabs.addTab(self._build_audio_tab(), "­ƒÄÖ VOZ")
        
        self._main_layout.addWidget(self._settings_tabs)

    def update_status(self, provider: str):
        """No-op status updater, compatibility fallback."""
        pass

    def _on_provider_clicked(self, provider: str):
        """Emit provider signal, compatibility fallback."""
        self.provider_changed.emit(provider)

    # ÔöÇÔöÇ Tab: Gemini ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ
    def _build_gemini_tab(self) -> QWidget:
        w = QWidget(); lay = QVBoxLayout(w)
        lay.setContentsMargins(60, 20, 60, 20)
        lay.setSpacing(10)

        lay.addStretch()
        lay.addWidget(self._build_lbl("🔑  GEMINI API KEY", 10, True, C.ACC, align=Qt.AlignmentFlag.AlignCenter))
        lay.addWidget(self._build_lbl(
            "Requerida para el reconocimiento de voz (Cloud STT).\n"
            "Consíguela gratis en aistudio.google.com",
            8, color=C.TEXT_DIM, align=Qt.AlignmentFlag.AlignCenter
        ))
        lay.addSpacing(10)

        cfg = load_config()
        self._gemini_key_input = QLineEdit()
        self._gemini_key_input.setFont(QFont("Segoe UI", 11))
        self._gemini_key_input.setFixedHeight(32)
        self._gemini_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._gemini_key_input.setText(cfg.get("gemini_api_key", ""))
        self._gemini_key_input.setStyleSheet(_INPUT_STYLE)
        lay.addWidget(self._gemini_key_input)

        save_row = QHBoxLayout(); save_row.setSpacing(15)
        self._save_gemini_btn = self._build_btn("GUARDAR", C.GREEN, h=30, w=120)
        self._save_gemini_btn.clicked.connect(self._save_gemini_key)
        self._gemini_status = self._build_lbl("", 8, color=C.TEXT_DIM)
        save_row.addStretch()
        save_row.addWidget(self._save_gemini_btn)
        save_row.addWidget(self._gemini_status)
        save_row.addStretch()
        lay.addLayout(save_row)

        lay.addStretch()
        return w

    # ÔöÇÔöÇ Tab: OpenRouter ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ
    def _build_openrouter_tab(self) -> QWidget:
        w = QWidget(); lay = QVBoxLayout(w)
        lay.setContentsMargins(60, 10, 60, 10)
        lay.setSpacing(8)

        lay.addWidget(self._build_lbl("🔑  OPENROUTER API KEY", 10, True, C.ACC, align=Qt.AlignmentFlag.AlignCenter))
        lay.addWidget(self._build_lbl(
            "Requerida para modelos en la nube. Consíguela en openrouter.ai/keys",
            8, color=C.TEXT_DIM, align=Qt.AlignmentFlag.AlignCenter
        ))

        cfg = load_config()
        self._openrouter_key_input = QLineEdit()
        self._openrouter_key_input.setFont(QFont("Segoe UI", 11))
        self._openrouter_key_input.setFixedHeight(32)
        self._openrouter_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._openrouter_key_input.setText(cfg.get("openrouter_api_key", ""))
        self._openrouter_key_input.setStyleSheet(_INPUT_STYLE)
        lay.addWidget(self._openrouter_key_input)

        save_row = QHBoxLayout(); save_row.setSpacing(15)
        self._save_or_btn = self._build_btn("GUARDAR", C.GREEN, h=30, w=120)
        self._save_or_btn.clicked.connect(self._save_openrouter_key)
        self._or_status = self._build_lbl("", 8, color=C.TEXT_DIM)
        save_row.addStretch()
        save_row.addWidget(self._save_or_btn)
        save_row.addWidget(self._or_status)
        save_row.addStretch()
        lay.addLayout(save_row)

        lay.addWidget(self._mk_sep())

        lay.addWidget(self._build_lbl("📦  FREE MODELS (OpenRouter)", 9, True, C.GREEN, align=Qt.AlignmentFlag.AlignCenter))
        self._or_model_combo = QComboBox()
        self._or_model_combo.setFont(QFont("Segoe UI", 11))
        self._or_model_combo.setFixedHeight(30)
        self._or_model_combo.setStyleSheet(_COMBO_STYLE)
        _populate_or_combo(self._or_model_combo, get_model("openrouter"))
        lay.addWidget(self._or_model_combo)

        save_model_row = QHBoxLayout(); save_model_row.setSpacing(15)
        self._save_or_model_btn = self._build_btn("GUARDAR MODELO", C.GREEN, h=30, w=140)
        self._save_or_model_btn.clicked.connect(self._save_or_model)
        self._or_model_status = self._build_lbl("", 8, color=C.TEXT_DIM)
        save_model_row.addStretch()
        save_model_row.addWidget(self._save_or_model_btn)
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
            self._or_model_status.setText(f"Ô£à Guardado: {model_id.split('/')[1].split(':')[0]}")
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
            self._or_model_status.setText("ÔØî No se seleccion├│ modelo")
            self._or_model_status.setStyleSheet(f"color: {C.RED}; background: transparent;")

    # ÔöÇÔöÇ Tab: Audio Settings ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ
    def _build_audio_tab(self) -> QWidget:
        w = QWidget(); lay = QVBoxLayout(w)
        lay.setContentsMargins(20, 10, 20, 10)
        lay.setSpacing(10)
        
        # Sub-tabs for Voice Settings
        self._voice_tabs = QTabWidget()
        self._voice_tabs.setStyleSheet(_TAB_STYLE)
        
        # 1. Hardware Tab
        hw_w = QWidget(); hw_lay = QVBoxLayout(hw_w)
        hw_lay.addWidget(self._build_lbl("🎙 DISPOSITIVOS", 9, True, C.PRI, align=Qt.AlignmentFlag.AlignCenter))
        
        cfg = load_config()
        self._mic_combo = QComboBox()
        self._speaker_combo = QComboBox()
        for combo in (self._mic_combo, self._speaker_combo):
            combo.setFont(QFont("Segoe UI", 10))
            combo.setFixedHeight(28)
            combo.setStyleSheet(_COMBO_STYLE)
            
        mic_row = QHBoxLayout()
        mic_row.addWidget(self._build_lbl("Input:", 8, color=C.TEXT_MED))
        mic_row.addWidget(self._mic_combo, stretch=1)
        hw_lay.addLayout(mic_row)
        
        spk_row = QHBoxLayout()
        spk_row.addWidget(self._build_lbl("Output:", 8, color=C.TEXT_MED))
        spk_row.addWidget(self._speaker_combo, stretch=1)
        hw_lay.addLayout(spk_row)
        
        hw_lay.addWidget(self._mk_sep())
        
        hw_lay.addWidget(self._build_lbl("🔊 VOLUMEN", 9, True, C.PRI, align=Qt.AlignmentFlag.AlignCenter))
        vol_val = cfg.get("audio_volume", 100)
        self._vol_label = self._build_lbl(f"{vol_val}%", 11, True, C.TEXT_MED, align=Qt.AlignmentFlag.AlignCenter)
        hw_lay.addWidget(self._vol_label)
        
        self._vol_slider = QSlider(Qt.Orientation.Horizontal)
        self._vol_slider.setRange(0, 100)
        self._vol_slider.setValue(vol_val)
        self._vol_slider.valueChanged.connect(self._on_volume_changed)
        hw_lay.addWidget(self._vol_slider)
        hw_lay.addStretch()
        
        # 2. Gemini Tab
        gem_w = QWidget(); gem_lay = QVBoxLayout(gem_w)
        gem_lay.addWidget(self._build_lbl("☁️ GEMINI VOICE (Cloud)", 10, True, C.ACC, align=Qt.AlignmentFlag.AlignCenter))
        gem_lay.addWidget(self._build_lbl("Gemini sirve como 'Oído' (STT) ultrarrápido y como 'Voz' (TTS).", 8, color=C.TEXT_DIM, align=Qt.AlignmentFlag.AlignCenter))
        gem_lay.addStretch()
        
        # 3. Whisper Tab
        wsp_w = QWidget(); wsp_lay = QVBoxLayout(wsp_w)
        wsp_lay.addWidget(self._build_lbl("🧠 WHISPER (Local STT)", 10, True, C.GREEN, align=Qt.AlignmentFlag.AlignCenter))
        wsp_lay.addWidget(self._build_lbl("Motor de Escucha Offline. Requiere descargar modelo local.", 8, color=C.TEXT_DIM, align=Qt.AlignmentFlag.AlignCenter))
        
        wp_row = QHBoxLayout()
        self._whisper_path_edit = QLineEdit(cfg.get("whisper_path", ""))
        self._whisper_path_edit.setStyleSheet(_INPUT_STYLE); self._whisper_path_edit.setPlaceholderText("Ejecutable Whisper.cpp")
        self._whisper_path_btn = self._build_btn("...", C.PRI, h=24, w=30)
        self._whisper_path_btn.clicked.connect(self._browse_whisper_path)
        wp_row.addWidget(self._whisper_path_edit, stretch=1); wp_row.addWidget(self._whisper_path_btn)
        wsp_lay.addLayout(wp_row)
        
        wm_row = QHBoxLayout()
        self._whisper_model_edit = QLineEdit(cfg.get("whisper_model", ""))
        self._whisper_model_edit.setStyleSheet(_INPUT_STYLE); self._whisper_model_edit.setPlaceholderText("Archivo de modelo .bin")
        self._whisper_model_btn = self._build_btn("...", C.PRI, h=24, w=30)
        self._whisper_model_btn.clicked.connect(self._browse_whisper_model)
        wm_row.addWidget(self._whisper_model_edit, stretch=1); wm_row.addWidget(self._whisper_model_btn)
        wsp_lay.addLayout(wm_row)
        wsp_lay.addStretch()
        
        # 4. Piper Tab
        pip_w = QWidget(); pip_lay = QVBoxLayout(pip_w)
        pip_lay.addWidget(self._build_lbl("🗣️ PIPER (Local TTS)", 10, True, C.PRI, align=Qt.AlignmentFlag.AlignCenter))
        pip_lay.addWidget(self._build_lbl("Motor de Habla Offline. Sintetiza voz localmente sin internet.", 8, color=C.TEXT_DIM, align=Qt.AlignmentFlag.AlignCenter))
        
        pp_row = QHBoxLayout()
        self._piper_path_edit = QLineEdit(cfg.get("piper_path", ""))
        self._piper_path_edit.setStyleSheet(_INPUT_STYLE); self._piper_path_edit.setPlaceholderText("Ejecutable Piper")
        self._piper_path_btn = self._build_btn("...", C.PRI, h=24, w=30)
        self._piper_path_btn.clicked.connect(self._browse_piper_path)
        pp_row.addWidget(self._piper_path_edit, stretch=1); pp_row.addWidget(self._piper_path_btn)
        pip_lay.addLayout(pp_row)
        
        pm_row = QHBoxLayout()
        self._piper_model_edit = QLineEdit(cfg.get("piper_model", ""))
        self._piper_model_edit.setStyleSheet(_INPUT_STYLE); self._piper_model_edit.setPlaceholderText("Archivo de modelo .onnx")
        self._piper_model_btn = self._build_btn("...", C.PRI, h=24, w=30)
        self._piper_model_btn.clicked.connect(self._browse_piper_model)
        pm_row.addWidget(self._piper_model_edit, stretch=1); pm_row.addWidget(self._piper_model_btn)
        pip_lay.addLayout(pm_row)
        pip_lay.addStretch()
        
        self._voice_tabs.addTab(hw_w, "🎛️ HARDWARE")
        self._voice_tabs.addTab(gem_w, "☁️ GEMINI")
        self._voice_tabs.addTab(wsp_w, "🧠 WHISPER")
        self._voice_tabs.addTab(pip_w, "🗣️ PIPER")
        
        lay.addWidget(self._voice_tabs, stretch=1)
        
        # Engine Selection Global
        eng_lay = QHBoxLayout(); eng_lay.setSpacing(10)
        
        eng_lay.addWidget(self._build_lbl("Motor STT (Oído):", 9, True, C.TEXT_MED))
        self._stt_engine_combo = QComboBox()
        self._stt_engine_combo.setFont(QFont("Segoe UI", 10))
        self._stt_engine_combo.setFixedHeight(28)
        self._stt_engine_combo.setStyleSheet(_COMBO_STYLE)
        self._stt_engine_combo.addItem("Gemini Cloud", "gemini")
        self._stt_engine_combo.addItem("Whisper Local", "whisper")
        self._select_combo_by_data(self._stt_engine_combo, cfg.get("stt_engine", "gemini"))
        eng_lay.addWidget(self._stt_engine_combo)
        
        eng_lay.addWidget(self._build_lbl("Motor TTS (Voz):", 9, True, C.TEXT_MED))
        self._tts_engine_combo = QComboBox()
        self._tts_engine_combo.setFont(QFont("Segoe UI", 10))
        self._tts_engine_combo.setFixedHeight(28)
        self._tts_engine_combo.setStyleSheet(_COMBO_STYLE)
        self._tts_engine_combo.addItem("Gemini Cloud", "gemini")
        self._tts_engine_combo.addItem("Piper Local", "piper")
        self._select_combo_by_data(self._tts_engine_combo, cfg.get("tts_engine", "piper"))
        eng_lay.addWidget(self._tts_engine_combo)
        
        lay.addLayout(eng_lay)
        
        # Save Voice Settings
        save_row = QHBoxLayout()
        save_row.addStretch()
        self._voice_enabled_chk = QCheckBox(" Activar Voz de Jarvis (Global)")
        self._voice_enabled_chk.setStyleSheet(f"color: {C.TEXT_MED}; font-weight: bold;")
        self._voice_enabled_chk.setChecked(cfg.get("voice_wrapper_enabled", False))
        save_row.addWidget(self._voice_enabled_chk)
        
        self._save_voice_btn = self._build_btn("GUARDAR AJUSTES", C.GREEN, h=30)
        self._save_voice_btn.clicked.connect(self._on_voice_settings_changed)
        save_row.addWidget(self._save_voice_btn)
        save_row.addStretch()
        lay.addLayout(save_row)
        
        self._populate_audio_devices()
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

    # ÔöÇÔöÇ Tab: Ollama Tools + Commands ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ
    def _build_ollama_tab(self) -> QWidget:
        w = QWidget(); lay = QVBoxLayout(w)
        lay.setContentsMargins(50, 10, 50, 10)
        lay.setSpacing(12)

        lay.addWidget(self._build_lbl("🦙  OLLAMA LOCAL MODELS", 10, True, C.ACC2, align=Qt.AlignmentFlag.AlignCenter))
        lay.addWidget(self._build_lbl("Gestiona tus modelos de IA locales. Ollama se iniciará automáticamente.", 8, color=C.TEXT_DIM, align=Qt.AlignmentFlag.AlignCenter))
        lay.addSpacing(5)

        # Combo and Refresh
        combo_row = QHBoxLayout(); combo_row.setSpacing(10)
        self._model_combo = QComboBox()
        self._model_combo.setEditable(True)
        self._model_combo.setFont(QFont("Segoe UI", 12))
        self._model_combo.setFixedHeight(34)
        self._model_combo.setStyleSheet(_COMBO_STYLE)
        combo_row.addWidget(self._model_combo, stretch=1)

        self._reload_btn = self._build_btn("↻", C.PRI, h=34, w=38, bold=True)
        self._reload_btn.setToolTip("Refresh model list")
        self._reload_btn.clicked.connect(self._refresh_model_list)
        combo_row.addWidget(self._reload_btn)

        self._run_btn = self._build_btn("▶ RUN", C.GREEN, h=34, w=90)
        self._run_btn.clicked.connect(self._save_ollama_model)
        combo_row.addWidget(self._run_btn)
        
        self._pull_btn = self._build_btn("⬇ PULL", C.PRI, h=34, w=90)
        self._pull_btn.clicked.connect(self._on_pull_model)
        combo_row.addWidget(self._pull_btn)
        lay.addLayout(combo_row)

        # Pull status
        self._pull_status = self._build_lbl("Listo para usar", 8, color=C.TEXT_DIM, align=Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self._pull_status)
        
        lay.addWidget(self._mk_sep())
        
        # Presets
        presets_lay = QVBoxLayout(); presets_lay.setSpacing(6)
        
        # Open Folder
        folder_row = QHBoxLayout()
        folder_row.addStretch()
        self._open_ollama_btn = self._build_btn("📁 CARPETA MODELOS", C.PRI, h=26, bold=False)
        self._open_ollama_btn.clicked.connect(self._open_ollama_models_folder)
        folder_row.addWidget(self._open_ollama_btn)
        folder_row.addStretch()
        lay.addLayout(folder_row)
        
        presets_lay.addWidget(self._build_lbl("Quick Run (Recomendados):", 8, color=C.TEXT_MED, align=Qt.AlignmentFlag.AlignCenter))
        p_row = QHBoxLayout(); p_row.setSpacing(8)
        p_row.addStretch()
        for mid, mname in [("llama3.2", "Llama 3.2"), ("mistral", "Mistral"), ("phi4", "Phi-4"), ("deepseek-r1", "DeepSeek")]:
            b = self._build_btn(mname, C.ACC2, h=26, bold=False)
            b.clicked.connect(lambda checked, m=mid: self._quick_run(m))
            p_row.addWidget(b)
        p_row.addStretch()
        presets_lay.addLayout(p_row)
        lay.addLayout(presets_lay)
        
        lay.addSpacing(5)
        
        # Server Control
        s_row = QHBoxLayout(); s_row.setSpacing(8)
        s_row.addStretch()
        s_row.addWidget(self._build_lbl("Server:", 8, color=C.TEXT_MED))
        self._up_btn = self._build_btn("▶ UP", C.GREEN, h=24)
        self._up_btn.clicked.connect(self._on_up_server)
        self._down_btn = self._build_btn("⏹ DOWN", C.RED, h=24)
        self._down_btn.clicked.connect(self._on_down_server)
        s_row.addWidget(self._up_btn)
        s_row.addWidget(self._down_btn)
        
        self._srv_status = self._build_lbl("checking...", 8, color=C.TEXT_DIM)
        s_row.addWidget(self._srv_status)
        s_row.addStretch()
        lay.addLayout(s_row)
        
        lay.addStretch()

        self._refresh_model_list()
        self._check_server_status()
        return w

    # ÔöÇÔöÇ Tab: LM Studio ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ
    def _build_lmstudio_tab(self) -> QWidget:
        w = QWidget(); lay = QVBoxLayout(w)
        lay.setContentsMargins(40, 10, 40, 10)
        lay.setSpacing(10)

        lay.addWidget(self._build_lbl("🖥  LM STUDIO SERVER", 10, True, C.ACC, align=Qt.AlignmentFlag.AlignCenter))
        self._lm_path_lbl = self._build_lbl("Buscando instalación...", 8, color=C.TEXT_DIM, align=Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self._lm_path_lbl)
        
        url_row = QHBoxLayout(); url_row.setSpacing(8)
        url_row.addWidget(self._build_lbl("URL:", 9, True, C.TEXT_MED))
        cfg = load_config()
        self._lm_url_input = QLineEdit()
        self._lm_url_input.setFont(QFont("Segoe UI", 11))
        self._lm_url_input.setFixedHeight(30)
        self._lm_url_input.setText(cfg.get("lmstudio_url", "http://localhost:1234"))
        self._lm_url_input.setStyleSheet(_INPUT_STYLE)
        url_row.addWidget(self._lm_url_input, stretch=1)
        
        self._save_lm_url_btn = self._build_btn("✓", C.GREEN, h=30, w=32)
        self._save_lm_url_btn.clicked.connect(self._save_lmstudio_url)
        url_row.addWidget(self._save_lm_url_btn)
        lay.addLayout(url_row)
        
        ctrl_row = QHBoxLayout(); ctrl_row.setSpacing(10)
        ctrl_row.addStretch()
        self._lm_launch_btn = self._build_btn("▶ LAUNCH", C.GREEN, h=28)
        self._lm_launch_btn.clicked.connect(self._on_lm_launch)
        self._lm_quit_btn = self._build_btn("⏹ QUIT", C.RED, h=28)
        self._lm_quit_btn.clicked.connect(self._on_lm_quit)
        ctrl_row.addWidget(self._lm_launch_btn)
        ctrl_row.addWidget(self._lm_quit_btn)
        
        self._lm_auto_toggle = self._build_btn("AUTO: ON", C.GREEN, h=28)
        self._lm_auto_toggle.clicked.connect(self._toggle_lm_auto)
        self._update_lm_auto_btn(cfg.get("lmstudio_auto_launch", True))
        ctrl_row.addWidget(self._lm_auto_toggle)
        
        self._lm_server_lbl = self._build_lbl("● Server: checking...", 9, True, C.TEXT_DIM)
        self._lm_refresh_btn = self._build_btn("↻", C.PRI, h=28, w=30)
        self._lm_refresh_btn.clicked.connect(self._refresh_lmstudio_status)
        ctrl_row.addWidget(self._lm_server_lbl)
        ctrl_row.addWidget(self._lm_refresh_btn)
        ctrl_row.addStretch()
        lay.addLayout(ctrl_row)
        
        self._lm_install_lbl = self._build_lbl("", 8, color=C.TEXT_DIM, align=Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self._lm_install_lbl)

        lay.addWidget(self._mk_sep())
        
        lay.addWidget(self._build_lbl("📦  MODEL SELECTION", 9, True, C.ACC, align=Qt.AlignmentFlag.AlignCenter))
        self._lm_model_combo = QComboBox()
        self._lm_model_combo.setFont(QFont("Segoe UI", 11))
        self._lm_model_combo.setFixedHeight(30)
        self._lm_model_combo.setStyleSheet(_COMBO_STYLE)
        lay.addWidget(self._lm_model_combo)
        
        model_action_row = QHBoxLayout()
        model_action_row.addStretch()
        self._save_lm_model_btn = self._build_btn("GUARDAR MODELO", C.GREEN, h=30)
        self._save_lm_model_btn.clicked.connect(self._save_lm_model)
        self._lm_refresh_models_btn = self._build_btn("↻ SCAN", C.ACC, h=30)
        self._lm_folder_btn = self._build_btn("📁 CARPETA", C.PRI, h=30)
        self._lm_folder_btn.clicked.connect(self._open_lm_models_folder)
        model_action_row.addWidget(self._lm_folder_btn)
        self._lm_refresh_models_btn.clicked.connect(self._populate_lm_models)
        model_action_row.addWidget(self._save_lm_model_btn)
        model_action_row.addWidget(self._lm_refresh_models_btn)
        
        self._lm_model_status = self._build_lbl("", 8, color=C.TEXT_DIM)
        model_action_row.addWidget(self._lm_model_status)
        model_action_row.addStretch()
        lay.addLayout(model_action_row)

        lay.addStretch()

        self._check_lmstudio_path()
        self._refresh_lmstudio_status()
        self._populate_lm_models()
        return w

    def _check_lmstudio_path(self):
        """Find LM Studio installation and update UI."""
        path = find_lmstudio_path()
        if path:
            self._lm_path_lbl.setText(f"Ô£à Instalado en: {path.parent}")
            self._lm_path_lbl.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
        else:
            self._lm_path_lbl.setText("ÔÜá´©Å LM Studio no encontrado. Inst├ílalo desde lmstudio.ai")
            self._lm_path_lbl.setStyleSheet(f"color: {C.RED}; background: transparent;")

    def _refresh_lmstudio_status(self):
        """Check LM Studio server status and update UI."""
        running = is_server_running()
        if running:
            self._lm_server_lbl.setText("ÔùÅ  Server: RUNNING")
            self._lm_server_lbl.setStyleSheet(f"color: {C.GREEN}; background: transparent; padding: 2px 0;")
        else:
            self._lm_server_lbl.setText("ÔùÅ  Server: OFFLINE")
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
            self._lm_model_status.setText(f"­ƒôª {count} modelo(s) encontrado(s)")
            self._lm_model_status.setStyleSheet(f"color: {C.TEXT_MED}; background: transparent;")
        else:
            self._lm_model_status.setText("ÔÜá´©Å No se encontraron modelos locales")
            self._lm_model_status.setStyleSheet(f"color: {C.RED}; background: transparent;")

    def _save_lm_model(self):
        """Save LM Studio model selection, sync right-panel, restart engine."""
        model_id = self._lm_model_combo.currentData()
        if model_id:
            set_model(model_id, "lmstudio")
            short_name = model_id.split("/")[-1].split(":")[0]
            self._lm_model_status.setText(f"Ô£à Guardado: {short_name}")
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
            self._lm_model_status.setText("ÔØî No se seleccion├│ modelo")
            self._lm_model_status.setStyleSheet(f"color: {C.RED}; background: transparent;")

    def _save_lmstudio_url(self):
        """Save LM Studio URL to config."""
        url = self._lm_url_input.text().strip()
        if url:
            save_config({"lmstudio_url": url})
            self._save_lm_url_btn.setText("Ô£ô")
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
            self._lm_install_lbl.setText("ÔØî LM Studio no est├í instalado.")
            self._lm_install_lbl.setStyleSheet(f"color: {C.RED}; background: transparent;")
            return

        success = launch_lmstudio()
        if success:
            self._lm_install_lbl.setText("Ô£à LM Studio iniciado. Esperando servidor...")
            self._lm_install_lbl.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
            # Wait for server then refresh
            QTimer.singleShot(1000, self._refresh_lmstudio_status)
        else:
            self._lm_install_lbl.setText("ÔØî Error al iniciar LM Studio.")
            self._lm_install_lbl.setStyleSheet(f"color: {C.RED}; background: transparent;")

    def _on_lm_quit(self):
        """Quit LM Studio application."""
        success = quit_lmstudio()
        if success:
            self._lm_install_lbl.setText("Ô£à LM Studio detenido.")
            self._lm_install_lbl.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
            QTimer.singleShot(500, self._refresh_lmstudio_status)
        else:
            self._lm_install_lbl.setText("ÔÜá´©Å No se pudo detener LM Studio.")
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
            self._gemini_status.setText("Ô£à Gemini key guardada")
            self._gemini_status.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
        except Exception as e:
            self._gemini_status.setText(f"ÔØî Error: {e}")
            self._gemini_status.setStyleSheet(f"color: {C.RED}; background: transparent;")

    def _save_openrouter_key(self):
        """Save OpenRouter API key to config."""
        openrouter = self._openrouter_key_input.text().strip()
        try:
            save_config({"openrouter_api_key": openrouter})
            self._or_status.setText("Ô£à OpenRouter key guardada")
            self._or_status.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
        except Exception as e:
            self._or_status.setText(f"ÔØî Error: {e}")
            self._or_status.setStyleSheet(f"color: {C.RED}; background: transparent;")

    def _populate_audio_devices(self):
        """Populate microphone/speaker dropdowns from sounddevice."""
        saved_mic = load_config().get("audio_input_device", None)
        saved_spk = load_config().get("audio_output_device", None)

        # Add "System Default" as the first / fallback option (stored as None)
        self._mic_combo.addItem("­ƒÄÖ  System Default", None)
        self._speaker_combo.addItem("­ƒöè  System Default", None)

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
        self._reload_btn.setText("ÔÅ│")

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
        self._reload_btn.setText("Ôå╗")
        self._reload_btn.setEnabled(True)


    def _save_ollama_model(self):
        model_id = self._model_combo.currentData() or self._model_combo.currentText()
        if model_id:
            set_model(model_id, "ollama")
            self._pull_status.setText(f"✅ Guardado: {model_id}")
            self._pull_status.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
            # Sync right-panel if needed
            if hasattr(self, '_main_win') and self._main_win:
                right_combo = self._main_win._right_model_combo
                # If the provider is ollama, we update the combo
                cfg = load_config()
                provider = cfg.get("selected_provider", "gemini")
                if provider == "ollama":
                    for i in range(right_combo.count()):
                        if right_combo.itemData(i) == model_id or right_combo.itemText(i) == model_id:
                            right_combo.setCurrentIndex(i)
                            break
                    if hasattr(self._main_win, '_on_provider_changed') and self._main_win._on_provider_changed:
                        self._main_win._on_provider_changed(provider)


    def _open_folder(self, path: str):
        import os, subprocess, platform
        from pathlib import Path
        p = Path(path).expanduser()
        if p.exists():
            if platform.system() == "Windows":
                os.startfile(p)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", str(p)])
            else:
                subprocess.Popen(["xdg-open", str(p)])
        else:
            print(f"[JARVIS] Carpeta no encontrada: {p}")

    def _open_ollama_models_folder(self):
        import platform
        if platform.system() == "Windows":
            path = "~/.ollama/models"
        elif platform.system() == "Darwin":
            path = "~/.ollama/models"
        else:
            path = "/usr/share/ollama/.ollama/models"
        self._open_folder(path)

    def _open_lm_models_folder(self):
        self._open_folder("~/.cache/lm-studio/models")

    def _quick_run(self, model_id: str):
        # Selecciona el modelo si está en la lista o lo agrega
        found = False
        for i in range(self._model_combo.count()):
            if self._model_combo.itemData(i) == model_id or self._model_combo.itemText(i) == model_id:
                self._model_combo.setCurrentIndex(i)
                found = True
                break
        if not found:
            self._model_combo.addItem(model_id, model_id)
            self._model_combo.setCurrentIndex(self._model_combo.count() - 1)
            
        self._save_ollama_model()

    def _quick_pull(self, model_id: str):
        """Quick pull a preset model in the Ollama tab."""
        self._model_combo.setCurrentText(model_id)
        self._pull_status.setText(f"ÔñÁ  Pulling {model_id}...")
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
            self._pull_status.setText(f"ÔØî Error: {e}")
            self._pull_status.setStyleSheet(f"color: {C.RED}; background: transparent;")
        QTimer.singleShot(3000, lambda: (
            self._pull_btn.setEnabled(True),
            self._pull_status.setText("Ô£à Pull started ÔÇö check terminal"),
            self._pull_status.setStyleSheet(f"color: {C.GREEN}; background: transparent;"),
        ))

    def _on_pull_model(self):
        """Run ollama pull <model> in a terminal window."""
        model_id = self._model_combo.currentData()
        self._pull_status.setText(f"Ô¼ç  Pulling {model_id}...")
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
            self._pull_status.setText(f"ÔØî Error: {e}")
            self._pull_status.setStyleSheet(f"color: {C.RED}; background: transparent;")

        # Re-enable after a moment
        QTimer.singleShot(3000, lambda: (
            self._pull_btn.setEnabled(True),
            self._pull_status.setText("Ô£à Pull started ÔÇö check terminal"),
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
            self._srv_status.setText("Ôû▓ Server starting...")
            self._srv_status.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
            QTimer.singleShot(3000, self._check_server_status)
        except Exception as e:
            self._srv_status.setText(f"ÔØî Error: {e}")
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
            self._srv_status.setText("Ôû╝ Server stopped")
            self._srv_status.setStyleSheet(f"color: {C.RED}; background: transparent;")
        except Exception as e:
            self._srv_status.setText(f"ÔØî Error: {e}")
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
                    self._srv_status.setText("ÔùÅ  Server: RUNNING")
                    self._srv_status.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
                    return
            else:
                r = subprocess.run(
                    ["pgrep", "-f", "ollama"], capture_output=True, timeout=3
                )
                if r.returncode == 0:
                    self._srv_status.setText("ÔùÅ  Server: RUNNING")
                    self._srv_status.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
                    return
            self._srv_status.setText("Ôùï  Server: STOPPED")
            self._srv_status.setStyleSheet(f"color: {C.TEXT_DIM}; background: transparent;")
        except Exception:
            self._srv_status.setText("Ôùï  Server: unknown")
            self._srv_status.setStyleSheet(f"color: {C.TEXT_DIM}; background: transparent;")
