from __future__ import annotations

import json
import math
import os
import platform
import random
import subprocess
import sys
import threading
import time
from pathlib import Path

import psutil

from PyQt6.QtCore import (
    QEasingCurve, QMimeData, QObject, QPointF, QRectF, QSize, Qt,
    QTimer, QUrl, pyqtSignal, QThread,
)
from PyQt6.QtGui import (
    QBrush, QColor, QDragEnterEvent, QDropEvent, QFont, QFontDatabase,
    QKeySequence, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap,
    QRadialGradient, QShortcut,
)
from PyQt6.QtWidgets import (
    QApplication, QComboBox, QFileDialog, QFrame, QHBoxLayout, QLabel,
    QMainWindow, QProgressBar, QPushButton, QSizePolicy, QTextEdit, QVBoxLayout, QWidget,
    QTabWidget, QSlider,
)

from memory.config_manager import load_config, save_config, get_model, set_model, is_configured, get_lmstudio_url
from ui.theme import Theme as C, qcol, PROVIDER_COLORS, get_openrouter_color as _get_openrouter_color
from ui.wave_canvas import WaveCanvas
from ui.config_toolbar import _OR_FREE_MODELS, _populate_or_combo, _COMBO_STYLE
from ui.components.settings_panel import SettingsPanel
from ui.components.chat_bar import ChatBarWidget
from providers.lmstudio_control import (
    find_lmstudio_path, get_downloaded_models,
    launch_lmstudio, quit_lmstudio,
    is_server_running, get_server_status,
)

def _base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR   = _base_dir()
CONFIG_DIR = BASE_DIR / "config"
API_FILE   = CONFIG_DIR / "api_keys.json"

_DEFAULT_W, _DEFAULT_H = 980, 700
_MIN_W,     _MIN_H     = 820, 580
_LEFT_W  = 148
_RIGHT_W = 340

_OS = platform.system()  # "Windows" | "Darwin" | "Linux"


# ── Extracted components (now in separate modules) ──
from ui.metrics import SysMetrics as _SysMetrics, ProviderStatusWorker, MetricBar
from ui.log_panel import LogWidget
from ui.file_drop import FileDropZone, _FILE_ICONS, file_category as _file_category, fmt_size as _fmt_size
from ui.dialogs.settings import SetupOverlay


class _SysMetricsCompat(_SysMetrics):
    """Backwards-compatible alias."""
    pass


_metrics = _SysMetricsCompat()





