"""
SettingsPanel — Right-side configuration panel with collapsible sections.

Replaces the old QTabWidget-based ConfigToolbar with an always-visible
scrollable panel containing accordion sections for all settings.
"""
from __future__ import annotations

import os
import platform
import subprocess
import json
from pathlib import Path

import sounddevice as sd

from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSlider, QVBoxLayout, QWidget, QScrollArea,
    QCheckBox, QFileDialog, QSizePolicy,
)

from ui.theme import Theme as C, PROVIDER_COLORS
from ui.components.collapsible_section import CollapsibleSection
from memory.config_manager import load_config, save_config, get_model, set_model
from core.model_registry import badged_name
from providers.lmstudio_control import (
    find_lmstudio_path, find_lms_cli_path, get_downloaded_models,
    launch_lmstudio, quit_lmstudio,
    is_server_running, load_model, unload_model,
)

_OS = platform.system()

# ── Shared styles ──
_INPUT_STYLE = (
    "QLineEdit { background: #000d14; color: #d8f8ff; border: 1px solid #0d3347;"
    " border-radius: 8px; padding: 2px 6px; font-size: 10pt; }"
    "QLineEdit:focus { border: 1px solid #00d4ff; }"
)
_COMBO_STYLE = (
    "QComboBox { background: #000d12; color: #8ffcff;"
    " border: 1px solid #0d3347; border-radius: 8px; padding: 2px 6px; font-size: 9pt; }"
    "QComboBox:hover { border: 1px solid #1a5c7a; }"
    "QComboBox::drop-down { border: none; width: 18px; }"
    "QComboBox QAbstractItemView { background: #000d12; color: #8ffcff;"
    " border: 1px solid #0d3347; selection-background-color: #007a99; }"
)

# Re-export for chat_bar.py backward compatibility
from ui.config_toolbar import _OR_FREE_MODELS, _populate_or_combo


class SettingsPanel(QWidget):
    """Right-side settings panel with collapsible accordion sections."""

    provider_changed = pyqtSignal(str)

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self._main_win = main_window
        self.setMinimumWidth(280)
        self.setMaximumWidth(380)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        self.setStyleSheet(f"""
            QWidget {{ background: {C.DARK}; }}
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Panel header
        header = QWidget()
        header.setFixedHeight(30)
        header.setStyleSheet(f"background: {C.PANEL}; border-bottom: 1px solid {C.BORDER};")
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(10, 0, 10, 0)
        title = QLabel("⚙  CONFIGURATION")
        title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {C.PRI}; background: transparent;")
        h_lay.addWidget(title)
        h_lay.addStretch()
        outer.addWidget(header)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{ border: none; background: {C.DARK}; }}
            QScrollBar:vertical {{
                background: {C.DARK}; width: 6px; margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {C.BORDER}; border-radius: 3px; min-height: 30px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)

        container = QWidget()
        self._container_layout = QVBoxLayout(container)
        self._container_layout.setContentsMargins(4, 4, 4, 4)
        self._container_layout.setSpacing(2)

        # Build sections
        self._build_api_providers_section()
        self._build_local_providers_section()
        self._build_local_settings_section()
        self._build_mcp_section()
        self._build_skills_section()
        self._build_agents_section()
        self._build_tasks_section()

        self._container_layout.addStretch()
        scroll.setWidget(container)
        outer.addWidget(scroll)

    # ── Helpers ──────────────────────────────────────────────────────

    def _lbl(self, txt, sz=9, bold=False, color=None, align=None):
        w = QLabel(txt)
        if align:
            w.setAlignment(align)
        w.setFont(QFont("Segoe UI", sz, QFont.Weight.Bold if bold else QFont.Weight.Normal))
        w.setStyleSheet(f"color: {color or C.TEXT_DIM}; background: transparent;")
        w.setWordWrap(True)
        return w

    def _btn(self, txt, color=C.PRI, h=26, w=None, bold=True):
        btn = QPushButton(txt)
        btn.setFont(QFont("Segoe UI", 8 if not bold else 9, QFont.Weight.Bold if bold else QFont.Weight.Normal))
        if w:
            btn.setFixedWidth(w)
        btn.setFixedHeight(h)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {C.DARK}; color: {color};
                border: 1px solid {C.BORDER}; border-radius: 8px; padding: 1px 8px;
            }}
            QPushButton:hover {{
                background: {color}22; border: 1px solid {color};
            }}
            QPushButton:pressed {{ background: {color}44; }}
        """)
        return btn

    def _sep(self):
        f = QFrame()
        f.setFrameShape(QFrame.Shape.HLine)
        f.setFixedHeight(1)
        f.setStyleSheet(f"background: {C.BORDER}; border: none; margin: 2px 0;")
        return f

    def _combo(self):
        c = QComboBox()
        c.setFont(QFont("Segoe UI", 9))
        c.setFixedHeight(26)
        c.setStyleSheet(_COMBO_STYLE)
        return c

    def _input(self, text="", placeholder="", echo_password=False):
        inp = QLineEdit()
        inp.setFont(QFont("Segoe UI", 9))
        inp.setFixedHeight(26)
        inp.setText(text)
        inp.setPlaceholderText(placeholder)
        inp.setStyleSheet(_INPUT_STYLE)
        if echo_password:
            inp.setEchoMode(QLineEdit.EchoMode.Password)
        return inp

    # ══════════════════════════════════════════════════════════════════
    # SECTION 1: PROVIDERS (API & LOCAL)
    # ══════════════════════════════════════════════════════════════════

    def _build_api_providers_section(self):
        sec = CollapsibleSection("PROVIDERS (API)", "🌐", expanded=True)

        cfg = load_config()

        # ── Gemini ──
        sec.add_widget(self._lbl("🔑 Gemini API Key", 8, True, C.ACC))
        self._gemini_key_input = self._input(
            cfg.get("gemini_api_key", ""),
            "Gemini API Key...",
            echo_password=True,
        )
        sec.add_widget(self._gemini_key_input)
        gem_row = QHBoxLayout()
        gem_row.setSpacing(4)
        self._save_gemini_btn = self._btn("Save", C.GREEN, h=22, w=60)
        self._save_gemini_btn.clicked.connect(self._save_gemini_key)
        self._gemini_status = self._lbl("", 7, color=C.TEXT_DIM)
        gem_row.addWidget(self._save_gemini_btn)
        gem_row.addWidget(self._gemini_status, stretch=1)
        sec.add_layout(gem_row)

        sec.add_widget(self._sep())

        # ── OpenRouter ──
        sec.add_widget(self._lbl("🔑 OpenRouter API Key", 8, True, C.ACC))
        self._openrouter_key_input = self._input(
            cfg.get("openrouter_api_key", ""),
            "OpenRouter API Key...",
            echo_password=True,
        )
        sec.add_widget(self._openrouter_key_input)
        or_save_row = QHBoxLayout()
        or_save_row.setSpacing(4)
        self._save_or_btn = self._btn("Save", C.GREEN, h=22, w=60)
        self._save_or_btn.clicked.connect(self._save_openrouter_key)
        self._or_status = self._lbl("", 7, color=C.TEXT_DIM)
        or_save_row.addWidget(self._save_or_btn)
        or_save_row.addWidget(self._or_status, stretch=1)
        sec.add_layout(or_save_row)

        sec.add_widget(self._lbl("Free Models", 8, True, C.GREEN))
        self._or_model_combo = self._combo()
        _populate_or_combo(self._or_model_combo, get_model("openrouter"))
        sec.add_widget(self._or_model_combo)
        or_model_row = QHBoxLayout()
        or_model_row.setSpacing(4)
        self._save_or_model_btn = self._btn("Apply", C.GREEN, h=22, w=60)
        self._save_or_model_btn.clicked.connect(self._save_or_model)
        self._or_model_status = self._lbl("", 7, color=C.TEXT_DIM)
        or_model_row.addWidget(self._save_or_model_btn)
        or_model_row.addWidget(self._or_model_status, stretch=1)
        sec.add_layout(or_model_row)

        sec.add_widget(self._sep())

        self._container_layout.addWidget(sec)

    def _build_local_providers_section(self):
        sec = CollapsibleSection("PROVIDERS (LOCAL)", "💻", expanded=True)

        cfg = load_config()

        # ── Ollama ──
        sec.add_widget(self._lbl("🦙 Ollama", 8, True, "#00e5ff"))
        ollama_row = QHBoxLayout()
        ollama_row.setSpacing(4)
        self._ollama_model_combo = self._combo()
        self._ollama_model_combo.setEditable(True)
        ollama_row.addWidget(self._ollama_model_combo, stretch=1)
        self._ollama_refresh_btn = self._btn("↻", C.PRI, h=26, w=28)
        self._ollama_refresh_btn.clicked.connect(self._refresh_ollama_models)
        ollama_row.addWidget(self._ollama_refresh_btn)
        sec.add_layout(ollama_row)

        oll_btns = QHBoxLayout()
        oll_btns.setSpacing(4)
        self._ollama_run_btn = self._btn("▶ Run", C.GREEN, h=22)
        self._ollama_run_btn.clicked.connect(self._save_ollama_model)
        self._ollama_eject_btn = self._btn("⏹ Eject", C.RED, h=22)
        self._ollama_eject_btn.clicked.connect(self._eject_ollama)
        self._ollama_pull_btn = self._btn("⬇ Pull", C.PRI, h=22)
        self._ollama_pull_btn.clicked.connect(self._pull_ollama)
        oll_btns.addWidget(self._ollama_run_btn)
        oll_btns.addWidget(self._ollama_eject_btn)
        oll_btns.addWidget(self._ollama_pull_btn)
        sec.add_layout(oll_btns)

        self._ollama_status = self._lbl("", 7, color=C.TEXT_DIM)
        sec.add_widget(self._ollama_status)

        # Server control
        srv_row = QHBoxLayout()
        srv_row.setSpacing(4)
        self._oll_up_btn = self._btn("▶ UP", C.GREEN, h=22)
        self._oll_up_btn.clicked.connect(self._ollama_up)
        self._oll_down_btn = self._btn("⏹ DOWN", C.RED, h=22)
        self._oll_down_btn.clicked.connect(self._ollama_down)
        self._oll_srv_status = self._lbl("...", 7, color=C.TEXT_DIM)
        srv_row.addWidget(self._oll_up_btn)
        srv_row.addWidget(self._oll_down_btn)
        srv_row.addWidget(self._oll_srv_status, stretch=1)
        sec.add_layout(srv_row)

        sec.add_widget(self._sep())

        # ── LM Studio ──
        sec.add_widget(self._lbl("💻 LM Studio", 8, True, "#ffb300"))
        self._lm_path_lbl = self._lbl("Scanning...", 7, color=C.TEXT_DIM)
        sec.add_widget(self._lm_path_lbl)

        url_row = QHBoxLayout()
        url_row.setSpacing(4)
        url_row.addWidget(self._lbl("URL:", 8, True, C.TEXT_MED))
        self._lm_url_input = self._input(
            cfg.get("lmstudio_url", "http://localhost:1234"),
            "http://localhost:1234",
        )
        url_row.addWidget(self._lm_url_input, stretch=1)
        self._lm_url_save_btn = self._btn("✓", C.GREEN, h=24, w=28)
        self._lm_url_save_btn.clicked.connect(self._save_lm_url)
        url_row.addWidget(self._lm_url_save_btn)
        sec.add_layout(url_row)

        lm_ctrl = QHBoxLayout()
        lm_ctrl.setSpacing(4)
        self._lm_launch_btn = self._btn("▶ Start", C.GREEN, h=22)
        self._lm_launch_btn.clicked.connect(self._on_lm_launch)
        self._lm_quit_btn = self._btn("⏹ Stop", C.RED, h=22)
        self._lm_quit_btn.clicked.connect(self._on_lm_quit)
        self._lm_server_lbl = self._lbl("...", 7, color=C.TEXT_DIM)
        lm_ctrl.addWidget(self._lm_launch_btn)
        lm_ctrl.addWidget(self._lm_quit_btn)
        lm_ctrl.addWidget(self._lm_server_lbl, stretch=1)
        sec.add_layout(lm_ctrl)

        self._lm_model_combo = self._combo()
        self._lm_model_combo.currentIndexChanged.connect(self._save_lm_model)
        sec.add_widget(self._lm_model_combo)

        lm_model_btns = QHBoxLayout()
        lm_model_btns.setSpacing(4)
        self._lm_run_btn = self._btn("▶ Load", C.GREEN, h=22)
        self._lm_run_btn.clicked.connect(self._on_lm_run_model)
        self._lm_eject_btn = self._btn("⏹ Unload", C.RED, h=22)
        self._lm_eject_btn.clicked.connect(self._on_lm_eject_model)
        self._lm_scan_btn = self._btn("↻ Scan", C.ACC, h=22)
        self._lm_scan_btn.clicked.connect(self._populate_lm_models)
        self._lm_model_status = self._lbl("", 7, color=C.TEXT_DIM)
        lm_model_btns.addWidget(self._lm_run_btn)
        lm_model_btns.addWidget(self._lm_eject_btn)
        lm_model_btns.addWidget(self._lm_scan_btn)
        sec.add_layout(lm_model_btns)
        sec.add_widget(self._lm_model_status)

        self._container_layout.addWidget(sec)

        # Deferred init
        QTimer.singleShot(100, self._deferred_provider_init)

    def _deferred_provider_init(self):
        """Load data that may be slow (network calls, subprocess)."""
        self._refresh_ollama_models()
        self._check_ollama_server()
        self._check_lm_path()
        self._refresh_lm_status()
        self._populate_lm_models()

    # ══════════════════════════════════════════════════════════════════
    # SECTION 2: LOCAL SETTINGS
    # ══════════════════════════════════════════════════════════════════

    def _build_local_settings_section(self):
        sec = CollapsibleSection("LOCAL SETTINGS", "🎛️", expanded=False)
        cfg = load_config()

        # Audio Devices
        sec.add_widget(self._lbl("🎙 Audio Input", 8, True, C.PRI))
        self._mic_combo = self._combo()
        sec.add_widget(self._mic_combo)

        sec.add_widget(self._lbl("🔊 Audio Output", 8, True, C.PRI))
        self._speaker_combo = self._combo()
        sec.add_widget(self._speaker_combo)

        # Volume
        sec.add_widget(self._sep())
        sec.add_widget(self._lbl("🔊 Volume", 8, True, C.PRI))
        vol_row = QHBoxLayout()
        vol_row.setSpacing(4)
        vol_val = cfg.get("audio_volume", 80)
        self._volume_slider = QSlider(Qt.Orientation.Horizontal)
        self._volume_slider.setRange(0, 100)
        self._volume_slider.setValue(vol_val)
        self._volume_slider.setFixedHeight(20)
        self._volume_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background: {C.BORDER}; height: 3px; border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {C.PRI}; width: 12px; height: 12px;
                margin: -5px 0; border-radius: 6px;
            }}
            QSlider::sub-page:horizontal {{
                background: {C.PRI_DIM}; border-radius: 2px;
            }}
        """)
        self._volume_slider.valueChanged.connect(self._on_volume_changed)
        vol_row.addWidget(self._volume_slider, stretch=1)
        self._vol_label = self._lbl(f"{vol_val}%", 8, True, C.PRI)
        self._vol_label.setFixedWidth(35)
        vol_row.addWidget(self._vol_label)
        sec.add_layout(vol_row)

        # STT / TTS engine
        sec.add_widget(self._sep())
        sec.add_widget(self._lbl("🗣 Voice Engines", 8, True, C.PRI))

        stt_row = QHBoxLayout()
        stt_row.setSpacing(4)
        stt_row.addWidget(self._lbl("STT:", 8, color=C.TEXT_MED))
        self._stt_combo = self._combo()
        self._stt_combo.addItem("Gemini Cloud", "gemini")
        self._stt_combo.addItem("Whisper Local", "whisper")
        self._select_by_data(self._stt_combo, cfg.get("stt_engine", "gemini"))
        stt_row.addWidget(self._stt_combo, stretch=1)
        sec.add_layout(stt_row)

        tts_row = QHBoxLayout()
        tts_row.setSpacing(4)
        tts_row.addWidget(self._lbl("TTS:", 8, color=C.TEXT_MED))
        self._tts_combo = self._combo()
        self._tts_combo.addItem("Gemini Cloud", "gemini")
        self._tts_combo.addItem("Piper Local", "piper")
        self._select_by_data(self._tts_combo, cfg.get("tts_engine", "piper"))
        tts_row.addWidget(self._tts_combo, stretch=1)
        sec.add_layout(tts_row)

        # Whisper/Piper paths
        sec.add_widget(self._sep())
        sec.add_widget(self._lbl("Whisper Path", 7, color=C.TEXT_DIM))
        self._whisper_path = self._input(cfg.get("whisper_path", ""), "Whisper executable")
        sec.add_widget(self._whisper_path)
        sec.add_widget(self._lbl("Whisper Model", 7, color=C.TEXT_DIM))
        self._whisper_model = self._input(cfg.get("whisper_model", ""), "GGML model .bin")
        sec.add_widget(self._whisper_model)
        sec.add_widget(self._lbl("Piper Path", 7, color=C.TEXT_DIM))
        self._piper_path = self._input(cfg.get("piper_path", ""), "Piper executable")
        sec.add_widget(self._piper_path)
        sec.add_widget(self._lbl("Piper Model", 7, color=C.TEXT_DIM))
        self._piper_model = self._input(cfg.get("piper_model", ""), "ONNX model .onnx")
        sec.add_widget(self._piper_model)

        # Voice toggle + save
        sec.add_widget(self._sep())
        self._voice_chk = QCheckBox(" Enable Voice")
        self._voice_chk.setStyleSheet(f"color: {C.TEXT_MED}; font-size: 9pt;")
        self._voice_chk.setChecked(cfg.get("voice_wrapper_enabled", False))
        sec.add_widget(self._voice_chk)

        save_row = QHBoxLayout()
        save_row.setSpacing(4)
        self._auto_detect_btn = self._btn("🔍 Auto-detect", C.ACC, h=22)
        self._auto_detect_btn.clicked.connect(self._scan_local_engines)
        self._save_voice_btn = self._btn("💾 Save", C.GREEN, h=22)
        self._save_voice_btn.clicked.connect(self._save_voice_settings)
        save_row.addWidget(self._auto_detect_btn)
        save_row.addWidget(self._save_voice_btn)
        sec.add_layout(save_row)

        # Security
        sec.add_widget(self._sep())
        sec.add_widget(self._lbl("🔐 Security Password", 8, True, C.RED))
        self._admin_pwd = self._input(cfg.get("admin_password", ""), "Leave empty to disable", True)
        sec.add_widget(self._admin_pwd)

        self._container_layout.addWidget(sec)

        # Populate audio devices deferred
        QTimer.singleShot(200, self._populate_audio_devices)

    # ══════════════════════════════════════════════════════════════════
    # SECTION 3: MCP SERVERS
    # ══════════════════════════════════════════════════════════════════

    def _build_mcp_section(self):
        sec = CollapsibleSection("MCP SERVERS", "🔗", expanded=False)

        self._mcp_list_layout = QVBoxLayout()
        self._mcp_list_layout.setSpacing(2)
        sec.add_layout(self._mcp_list_layout)

        self._mcp_status_lbl = self._lbl("Loading...", 8, color=C.TEXT_DIM)
        sec.add_widget(self._mcp_status_lbl)

        self._container_layout.addWidget(sec)
        QTimer.singleShot(300, self._refresh_mcp_list)

    def _refresh_mcp_list(self):
        """Read MCP server config and show status."""
        # Clear existing
        while self._mcp_list_layout.count():
            item = self._mcp_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cfg = load_config()
        servers = cfg.get("mcp_servers", {})
        if not servers:
            self._mcp_status_lbl.setText("No MCP servers configured")
            self._mcp_status_lbl.setStyleSheet(f"color: {C.TEXT_DIM}; background: transparent;")
            return

        for name, config in servers.items():
            row = QHBoxLayout()
            row.setSpacing(4)
            dot = self._lbl("●", 8, True, C.GREEN)
            dot.setFixedWidth(12)
            row.addWidget(dot)
            row.addWidget(self._lbl(name, 8, True, C.TEXT_MED), stretch=1)
            cmd = config.get("command", "?")
            row.addWidget(self._lbl(cmd, 7, color=C.TEXT_DIM))

            wrapper = QWidget()
            wrapper.setLayout(row)
            wrapper.setStyleSheet("background: transparent;")
            self._mcp_list_layout.addWidget(wrapper)

        self._mcp_status_lbl.setText(f"{len(servers)} server(s) configured")
        self._mcp_status_lbl.setStyleSheet(f"color: {C.GREEN}; background: transparent;")

    # ══════════════════════════════════════════════════════════════════
    # SECTION 4: SKILLS
    # ══════════════════════════════════════════════════════════════════

    def _build_skills_section(self):
        sec = CollapsibleSection("SKILLS", "⚡", expanded=False)

        self._skills_list_layout = QVBoxLayout()
        self._skills_list_layout.setSpacing(2)
        sec.add_layout(self._skills_list_layout)

        self._skills_status_lbl = self._lbl("Loading...", 8, color=C.TEXT_DIM)
        sec.add_widget(self._skills_status_lbl)

        refresh_btn = self._btn("↻ Refresh", C.PRI, h=22)
        refresh_btn.clicked.connect(self._refresh_skills_list)
        sec.add_widget(refresh_btn)

        self._container_layout.addWidget(sec)
        QTimer.singleShot(400, self._refresh_skills_list)

    def _refresh_skills_list(self):
        """Read loaded skills from SkillManager singleton."""
        while self._skills_list_layout.count():
            item = self._skills_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        try:
            from services.skills.manager import SkillManager
            mgr = SkillManager()
            skills = mgr.loaded_skills
        except Exception:
            skills = {}

        if not skills:
            self._skills_status_lbl.setText("No skills loaded")
            self._skills_status_lbl.setStyleSheet(f"color: {C.TEXT_DIM}; background: transparent;")
            return

        for name, tool in skills.items():
            row = QHBoxLayout()
            row.setSpacing(4)
            row.addWidget(self._lbl("⚡", 8, color=C.ACC))
            row.addWidget(self._lbl(name, 8, True, C.TEXT_MED), stretch=1)
            wrapper = QWidget()
            wrapper.setLayout(row)
            wrapper.setStyleSheet("background: transparent;")
            self._skills_list_layout.addWidget(wrapper)

        self._skills_status_lbl.setText(f"{len(skills)} skill(s) loaded")
        self._skills_status_lbl.setStyleSheet(f"color: {C.GREEN}; background: transparent;")

    # ══════════════════════════════════════════════════════════════════
    # SECTION 5: AGENTS (placeholder)
    # ══════════════════════════════════════════════════════════════════

    def _build_agents_section(self):
        sec = CollapsibleSection("AGENTS", "🤖", expanded=False)
        sec.add_widget(self._lbl("Agent orchestration coming soon.", 8, color=C.TEXT_DIM,
                                  align=Qt.AlignmentFlag.AlignCenter))
        sec.add_widget(self._lbl("Agents will be configurable here\nfor multi-model workflows.", 7,
                                  color=C.TEXT_DIM, align=Qt.AlignmentFlag.AlignCenter))
        self._container_layout.addWidget(sec)

    # ══════════════════════════════════════════════════════════════════
    # SECTION 6: DAILY TASKS (placeholder)
    # ══════════════════════════════════════════════════════════════════

    def _build_tasks_section(self):
        sec = CollapsibleSection("DAILY TASKS", "📋", expanded=False)
        sec.add_widget(self._lbl("Task scheduler coming soon.", 8, color=C.TEXT_DIM,
                                  align=Qt.AlignmentFlag.AlignCenter))
        sec.add_widget(self._lbl("Define recurring routines and\nautomation schedules.", 7,
                                  color=C.TEXT_DIM, align=Qt.AlignmentFlag.AlignCenter))
        self._container_layout.addWidget(sec)

    # ══════════════════════════════════════════════════════════════════
    # PROVIDER ACTIONS
    # ══════════════════════════════════════════════════════════════════

    def _save_gemini_key(self):
        key = self._gemini_key_input.text().strip()
        try:
            save_config({"gemini_api_key": key})
            self._gemini_status.setText("✓ Saved")
            self._gemini_status.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
        except Exception as e:
            self._gemini_status.setText(f"❌ {e}")
            self._gemini_status.setStyleSheet(f"color: {C.RED}; background: transparent;")

    def _save_openrouter_key(self):
        key = self._openrouter_key_input.text().strip()
        try:
            save_config({"openrouter_api_key": key})
            self._or_status.setText("✓ Saved")
            self._or_status.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
        except Exception as e:
            self._or_status.setText(f"❌ {e}")
            self._or_status.setStyleSheet(f"color: {C.RED}; background: transparent;")

    def _save_or_model(self):
        model_id = self._or_model_combo.currentData()
        if model_id:
            set_model(model_id, "openrouter")
            self._or_model_status.setText(f"✓ {model_id.split('/')[1].split(':')[0]}")
            self._or_model_status.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
            # Sync right combo
            right_combo = self._main_win._right_model_combo
            _populate_or_combo(right_combo, model_id)
            # Trigger engine restart
            cfg = load_config()
            provider = cfg.get("selected_provider", "gemini")
            if hasattr(self._main_win, '_on_provider_changed') and self._main_win._on_provider_changed:
                self._main_win._on_provider_changed(provider)

    def _refresh_ollama_models(self):
        self._ollama_model_combo.blockSignals(True)
        self._ollama_model_combo.clear()
        saved = get_model("ollama")
        try:
            r = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
            if r.returncode == 0 and r.stdout.strip():
                for line in r.stdout.strip().split("\n")[1:]:
                    parts = line.split()
                    if parts:
                        mid = parts[0].strip()
                        self._ollama_model_combo.addItem(mid.replace(":latest", ""), mid)
        except Exception:
            pass
        # Select saved
        for i in range(self._ollama_model_combo.count()):
            if self._ollama_model_combo.itemData(i) == saved:
                self._ollama_model_combo.setCurrentIndex(i)
                break
        self._ollama_model_combo.blockSignals(False)

    def _save_ollama_model(self):
        mid = self._ollama_model_combo.currentData() or self._ollama_model_combo.currentText()
        if mid:
            set_model(mid, "ollama")
            self._ollama_status.setText(f"✓ {mid}")
            self._ollama_status.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
            cfg = load_config()
            provider = cfg.get("selected_provider", "gemini")
            if provider == "ollama":
                right = self._main_win._right_model_combo
                for i in range(right.count()):
                    if right.itemData(i) == mid or right.itemText(i) == mid:
                        right.setCurrentIndex(i)
                        break

    def _eject_ollama(self):
        import re
        mid = self._ollama_model_combo.currentData() or self._ollama_model_combo.currentText()
        if not mid or not re.match(r"^[a-zA-Z0-9\-\.\:]+$", mid):
            return
        try:
            subprocess.run(["ollama", "stop", mid], capture_output=True, timeout=10)
            self._ollama_status.setText(f"✓ Ejected {mid}")
            self._ollama_status.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
        except Exception as e:
            self._ollama_status.setText(f"❌ {e}")
            self._ollama_status.setStyleSheet(f"color: {C.RED}; background: transparent;")

    def _pull_ollama(self):
        import re
        mid = self._ollama_model_combo.currentData() or self._ollama_model_combo.currentText()
        if not mid or not re.match(r"^[a-zA-Z0-9\-\.\:]+$", mid):
            return
        try:
            if _OS == "Windows":
                subprocess.Popen(["cmd.exe", "/c", "start", "cmd.exe", "/k", "ollama", "pull", mid])
            self._ollama_status.setText(f"⬇ Pulling {mid}...")
            self._ollama_status.setStyleSheet(f"color: {C.ACC}; background: transparent;")
        except Exception as e:
            self._ollama_status.setText(f"❌ {e}")

    def _check_ollama_server(self):
        try:
            if _OS == "Windows":
                r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq ollama.exe"],
                                   capture_output=True, text=True, timeout=3)
                if "ollama.exe" in r.stdout:
                    self._oll_srv_status.setText("● RUNNING")
                    self._oll_srv_status.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
                    return
            self._oll_srv_status.setText("○ STOPPED")
            self._oll_srv_status.setStyleSheet(f"color: {C.TEXT_DIM}; background: transparent;")
        except Exception:
            self._oll_srv_status.setText("○ unknown")

    def _ollama_up(self):
        try:
            if _OS == "Windows":
                subprocess.Popen(["cmd.exe", "/c", "start", "cmd.exe", "/k", "ollama", "serve"])
            self._oll_srv_status.setText("▶ Starting...")
            self._oll_srv_status.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
            QTimer.singleShot(3000, self._check_ollama_server)
        except Exception as e:
            self._oll_srv_status.setText(f"❌ {e}")

    def _ollama_down(self):
        try:
            if _OS == "Windows":
                subprocess.run(["taskkill", "/F", "/IM", "ollama.exe"], capture_output=True, timeout=5)
            self._oll_srv_status.setText("■ Stopped")
            self._oll_srv_status.setStyleSheet(f"color: {C.RED}; background: transparent;")
        except Exception as e:
            self._oll_srv_status.setText(f"❌ {e}")

    # ── LM Studio ──
    def _check_lm_path(self):
        cli = find_lms_cli_path()
        gui = find_lmstudio_path()
        if cli or gui:
            parts = []
            if cli: parts.append("CLI")
            if gui: parts.append("GUI")
            self._lm_path_lbl.setText(f"✓ {', '.join(parts)} detected")
            self._lm_path_lbl.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
        else:
            self._lm_path_lbl.setText("⚠ Not found")
            self._lm_path_lbl.setStyleSheet(f"color: {C.RED}; background: transparent;")

    def _refresh_lm_status(self):
        running = is_server_running()
        if running:
            self._lm_server_lbl.setText("● RUNNING")
            self._lm_server_lbl.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
        else:
            self._lm_server_lbl.setText("● OFFLINE")
            self._lm_server_lbl.setStyleSheet(f"color: {C.RED}; background: transparent;")

    def _populate_lm_models(self):
        self._lm_model_combo.blockSignals(True)
        self._lm_model_combo.clear()
        saved = get_model("lmstudio")
        models = get_downloaded_models()
        if models:
            for m in models:
                self._lm_model_combo.addItem(m["name"], m["id"])
            for i in range(self._lm_model_combo.count()):
                if self._lm_model_combo.itemData(i) == saved:
                    self._lm_model_combo.setCurrentIndex(i)
                    break
            self._lm_model_status.setText(f"📦 {len(models)} model(s)")
        else:
            self._lm_model_combo.addItem("Default (loaded)", "local-model")
            self._lm_model_status.setText("No models found")
        self._lm_model_combo.blockSignals(False)

    def _save_lm_model(self, *args):
        mid = self._lm_model_combo.currentData()
        if mid:
            set_model(mid, "lmstudio")

    def _save_lm_url(self):
        url = self._lm_url_input.text().strip()
        if url:
            save_config({"lmstudio_url": url})

    def _on_lm_launch(self):
        import threading
        self._lm_server_lbl.setText("⏳ Starting...")
        self._lm_server_lbl.setStyleSheet(f"color: {C.ACC}; background: transparent;")
        def worker():
            launch_lmstudio()
            QTimer.singleShot(0, lambda: (self._refresh_lm_status(), self._populate_lm_models()))
        threading.Thread(target=worker, daemon=True).start()

    def _on_lm_quit(self):
        import threading
        self._lm_server_lbl.setText("⏳ Stopping...")
        def worker():
            quit_lmstudio()
            QTimer.singleShot(0, self._refresh_lm_status)
        threading.Thread(target=worker, daemon=True).start()

    def _on_lm_run_model(self):
        mid = self._lm_model_combo.currentData()
        if not mid or mid == "local-model":
            return
        import threading
        self._lm_model_status.setText(f"⏳ Loading...")
        self._lm_model_status.setStyleSheet(f"color: {C.ACC}; background: transparent;")
        self._lm_run_btn.setEnabled(False)
        def worker():
            ok, msg = load_model(mid)
            def done():
                self._lm_run_btn.setEnabled(True)
                if ok:
                    self._save_lm_model()
                    self._lm_model_status.setText(f"✅ Loaded")
                    self._lm_model_status.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
                else:
                    self._lm_model_status.setText(f"❌ {msg}")
                    self._lm_model_status.setStyleSheet(f"color: {C.RED}; background: transparent;")
            QTimer.singleShot(0, done)
        threading.Thread(target=worker, daemon=True).start()

    def _on_lm_eject_model(self):
        mid = self._lm_model_combo.currentData()
        if not mid or mid == "local-model":
            return
        import threading
        self._lm_eject_btn.setEnabled(False)
        def worker():
            ok, msg = unload_model(mid)
            def done():
                self._lm_eject_btn.setEnabled(True)
                if ok:
                    self._lm_model_status.setText("✅ Unloaded")
                    self._lm_model_status.setStyleSheet(f"color: {C.GREEN}; background: transparent;")
                else:
                    self._lm_model_status.setText(f"❌ {msg}")
                    self._lm_model_status.setStyleSheet(f"color: {C.RED}; background: transparent;")
            QTimer.singleShot(0, done)
        threading.Thread(target=worker, daemon=True).start()

    # ── LOCAL SETTINGS ACTIONS ──

    def _populate_audio_devices(self):
        saved_mic = load_config().get("audio_input_device", None)
        saved_spk = load_config().get("audio_output_device", None)
        self._mic_combo.addItem("🎙 System Default", None)
        self._speaker_combo.addItem("🔊 System Default", None)
        _MAPPER_KW = ("asignador de sonido", "microsoft sound mapper", "controlador primario", "primary sound")
        try:
            devices = sd.query_devices()
            for i, dev in enumerate(devices):
                name = dev["name"]
                if any(kw in name.lower() for kw in _MAPPER_KW):
                    continue
                sr = dev.get("default_samplerate", 0)
                sr_str = f" {int(sr)}Hz" if sr else ""
                if dev["max_input_channels"] > 0:
                    self._mic_combo.addItem(f"[{i}] {name}{sr_str}", i)
                if dev["max_output_channels"] > 0:
                    self._speaker_combo.addItem(f"[{i}] {name}{sr_str}", i)
            self._select_by_data(self._mic_combo, saved_mic)
            self._select_by_data(self._speaker_combo, saved_spk)
        except Exception:
            pass
        self._mic_combo.currentIndexChanged.connect(self._on_audio_dev_changed)
        self._speaker_combo.currentIndexChanged.connect(self._on_audio_dev_changed)

    def _on_audio_dev_changed(self):
        try:
            save_config({
                "audio_input_device": self._mic_combo.currentData(),
                "audio_output_device": self._speaker_combo.currentData(),
            })
        except Exception:
            pass

    def _on_volume_changed(self, val: int):
        self._vol_label.setText(f"{val}%")
        save_config({"audio_volume": val})
        # Sync main window volume slider
        if hasattr(self._main_win, '_volume_slider'):
            self._main_win._volume_slider.blockSignals(True)
            self._main_win._volume_slider.setValue(val)
            self._main_win._vol_label.setText(f"{val}%")
            self._main_win._volume_slider.blockSignals(False)

    def _save_voice_settings(self):
        save_config({
            "voice_wrapper_enabled": self._voice_chk.isChecked(),
            "stt_engine": self._stt_combo.currentData(),
            "tts_engine": self._tts_combo.currentData(),
            "whisper_path": self._whisper_path.text().strip(),
            "whisper_model": self._whisper_model.text().strip(),
            "piper_path": self._piper_path.text().strip(),
            "piper_model": self._piper_model.text().strip(),
            "admin_password": self._admin_pwd.text().strip(),
        })

    def _scan_local_engines(self):
        base_dir = Path(__file__).resolve().parent.parent.parent
        search_dirs = [base_dir / "bin", base_dir / "scripts" / "bin", base_dir / "habilidades"]
        is_win = _OS == "Windows"
        whisper_exe = "main.exe" if is_win else "main"
        piper_exe = "piper.exe" if is_win else "piper"
        found = {"wp": "", "wm": "", "pp": "", "pm": ""}
        for s_dir in search_dirs:
            if not s_dir.exists():
                continue
            for root, dirs, files in os.walk(s_dir):
                for f in files:
                    if f == whisper_exe and not found["wp"] and "whisper" in str(root).lower():
                        found["wp"] = os.path.join(root, f)
                    elif f == piper_exe and not found["pp"]:
                        found["pp"] = os.path.join(root, f)
                    elif f.endswith(".bin") and "ggml" in f.lower() and not found["wm"]:
                        found["wm"] = os.path.join(root, f)
                    elif f.endswith(".onnx") and not found["pm"]:
                        found["pm"] = os.path.join(root, f)
        if found["wp"]: self._whisper_path.setText(os.path.normpath(found["wp"]))
        if found["wm"]: self._whisper_model.setText(os.path.normpath(found["wm"]))
        if found["pp"]: self._piper_path.setText(os.path.normpath(found["pp"]))
        if found["pm"]: self._piper_model.setText(os.path.normpath(found["pm"]))
        self._save_voice_settings()
        self._auto_detect_btn.setText("✓ Found")
        self._auto_detect_btn.setStyleSheet(f"""
            QPushButton {{ background: {C.GREEN}; color: {C.DARK};
            border: 1px solid {C.GREEN}; border-radius: 8px; padding: 1px 8px; font-weight: bold; }}
        """)

    def _select_by_data(self, combo, data):
        for i in range(combo.count()):
            if combo.itemData(i) == data:
                combo.setCurrentIndex(i)
                return

    # ── Compatibility with old ConfigToolbar references ──

    def update_status(self, provider: str):
        """No-op compatibility stub."""
        pass