class MainWindow(QMainWindow):
    _log_sig   = pyqtSignal(str)
    _state_sig = pyqtSignal(str)

    def __init__(self, face_path: str):
        super().__init__()
        self.setWindowTitle("J.A.R.V.I.S — MARK XL")
        self.setMinimumSize(_MIN_W, _MIN_H)
        self.resize(_DEFAULT_W, _DEFAULT_H)

        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            (screen.width()  - _DEFAULT_W) // 2,
            (screen.height() - _DEFAULT_H) // 2,
        )

        self.on_text_command    = None
        self.on_provider_changed = None
        self._muted              = False
        self._current_file: str | None = None
        cfg = load_config()
        self._llm_active = cfg.get("llm_active", True)

        central = QWidget()
        central.setStyleSheet(f"background: {C.BG};")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_header())

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self._left_panel = self._build_left_panel()
        body.addWidget(self._left_panel, stretch=0)

        self._main_content = self._build_main_content(face_path)
        body.addWidget(self._main_content, stretch=1)

        self._settings_panel = SettingsPanel(self)
        # initially visible or hidden based on your preference
        self._settings_panel.setVisible(True)
        body.addWidget(self._settings_panel, stretch=0)

        self._update_llm_ui()

        root.addLayout(body, stretch=1)
        root.addWidget(self._build_footer())

        self._clock_tmr = QTimer(self)
        self._clock_tmr.timeout.connect(self._tick_clock)
        self._clock_tmr.start(1000)
        self._tick_clock()

        # Metrik güncelleme timer'ı
        self._metric_tmr = QTimer(self)
        self._metric_tmr.timeout.connect(self._update_metrics)
        self._metric_tmr.start(2000)
        self._update_metrics()

        self._log_sig.connect(self._log.append_log)
        self._state_sig.connect(self._apply_state)

        self._overlay: SetupOverlay | None = None
        self._ready = self._check_config()
        if not self._ready:
            self._show_setup()

        self._provider_statuses = {"ollama": False, "lmstudio": False, "openrouter": False}
        self._current_state = "IDLE"
        self._status_worker = ProviderStatusWorker(self)
        self._status_worker.status_ready.connect(self._update_provider_status)
        self._status_worker.start()

        self._apply_theme_colors()

        sc_mute = QShortcut(QKeySequence("F4"), self)
        sc_mute.activated.connect(self._toggle_mute)
        sc_full = QShortcut(QKeySequence("F11"), self)
        sc_full.activated.connect(self._toggle_fullscreen)

    def _switch_provider(self, provider: str):
        """Switch the active AI provider and notify the backend."""
        # Save current model before switching away
        cfg = load_config()
        old_provider = cfg.get("selected_provider", "gemini")
        if old_provider != provider:
            old_model_id = self._right_model_combo.currentData()
            if old_model_id:
                set_model(old_model_id, old_provider)
        # Save new provider selection
        save_config({"selected_provider": provider})
        if provider in ("ollama", "openrouter", "lmstudio"):
            self._set_audio_engine("local", trigger_callback=False)
        else:
            self._set_audio_engine("gemini", trigger_callback=False)
            
        C.set_provider_theme(provider)
        self._apply_theme_colors()
        self._update_llm_ui()
        prov_name = {"gemini": "GEMINI", "ollama": "OLLAMA", "openrouter": "OPENROUTER", "lmstudio": "LM STUDIO"}.get(provider, provider)
        if hasattr(self, '_chat_bar'):
            idx = self._chat_bar.provider_combo.findText(provider, Qt.MatchFlag.MatchContains | Qt.MatchFlag.MatchFixedString)
            if idx >= 0 and self._chat_bar.provider_combo.currentIndex() != idx:
                self._chat_bar.provider_combo.setCurrentIndex(idx)
        if hasattr(self, '_settings_panel'):
            self._settings_panel.update_status(provider)
        # Update config toolbar
        if hasattr(self, '_config_bar'):
            self._config_bar.update_status(provider)
        self._log.append_log(f"SYS: Switched to {prov_name} provider.")
        # Notify the backend if it's connected
        if hasattr(self, '_on_provider_changed') and self._on_provider_changed:
            self._on_provider_changed(provider)

    def _toggle_llm_state(self):
        self._llm_active = not self._llm_active
        save_config({"llm_active": self._llm_active})
        if not self._llm_active:
            # Switch to gemini automatically
            self._switch_provider("gemini")
        else:
            self._update_llm_ui()
        state_str = "ACTIVATED" if self._llm_active else "DEACTIVATED"
        self._log.append_log(f"SYS: LLM service has been {state_str}.")

    def _update_llm_ui(self):
        cfg = load_config()
        selected_provider = cfg.get("selected_provider", "gemini")
        
        if self._llm_active:
            if hasattr(self, "_llm_toggle_btn"):
                self._llm_toggle_btn.setText("● LLM ONLINE")
                self._llm_toggle_btn.setStyleSheet(f"""
                    QPushButton {{
                        background: #001a0d; color: {C.GREEN};
                        border: 1px solid {C.GREEN}; border-radius: 10px; padding: 0px 8px;
                    }}
                    QPushButton:hover {{ background: {C.GREEN}; color: #000; }}
                """)
            if hasattr(self, "_ai_core_lbl"):
                self._ai_core_lbl.setText("AI CORE\nACTIVE")
                self._ai_core_lbl.setStyleSheet(
                    f"color: {C.GREEN}; background: {C.PANEL2};"
                    f"border: 1px solid {C.BORDER_A}; border-radius: 10px; padding: 4px;"
                )
            
            if hasattr(self, "_chat_bar"):
                self._chat_bar.provider_combo.setEnabled(True)
                self._chat_bar.provider_combo.setToolTip("Seleccionar proveedor")
            self._highlight_provider(selected_provider)
        else:
            if hasattr(self, "_llm_toggle_btn"):
                self._llm_toggle_btn.setText("○ LLM OFFLINE")
                self._llm_toggle_btn.setStyleSheet(f"""
                    QPushButton {{
                        background: #1a0005; color: {C.RED};
                        border: 1px solid {C.RED}; border-radius: 10px; padding: 0px 8px;
                    }}
                    QPushButton:hover {{ background: {C.RED}; color: #fff; }}
                """)
            if hasattr(self, "_ai_core_lbl"):
                self._ai_core_lbl.setText("AI CORE\nINACTIVE")
                self._ai_core_lbl.setStyleSheet(
                    f"color: {C.RED}; background: {C.PANEL2};"
                    f"border: 1px solid {C.BORDER_A}; border-radius: 10px; padding: 4px;"
                )
            
            self._highlight_provider("gemini")
            
            if hasattr(self, "_chat_bar"):
                self._chat_bar.provider_combo.setEnabled(False)
                self._chat_bar.provider_combo.setToolTip("Activa LLM ONLINE para usar otros proveedores")


    def _apply_theme_colors(self):
        """Reapply dynamic theme colors to the main UI components."""
        if hasattr(self, '_title_lbl'):
            self._title_lbl.setStyleSheet(f"color: {C.PRI}; background: transparent;")
        if hasattr(self, '_sub_lbl'):
            self._sub_lbl.setStyleSheet(f"color: {C.PRI_DIM}; background: transparent;")
        if hasattr(self, '_clock_lbl'):
            self._clock_lbl.setStyleSheet(f"color: {C.PRI}; background: transparent;")
        if hasattr(self, '_left_hdr_lbl'):
            self._left_hdr_lbl.setStyleSheet(f"color: {C.PRI}; background: transparent; border-bottom: 1px solid {C.BORDER}; padding-bottom: 4px;")
        if hasattr(self, '_sec_badges') and len(self._sec_badges) > 1:
            self._sec_badges[0].setStyleSheet(f"color: {C.PRI}; background: {C.PANEL2}; border: 1px solid {C.BORDER_A}; border-radius: 10px; padding: 4px;")
            self._sec_badges[1].setStyleSheet(f"color: {C.TEXT_DIM}; background: {C.PANEL2}; border: 1px solid {C.BORDER_A}; border-radius: 10px; padding: 4px;")
        if hasattr(self, '_vol_label'):
            self._vol_label.setStyleSheet(f"color: {C.PRI}; background: transparent;")
        if hasattr(self, '_volume_slider'):
            self._volume_slider.setStyleSheet(f"""
                QSlider::groove:horizontal {{
                    background: {C.BORDER}; height: 4px; border-radius: 6px;
                }}
                QSlider::handle:horizontal {{
                    background: {C.PRI}; width: 14px; height: 14px;
                    margin: -5px 0; border-radius: 7px;
                }}
                QSlider::sub-page:horizontal {{
                    background: {C.PRI_DIM}; border-radius: 6px;
                }}
            """)
    def _highlight_provider(self, provider: str):
        # Already handled nicely by combo box styling in ChatBarWidget
        pass

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._overlay and self._overlay.isVisible():
            ow, oh = 460, 390
            cw = self.centralWidget()
            self._overlay.setGeometry(
                (cw.width()  - ow) // 2,
                (cw.height() - oh) // 2,
                ow, oh,
            )

    def _update_metrics(self):
        snap = _metrics.snapshot()

        # CPU
        cpu = snap["cpu"]
        self._bar_cpu.set_value(cpu, f"{cpu:.0f}%")

        # MEM
        mem = snap["mem"]
        self._bar_mem.set_value(mem, f"{mem:.0f}%")

        # NET
        net = snap["net"]
        if net < 1.0:
            net_str = f"{net*1024:.0f}KB/s"
        else:
            net_str = f"{net:.1f}MB/s"
        net_pct = min(100, net * 10)  # 10 MB/s = %100
        self._bar_net.set_value(net_pct, net_str)

        # GPU
        gpu = snap["gpu"]
        if gpu >= 0:
            self._bar_gpu.set_value(gpu, f"{gpu:.0f}%")
        else:
            self._bar_gpu.set_value(0, "N/A")

        # TMP
        tmp = snap["tmp"]
        if tmp >= 0:
            tmp_pct = min(100, (tmp / 100) * 100)
            self._bar_tmp.set_value(tmp_pct, f"{tmp:.0f}°C")
        else:
            self._bar_tmp.set_value(0, "N/A")

        try:
            boot_t  = psutil.boot_time()
            elapsed = time.time() - boot_t
            h = int(elapsed // 3600)
            m = int((elapsed % 3600) // 60)
            self._uptime_lbl.setText(f"UP  {h:02d}:{m:02d}")
        except Exception:
            self._uptime_lbl.setText("UP  --:--")

        try:
            proc_count = len(psutil.pids())
            self._proc_lbl.setText(f"PROC  {proc_count}")
        except Exception:
            self._proc_lbl.setText("PROC  --")

    def _build_header(self) -> QWidget:
        w = QWidget()
        w.setFixedHeight(54)
        w.setStyleSheet(f"background: {C.DARK}; border-bottom: 1px solid {C.BORDER_B};")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(16, 0, 16, 0)

        def _badge(txt, color=C.TEXT_MED):
            l = QLabel(txt)
            l.setFont(QFont("Segoe UI", 11))
            l.setStyleSheet(f"color: {color}; background: transparent;")
            return l

        lay.addWidget(_badge("MARK XL", C.ACC))
        lay.addStretch()

        mid = QVBoxLayout(); mid.setSpacing(1)
        self._title_lbl = QLabel("J.A.R.V.I.S")
        self._title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title_lbl.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        mid.addWidget(self._title_lbl)
        self._sub_lbl = QLabel("Just A Rather Very Intelligent System")
        self._sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._sub_lbl.setFont(QFont("Segoe UI", 11))
        mid.addWidget(self._sub_lbl)
        lay.addLayout(mid)
        lay.addStretch()

        right_col = QVBoxLayout(); right_col.setSpacing(2)
        self._clock_lbl = QLabel("00:00:00")
        self._clock_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self._clock_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        right_col.addWidget(self._clock_lbl)
        self._date_lbl = QLabel("")
        self._date_lbl.setFont(QFont("Segoe UI", 11))
        self._date_lbl.setStyleSheet(f"color: {C.TEXT_DIM}; background: transparent;")
        self._date_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        right_col.addWidget(self._date_lbl)
        lay.addLayout(right_col)
        return w

    def _tick_clock(self):
        self._clock_lbl.setText(time.strftime("%H:%M:%S"))
        self._date_lbl.setText(time.strftime("%a %d %b %Y"))

    def _build_left_panel(self) -> QWidget:
        w = QWidget()
        w.setFixedWidth(_LEFT_W)
        w.setStyleSheet(f"background: {C.DARK}; border-right: 1px solid {C.BORDER};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(8, 10, 8, 10)
        lay.setSpacing(6)

        self._left_hdr_lbl = QLabel("◈ SYS MONITOR")
        self._left_hdr_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        lay.addWidget(self._left_hdr_lbl)
        lay.addSpacing(2)

        self._bar_cpu = MetricBar("CPU", C.PRI)
        self._bar_mem = MetricBar("MEM", C.ACC2)
        self._bar_net = MetricBar("NET", C.GREEN)
        self._bar_gpu = MetricBar("GPU", C.ACC)
        self._bar_tmp = MetricBar("TMP", "#ff6688")

        for bar in [self._bar_cpu, self._bar_mem, self._bar_net,
                    self._bar_gpu, self._bar_tmp]:
            lay.addWidget(bar)

        lay.addSpacing(4)

        info_panel = QWidget()
        info_panel.setStyleSheet(
            f"background: {C.PANEL2}; border: 1px solid {C.BORDER}; border-radius: 10px;"
        )
        ip_lay = QVBoxLayout(info_panel)
        ip_lay.setContentsMargins(6, 5, 6, 5)
        ip_lay.setSpacing(3)

        self._uptime_lbl = QLabel("UP  --:--")
        self._uptime_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._uptime_lbl.setStyleSheet(f"color: {C.GREEN}; background: transparent; border: none;")
        ip_lay.addWidget(self._uptime_lbl)

        self._proc_lbl = QLabel("PROC  --")
        self._proc_lbl.setFont(QFont("Segoe UI", 11))
        self._proc_lbl.setStyleSheet(f"color: {C.TEXT_MED}; background: transparent; border: none;")
        ip_lay.addWidget(self._proc_lbl)

        os_name = {"Windows": "WIN", "Darwin": "macOS", "Linux": "LINUX"}.get(_OS, _OS.upper())
        os_lbl = QLabel(f"OS  {os_name}")
        os_lbl.setFont(QFont("Segoe UI", 11))
        os_lbl.setStyleSheet(f"color: {C.ACC2}; background: transparent; border: none;")
        ip_lay.addWidget(os_lbl)

        lay.addWidget(info_panel)
        lay.addStretch()

        self._ai_core_lbl = QLabel("AI CORE\nACTIVE")
        self._ai_core_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self._ai_core_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self._ai_core_lbl)

        self._sec_badges = []
        for txt in ["SEC\nCLEARED", "PROTOCOL\nXXXVIII"]:
            lbl = QLabel(txt)
            lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._sec_badges.append(lbl)
            lay.addWidget(lbl)

        return w

    def _build_main_content(self, face_path: str) -> QWidget:
        # ── INTERACCIÓN Y CONSOLA ──
        console_widget = QWidget()
        console_widget.setStyleSheet("background: transparent;")
        console_lay = QHBoxLayout(console_widget)
        console_lay.setContentsMargins(12, 12, 12, 12)
        console_lay.setSpacing(16)

        def _sec(txt):
            l = QLabel(f"▸ {txt}")
            l.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            l.setStyleSheet(f"color: {C.TEXT_MED}; background: transparent;")
            return l

        cfg = load_config()

        # --- Columna Izquierda: HUD de Control ---
        hud_col = QVBoxLayout()
        hud_col.setSpacing(8)

        hud_col.addWidget(_sec("VISUALIZADOR HUD"))
        
        # Reduced-height visualizer
        self.hud = WaveCanvas(face_path)
        self.hud.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.hud.setMinimumHeight(240)
        self.hud.setMaximumHeight(300)
        hud_col.addWidget(self.hud, stretch=1)

        sep_hud = QFrame(); sep_hud.setFrameShape(QFrame.Shape.HLine)
        sep_hud.setStyleSheet(f"color: {C.BORDER}; margin: 4px 0;")
        hud_col.addWidget(sep_hud)

        hud_col.addWidget(_sec("CONTROLES DE VOZ"))
        
        self._mute_btn = QPushButton("🎙  MICROPHONE ACTIVE")
        self._mute_btn.setFixedHeight(34)
        self._mute_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._mute_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._mute_btn.clicked.connect(self._toggle_mute)
        self._style_mute_btn()
        hud_col.addWidget(self._mute_btn)

        fs_btn = QPushButton("⛶  FULLSCREEN  [F11]")
        fs_btn.setFixedHeight(34)
        fs_btn.setFont(QFont("Segoe UI", 10))
        fs_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        fs_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {C.TEXT_MED};
                border: 1px solid {C.BORDER}; border-radius: 10px;
            }}
            QPushButton:hover {{
                color: {C.PRI}; border: 1px solid {C.BORDER_B};
            }}
        """)
        fs_btn.clicked.connect(self._toggle_fullscreen)
        hud_col.addWidget(fs_btn)

        # Added Volume control directly in HUD for premium design
        hud_col.addSpacing(6)
        hud_col.addWidget(_sec("VOLUMEN DE RESPUESTA"))
        vol_row = QHBoxLayout(); vol_row.setSpacing(8)
        self._volume_slider = QSlider(Qt.Orientation.Horizontal)
        self._volume_slider.setFixedHeight(22)
        self._volume_slider.setMinimum(0)
        self._volume_slider.setMaximum(100)
        saved_vol = cfg.get("audio_volume", 80)
        self._volume_slider.setValue(saved_vol)
        self._volume_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background: {C.BORDER}; height: 4px; border-radius: 6px;
            }}
            QSlider::handle:horizontal {{
                background: {C.PRI}; width: 14px; height: 14px;
                margin: -5px 0; border-radius: 7px;
            }}
            QSlider::sub-page:horizontal {{
                background: {C.PRI_DIM}; border-radius: 6px;
            }}
        """)
        self._volume_slider.valueChanged.connect(self._on_volume_changed)
        vol_row.addWidget(self._volume_slider, stretch=1)
        self._vol_label = QLabel(f"{saved_vol}%")
        self._vol_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self._vol_label.setStyleSheet(f"color: {C.PRI}; background: transparent;")
        self._vol_label.setFixedWidth(40)
        vol_row.addWidget(self._vol_label)
        hud_col.addLayout(vol_row)

        hud_col.addSpacing(6)
        hud_col.addWidget(_sec("MOTOR DE AUDIO"))
        audio_btns = QHBoxLayout(); audio_btns.setSpacing(4)
        self._audio_gemini_btn = QPushButton("AUDIO\nGEMINI")
        self._audio_gemini_btn.setFixedHeight(50)
        self._audio_gemini_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self._audio_gemini_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._audio_gemini_btn.clicked.connect(lambda: self._set_audio_engine("gemini"))
        audio_btns.addWidget(self._audio_gemini_btn)
        
        self._audio_local_btn = QPushButton("WHISPER /\nPIPER")
        self._audio_local_btn.setFixedHeight(50)
        self._audio_local_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self._audio_local_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._audio_local_btn.clicked.connect(lambda: self._set_audio_engine("local"))
        audio_btns.addWidget(self._audio_local_btn)
        
        hud_col.addLayout(audio_btns)

        hud_col.addStretch()
        console_lay.addLayout(hud_col, stretch=4)

        # --- Columna Derecha: Consola de Chat y Comandos ---
        chat_col = QVBoxLayout()
        chat_col.setSpacing(6)

        chat_col.addWidget(_sec("CONSOLA DE ACTIVIDAD (LOG)"))
        self._log = LogWidget()
        chat_col.addWidget(self._log, stretch=1)

        sep_chat1 = QFrame(); sep_chat1.setFrameShape(QFrame.Shape.HLine)
        sep_chat1.setStyleSheet(f"color: {C.BORDER}; margin: 2px 0;")
        chat_col.addWidget(sep_chat1)

        self._chat_bar = ChatBarWidget(self)
        self._chat_bar.send_requested.connect(self._send_text)
        self._chat_bar.file_selected.connect(self._on_file_selected)
        self._chat_bar.folder_selected.connect(self._on_folder_selected)
        self._chat_bar.tool_command_requested.connect(self._insert_tool_cmd)
        self._chat_bar.provider_changed.connect(self._switch_provider)
        self._chat_bar.permissions_requested.connect(self._show_permissions)
        
        # Link aliases
        self._llm_toggle_btn = self._chat_bar.llm_toggle_btn
        self._llm_toggle_btn.clicked.connect(self._toggle_llm_state)
        
        self._right_model_combo = self._chat_bar.model_combo
        self._right_model_combo.currentIndexChanged.connect(self._on_right_model_changed)
        
        chat_col.addWidget(self._chat_bar)
        
        self._update_audio_toggles()
        
        saved_prov = cfg.get("selected_provider", "ollama")
        if saved_prov == "gemini": saved_prov = "ollama"
        idx = self._chat_bar.provider_combo.findText(saved_prov, Qt.MatchFlag.MatchContains | Qt.MatchFlag.MatchFixedString)
        if idx >= 0:
            self._chat_bar.provider_combo.setCurrentIndex(idx)
        else:
            # No combo signal fired — run refresh manually
            self._refresh_right_model_combo(saved_prov)

        console_lay.addLayout(chat_col, stretch=6)

        return console_widget

    def _on_volume_changed(self, val: int):
        self._vol_label.setText(f"{val}%")
        try:
            save_config({"audio_volume": val})
            if hasattr(self, "_settings_panel") and hasattr(self._settings_panel, "_volume_slider"):
                self._settings_panel._volume_slider.blockSignals(True)
                self._settings_panel._volume_slider.setValue(val)
                self._settings_panel._vol_label.setText(f"{val}%")
                self._settings_panel._volume_slider.blockSignals(False)
        except Exception:
            pass

    def _insert_tool_cmd(self, cmd_prefix: str):
        self._chat_bar.text_input.setText(cmd_prefix)
        self._chat_bar.text_input.setFocus()
        
    def _set_audio_engine(self, mode: str, trigger_callback: bool = True):
        if mode == "gemini":
            save_config({"stt_engine": "gemini", "tts_engine": "gemini"})
            self._log.append_log("SYS: Motores de audio configurados a Gemini Cloud.")
        else:
            save_config({"stt_engine": "whisper", "tts_engine": "piper"})
            self._log.append_log("SYS: Motores de audio configurados a Whisper / Piper local.")
        
        self._update_audio_toggles()
        
        if trigger_callback and hasattr(self, '_on_provider_changed') and self._on_provider_changed:
            cfg = load_config()
            provider = cfg.get("selected_provider", "ollama")
            self._on_provider_changed(provider)

    def _update_audio_toggles(self):
        if not hasattr(self, "_audio_gemini_btn"): return
        cfg = load_config()
        stt = cfg.get("stt_engine", "gemini")
        
        if stt == "gemini":
            self._audio_gemini_btn.setStyleSheet(f"""
                QPushButton {{ background: {C.PRI}; color: #001a22; border: none; border-radius: 10px; }}
            """)
            self._audio_local_btn.setStyleSheet(f"""
                QPushButton {{ background: #000d12; color: {C.TEXT_DIM}; border: 1px solid {C.BORDER}; border-radius: 10px; }}
                QPushButton:hover {{ color: {C.TEXT}; border-color: {C.BORDER_B}; }}
            """)
        else:
            self._audio_local_btn.setStyleSheet(f"""
                QPushButton {{ background: {C.GREEN}; color: #001a0d; border: none; border-radius: 10px; }}
            """)
            self._audio_gemini_btn.setStyleSheet(f"""
                QPushButton {{ background: #000d12; color: {C.TEXT_DIM}; border: 1px solid {C.BORDER}; border-radius: 10px; }}
                QPushButton:hover {{ color: {C.TEXT}; border-color: {C.BORDER_B}; }}
            """)

    def _build_footer(self) -> QWidget:
        w = QWidget()
        w.setFixedHeight(30)
        w.setStyleSheet(f"background: {C.DARK}; border-top: 1px solid {C.BORDER};")
        lay = QHBoxLayout(w); lay.setContentsMargins(10, 0, 10, 0); lay.setSpacing(6)

        def _ft_btn(txt, color, tooltip, cb):
            btn = QPushButton(txt)
            btn.setFixedHeight(28)
            btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setToolTip(tooltip)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; color: {color};
                    border: 1px solid {C.BORDER}; border-radius: 10px;
                    padding: 0px 8px;
                }}
                QPushButton:hover {{
                    background: {color}18; border: 1px solid {color};
                }}
            """)
            btn.clicked.connect(cb)
            return btn

        lay.addWidget(_ft_btn("⟳ RESET", C.ACC, "Restart the AI engine", self._on_reset))
        lay.addWidget(_ft_btn("⚙ CONFIG", C.PRI, "Open settings panel", self._on_toggle_config))

        # ── Persistent mute indicator ──
        self._mute_indicator = QLabel("● MIC ACTIVE")
        self._mute_indicator.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self._mute_indicator.setStyleSheet(
            f"color: {C.GREEN}; background: transparent; padding: 0px 6px;"
        )
        lay.addWidget(self._mute_indicator)

        def _fl(txt, color=C.TEXT_MED):
            l = QLabel(txt); l.setFont(QFont("Segoe UI", 10))
            l.setStyleSheet(f"color: {color}; background: transparent;")
            return l

        lay.addWidget(_fl("[F4] Mute  ·  [F11] Fullscreen"))
        lay.addStretch()
        lay.addWidget(_fl("MARK XL  ·  MULTI-PROVIDER"))
        return w

    def _on_reset(self):
        """Reset: trigger engine restart with the current provider."""
        cfg = load_config()
        current = cfg.get("selected_provider", "gemini")
        self._switch_provider(current)
        self._log.append_log("SYS: Engine reset triggered.")

    def _on_toggle_config(self):
        """Toggle between Console and Config tabs."""
        if hasattr(self, '_settings_panel'):
            is_visible = self._settings_panel.isVisible()
            self._settings_panel.setVisible(not is_visible)
            if not is_visible:
                self._log.append_log("SYS: Panel de ajustes abierto.")
            else:
                self._log.append_log("SYS: Panel de ajustes cerrado.")

    def _refresh_right_model_combo(self, provider: str):
        """Populate the right-panel model combo based on the active provider."""
        self._right_model_combo.blockSignals(True)
        self._right_model_combo.clear()
        cfg = load_config()
        saved_model = get_model(provider)

        if provider == "openrouter":
            self._right_model_combo.setVisible(True)
            # Use the shared catalogue — same list as the config tab
            _populate_or_combo(self._right_model_combo, saved_model or _OR_FREE_MODELS[0][0])
        elif provider == "ollama":
            self._right_model_combo.setVisible(True)
            try:
                res = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=3)
                if res.returncode == 0:
                    lines = res.stdout.strip().split("\n")
                    for line in lines[1:]:
                        parts = line.split()
                        if parts:
                            model_id = parts[0].strip()
                            display = model_id.replace(":latest", "")
                            self._right_model_combo.addItem(display, model_id)
            except Exception:
                pass
                
            # If nothing was loaded but we have a saved model, add it as fallback
            if self._right_model_combo.count() == 0 and saved_model:
                self._right_model_combo.addItem(saved_model.replace(":latest", ""), saved_model)
                
            for i in range(self._right_model_combo.count()):
                if self._right_model_combo.itemData(i) == saved_model or self._right_model_combo.itemText(i) == saved_model:
                    self._right_model_combo.setCurrentIndex(i)
                    break
        elif provider == "lmstudio":
            self._right_model_combo.setVisible(True)
            # Populate with locally downloaded models
            lm_models = get_downloaded_models()
            if lm_models:
                for m in lm_models:
                    self._right_model_combo.addItem(m["name"], m["id"])
                for i in range(self._right_model_combo.count()):
                    if self._right_model_combo.itemData(i) == saved_model:
                        self._right_model_combo.setCurrentIndex(i)
                        break
                else:
                    self._right_model_combo.setCurrentIndex(0)
            else:
                self._right_model_combo.addItem("Local Model (loaded)", "local-model")
        else:
            # Gemini: model is fixed, hide the combo
            self._right_model_combo.setVisible(False)

        self._right_model_combo.blockSignals(False)
        # Persist the model if none was saved yet for this provider
        selected = self._right_model_combo.currentData()
        if selected and not saved_model:
            set_model(selected, provider)

    def _on_right_model_changed(self):
        """Save model selection from the right panel combo, sync config-tab, restart engine."""
        model_id = self._right_model_combo.currentData()
        if model_id:
            cfg = load_config()
            provider = cfg.get("selected_provider", "gemini")
            set_model(model_id, provider)
            short = model_id.split("/")[-1].split(":")[0]
            self._log.append_log(f"SYS: Model set to {short}")
            # Keep the config-tab combo in sync
            config_bar = getattr(self, '_settings_panel', None)
            if config_bar:
                if provider == "openrouter" and hasattr(config_bar, '_or_model_combo'):
                    _populate_or_combo(config_bar._or_model_combo, model_id)
                elif provider == "lmstudio" and hasattr(config_bar, '_lm_model_combo'):
                    # Sync LM Studio config-tab combo
                    config_bar._lm_model_combo.blockSignals(True)
                    for i in range(config_bar._lm_model_combo.count()):
                        if config_bar._lm_model_combo.itemData(i) == model_id:
                            config_bar._lm_model_combo.setCurrentIndex(i)
                            break
                    config_bar._lm_model_combo.blockSignals(False)
            # Avoid engine restart to keep chat history intact.
            # The engine will dynamically pick up the new model on the next message.

    def _on_file_selected(self, path: str):
        self._current_file = path
        p    = Path(path)
        cat  = _file_category(p)
        icon, _ = _FILE_ICONS.get(cat, _FILE_ICONS["unknown"])
        size = _fmt_size(p.stat().st_size)
        self._log.append_log(f"📎 {icon} {p.name} ({size}) — {cat}")
        if self.on_text_command:
            msg = (
                f"[FILE_UPLOADED] path={path} | name={p.name} | "
                f"type={p.suffix.lstrip('.')} | size={size} | "
                f"Briefly tell the user you can see the file '{p.name}' "
                f"({size}) has been uploaded and ask what they'd like to do with it."
            )
            threading.Thread(target=self.on_text_command, args=(msg,), daemon=True).start()

    def _on_folder_selected(self, path: str):
        self._current_file = path
        from pathlib import Path as _P
        p = _P(path)
        self._log.append_log(f"📁 Carpeta seleccionada: {p.name} — {_fmt_size(_P(path).stat().st_size) if _P(path).stat else '...'}")
        if self.on_text_command:
            msg = (
                f"[FOLDER_UPLOADED] path={path} | name={p.name} | "
                f"The user has selected a folder '{p.name}'. Ask what they'd like to do with it."
            )
            threading.Thread(target=self.on_text_command, args=(msg,), daemon=True).start()

    def _show_permissions(self):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "🛡 Panel de Permisos",
            "⚙ Permisos disponibles:\n\n"
            "• 🎙 Micrófono: Activado\n"
            "• 📷 Captura de pantalla: Activada\n"
            "• 💻 Control del sistema: Restringido\n"
            "• 📁 Acceso a archivos: Permitido\n\n"
            "🔐 Próximamente: permisos granulares por proveedor y agente."
        )

    def _toggle_mute(self):
        self._muted = not self._muted
        self.hud.muted = self._muted
        self._style_mute_btn()
        self._update_mute_indicator()
        if self._muted:
            self._apply_state("MUTED")
            self._log.append_log("SYS: Microphone muted.")
        else:
            self._apply_state("LISTENING")
            self._log.append_log("SYS: Microphone active.")

    def _update_mute_indicator(self):
        """Actualiza el indicador persistente de mute en el footer."""
        if not hasattr(self, '_mute_indicator'):
            return
        if self._muted:
            self._mute_indicator.setText("● MIC MUTED")
            self._mute_indicator.setStyleSheet(
                f"color: {C.MUTED_C}; background: transparent; padding: 0px 6px;"
            )
        else:
            self._mute_indicator.setText("● MIC ACTIVE")
            self._mute_indicator.setStyleSheet(
                f"color: {C.GREEN}; background: transparent; padding: 0px 6px;"
            )

    def _style_mute_btn(self):
        if self._muted:
            self._mute_btn.setText("🔇  MICROPHONE MUTED")
            self._mute_btn.setStyleSheet(f"""
                QPushButton {{
                    background: #140006; color: {C.MUTED_C};
                    border: 1px solid {C.MUTED_C}; border-radius: 10px;
                }}
            """)
        else:
            self._mute_btn.setText("🎙  MICROPHONE ACTIVE")
            self._mute_btn.setStyleSheet(f"""
                QPushButton {{
                    background: #00140a; color: {C.GREEN};
                    border: 1px solid {C.GREEN}; border-radius: 10px;
                }}
                QPushButton:hover {{ background: #001f10; }}
            """)

    def _send_text(self, txt: str):
        if not txt: return
        self._log.append_log(f"You: {txt}")
        if self.on_text_command:
            threading.Thread(target=self.on_text_command, args=(txt,), daemon=True).start()

    def _apply_state(self, state: str):
        self._current_state = state
        self.hud.state    = state
        self.hud.speaking = (state == "SPEAKING")
        self._log.set_thinking(state == "THINKING")

    def _update_provider_status(self, statuses: dict):
        self._provider_statuses = statuses

    def _check_config(self) -> bool:
        return is_configured()

    def _show_setup(self):
        ov = SetupOverlay(self.centralWidget())
        cw = self.centralWidget()
        ow, oh = 480, 480
        ov.setGeometry(
            (cw.width()  - ow) // 2,
            (cw.height() - oh) // 2,
            ow, oh,
        )
        ov.done.connect(self._on_setup_done)
        ov.show()
        self._overlay = ov

    def _on_setup_done(self, provider: str, os_name: str,
                       gemini_key: str, ollama_url: str,
                       or_key: str, _model: str):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        save_config({
            "selected_provider": provider,
            "os_system": os_name,
            "gemini_api_key": gemini_key,
            "ollama_url": ollama_url or "http://localhost:11434",
            "openrouter_api_key": or_key,
        })
        self._ready = True
        if self._overlay:
            self._overlay.hide()
            self._overlay = None
        self._apply_state("LISTENING")
        prov_name = {"gemini": "Gemini", "ollama": "Ollama", "openrouter": "OpenRouter", "lmstudio": "LM Studio"}.get(provider, provider)
        self._log.append_log(f"SYS: Initialised. Provider={prov_name} OS={os_name.upper()}.")
        # Update provider indicator
        if hasattr(self, '_provider_lbl'):
            self._provider_lbl.setText(f"◈  {prov_name.upper()}")
        if hasattr(self, '_settings_panel'):
            self._settings_panel.update_status(provider)

    def closeEvent(self, event):
        if hasattr(self, "_status_worker") and self._status_worker:
            self._status_worker.stop()
        super().closeEvent(event)

    def _on_model_action_clicked(self):
        cfg = load_config()
        active = cfg.get("selected_provider", "ollama")
        if active == "ollama":
            from PyQt6.QtWidgets import QFileDialog
            import os, subprocess
            
            # Asegurar que Ollama esté corriendo
            def _start_ollama():
                if _OS == "Windows":
                    ollama_app = os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\ollama app.exe")
                    if os.path.exists(ollama_app):
                        subprocess.Popen([ollama_app])
                elif _OS == "Darwin":
                    subprocess.Popen(["open", "-a", "Ollama"])
            
            import threading
            threading.Thread(target=_start_ollama, daemon=True).start()

            base_path = os.path.expanduser("~/.ollama/models/manifests/registry.ollama.ai/library")
            if _OS == "Windows":
                base_path = os.path.expanduser("~\\.ollama\\models\\manifests\\registry.ollama.ai\\library")
                
            if not os.path.exists(base_path):
                os.makedirs(base_path, exist_ok=True)
                
            file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Modelo de Ollama", base_path)
            if file_path:
                try:
                    file_path_norm = os.path.normpath(file_path)
                    base_path_norm = os.path.normpath(base_path)
                    if file_path_norm.startswith(base_path_norm):
                        rel_path = os.path.relpath(file_path_norm, base_path_norm)
                        model_name = rel_path.replace(os.sep, ':')
                        if model_name:
                            self._right_model_combo.addItem(model_name, model_name)
                            self._right_model_combo.setCurrentIndex(self._right_model_combo.count() - 1)
                except Exception:
                    pass
            
        elif active == "lmstudio":
            model_id = self._right_model_combo.currentData()
            if not model_id:
                model_id = self._right_model_combo.currentText()
                
            def _setup_lm_studio():
                lms_exe_path = os.path.expandvars(r"%LOCALAPPDATA%\LM-Studio\LM Studio.exe")
                if os.path.exists(lms_exe_path):
                    subprocess.Popen([lms_exe_path])
                
                lms_cli_path = os.path.expanduser(r"~/.lmstudio/bin/lms.exe")
                if os.path.exists(lms_cli_path):
                    # Start server
                    subprocess.Popen([lms_cli_path, "server", "start"], creationflags=0x08000000)
                    import time
                    time.sleep(3) # Wait for server to init
                    if model_id and model_id != "local-model":
                        subprocess.Popen([lms_cli_path, "load", str(model_id)], creationflags=0x08000000)
                else:
                    path = os.path.expanduser("~/.cache/lm-studio/models")
                    if not os.path.exists(path):
                        os.makedirs(path, exist_ok=True)
                    if _OS == "Windows": os.startfile(path)
                    elif _OS == "Darwin": subprocess.run(["open", path])
                    else: subprocess.run(["xdg-open", path])
            
            import threading
            threading.Thread(target=_setup_lm_studio, daemon=True).start()
            
        elif active == "openrouter":
            import webbrowser
            webbrowser.open("https://openrouter.ai/models")


class _RootShim:
    def __init__(self, app: QApplication):
        self._app = app
    def mainloop(self):
        self._app.exec()
    def protocol(self, *_):
        pass


class JarvisUI:
    def __init__(self, face_path: str, size=None):
        self._app = QApplication.instance() or QApplication(sys.argv)
        self._win = MainWindow(face_path)
        self._win.show()
        self.root = _RootShim(self._app)

    @property
    def muted(self) -> bool:
        return self._win._muted

    @muted.setter
    def muted(self, v: bool):
        if v != self._win._muted:
            self._win._toggle_mute()

    @property
    def current_file(self) -> str | None:
        return self._win._current_file

    @property
    def on_text_command(self):
        return self._win.on_text_command

    @on_text_command.setter
    def on_text_command(self, cb):
        self._win.on_text_command = cb

    @property
    def on_provider_changed(self):
        return self._win.on_provider_changed

    @on_provider_changed.setter
    def on_provider_changed(self, cb):
        self._win.on_provider_changed = cb
        self._win._on_provider_changed = cb

    def set_state(self, state: str):
        self._win._state_sig.emit(state)

    def write_log(self, text: str):
        self._win._log_sig.emit(text)

    def wait_for_api_key(self):
        while not self._win._ready:
            time.sleep(0.1)

    def start_speaking(self):
        self.set_state("SPEAKING")

    def stop_speaking(self):
        if not self.muted:
            self.set_state("LISTENING")
