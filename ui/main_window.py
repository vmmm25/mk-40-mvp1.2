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
    QRadialGradient, QShortcut, QAction,
)
from PyQt6.QtWidgets import (
    QApplication, QComboBox, QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QProgressBar, QPushButton, QSizePolicy, QTextEdit, QVBoxLayout, QWidget,
    QTabWidget, QSlider, QMenu,
)

from memory.config_manager import load_config, save_config, get_model, set_model, is_configured, get_lmstudio_url
from ui.theme import Theme as C, qcol, PROVIDER_COLORS, get_openrouter_color as _get_openrouter_color
from ui.wave_canvas import WaveCanvas
from ui.config_toolbar import ConfigToolbar, _OR_FREE_MODELS, _populate_or_combo, _COMBO_STYLE
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
from ui.file_drop import FileDropZone, file_category as _file_category, fmt_size as _fmt_size
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
        self._update_llm_ui()
        prov_name = {"gemini": "GEMINI", "ollama": "OLLAMA", "openrouter": "OPENROUTER", "lmstudio": "LM STUDIO"}.get(provider, provider)
        self._provider_lbl.setText(f"◈  {prov_name}")
        # Update model combo for the new provider
        self._refresh_right_model_combo(provider)
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
            self._llm_toggle_btn.setText("● LLM ONLINE")
            self._llm_toggle_btn.setStyleSheet(f"""
                QPushButton {{
                    background: #001a0d; color: {C.GREEN};
                    border: 1px solid {C.GREEN}; border-radius: 3px; padding: 0px 8px;
                }}
                QPushButton:hover {{ background: {C.GREEN}; color: #000; }}
            """)
            if hasattr(self, "_ai_core_lbl"):
                self._ai_core_lbl.setText("AI CORE\nACTIVE")
                self._ai_core_lbl.setStyleSheet(
                    f"color: {C.GREEN}; background: {C.PANEL2};"
                    f"border: 1px solid {C.BORDER_A}; border-radius: 3px; padding: 4px;"
                )
            
            # Enable buttons and restore highlight
            for btn in [self._ollama_btn, self._or_btn, self._lm_btn]:
                btn.setEnabled(True)
                btn.setToolTip("Seleccionar proveedor")
            self._highlight_provider(selected_provider)
        else:
            self._llm_toggle_btn.setText("○ LLM OFFLINE")
            self._llm_toggle_btn.setStyleSheet(f"""
                QPushButton {{
                    background: #1a0005; color: {C.RED};
                    border: 1px solid {C.RED}; border-radius: 3px; padding: 0px 8px;
                }}
                QPushButton:hover {{ background: {C.RED}; color: #fff; }}
            """)
            if hasattr(self, "_ai_core_lbl"):
                self._ai_core_lbl.setText("AI CORE\nINACTIVE")
                self._ai_core_lbl.setStyleSheet(
                    f"color: {C.RED}; background: {C.PANEL2};"
                    f"border: 1px solid {C.BORDER_A}; border-radius: 3px; padding: 4px;"
                )
            
            # Highlight gemini (which is active)
            self._highlight_provider("gemini")
            
            # Disable LLM buttons and apply gray out style
            for btn in [self._ollama_btn, self._or_btn, self._lm_btn]:
                btn.setEnabled(False)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: #050b0d; color: {C.TEXT_DIM};
                        border: 1px solid {C.BORDER_A}; border-radius: 3px;
                    }}
                """)
                btn.setToolTip("Activa LLM ONLINE para usar otros proveedores")

    def _highlight_provider(self, provider: str):
        """Highlight the active provider button."""
        colors = {"gemini": C.PRI, "ollama": C.ACC2, "openrouter": C.GREEN, "lmstudio": C.ACC}
        bg_map = {"gemini": "#001a22", "ollama": "#1a1400", "openrouter": "#001a0d", "lmstudio": "#1a0e00"}
        btns = {"gemini": self._gemini_btn, "ollama": self._ollama_btn, "openrouter": self._or_btn, "lmstudio": self._lm_btn}
        for k, btn in btns.items():
            if k == provider:
                fg = colors[k]
                bg = bg_map[k]
                btn.setStyleSheet(f"""
                    QPushButton {{ background: {fg}; color: {bg};
                        border: none; border-radius: 3px; font-weight: bold; }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{ background: #000d12; color: {C.TEXT_DIM};
                        border: 1px solid {C.BORDER}; border-radius: 3px; }}
                    QPushButton:hover {{ color: {C.TEXT}; border: 1px solid {C.BORDER_B}; }}
                """)

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
        title = QLabel("J.A.R.V.I.S")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {C.PRI}; background: transparent;")
        mid.addWidget(title)
        sub = QLabel("Just A Rather Very Intelligent System")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setFont(QFont("Segoe UI", 11))
        sub.setStyleSheet(f"color: {C.PRI_DIM}; background: transparent;")
        mid.addWidget(sub)
        lay.addLayout(mid)
        lay.addStretch()

        right_col = QVBoxLayout(); right_col.setSpacing(2)
        self._clock_lbl = QLabel("00:00:00")
        self._clock_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self._clock_lbl.setStyleSheet(f"color: {C.PRI}; background: transparent;")
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

        hdr = QLabel("◈ SYS MONITOR")
        hdr.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        hdr.setStyleSheet(f"color: {C.PRI}; background: transparent; "
                          f"border-bottom: 1px solid {C.BORDER}; padding-bottom: 4px;")
        lay.addWidget(hdr)
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
            f"background: {C.PANEL2}; border: 1px solid {C.BORDER}; border-radius: 4px;"
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
        self._ai_core_lbl.setStyleSheet(
            f"color: {C.GREEN}; background: {C.PANEL2};"
            f"border: 1px solid {C.BORDER_A}; border-radius: 3px; padding: 4px;"
        )
        lay.addWidget(self._ai_core_lbl)

        for txt, col in [
            ("SEC\nCLEARED",        C.PRI),
            ("PROTOCOL\nXXXVIII",   C.TEXT_DIM),
        ]:
            lbl = QLabel(txt)
            lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(
                f"color: {col}; background: {C.PANEL2};"
                f"border: 1px solid {C.BORDER_A}; border-radius: 3px; padding: 4px;"
            )
            lay.addWidget(lbl)

        return w

    def _build_main_content(self, face_path: str) -> QWidget:
        # Create the main TabWidget that lives at the top
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {C.BORDER};
                background: {C.BG};
            }}
            QTabBar::tab {{
                background: {C.DARK};
                color: {C.TEXT_DIM};
                border: 1px solid {C.BORDER};
                border-bottom: none;
                padding: 10px 24px;
                font: bold 10pt 'Segoe UI';
            }}
            QTabBar::tab:selected {{
                background: {C.PANEL2};
                color: {C.PRI};
                border-color: {C.BORDER_B};
            }}
            QTabBar::tab:hover {{
                color: {C.TEXT_MED};
            }}
        """)

        # ── TAB 1: INTERACCIÓN Y CONSOLA ──
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
                border: 1px solid {C.BORDER}; border-radius: 3px;
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
        self._vol_label = QLabel(f"{saved_vol}%")
        self._vol_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self._vol_label.setStyleSheet(f"color: {C.PRI}; background: transparent;")
        self._vol_label.setFixedWidth(40)
        vol_row.addWidget(self._vol_label)
        hud_col.addLayout(vol_row)

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

        # --- NEW ACTIONS ROW ---
        actions_row = QHBoxLayout(); actions_row.setSpacing(12)
        
        # 1. File Drop Zone (Square)
        self._drop_zone = FileDropZone()
        self._drop_zone.file_selected.connect(self._on_file_selected)
        self._drop_zone.setFixedSize(120, 120)
        actions_row.addWidget(self._drop_zone)
        
        # 2. File Info
        fd_info = QVBoxLayout()
        fd_info.addWidget(_sec("CARGAR ARCHIVOS"))
        self._file_hint = QLabel("No hay archivo cargado — arrastra o haz clic para subir")
        self._file_hint.setFont(QFont("Segoe UI", 9))
        self._file_hint.setStyleSheet(f"color: {C.TEXT_MED}; background: transparent;")
        self._file_hint.setWordWrap(True)
        fd_info.addWidget(self._file_hint)
        fd_info.addStretch()
        actions_row.addLayout(fd_info, stretch=2)
        
        # 3. Audio Toggles
        audio_col = QVBoxLayout(); audio_col.setSpacing(4)
        audio_col.addWidget(_sec("MOTOR DE AUDIO"))
        
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
        
        audio_col.addLayout(audio_btns)
        audio_col.addStretch()
        actions_row.addLayout(audio_col, stretch=2)
        
        chat_col.addLayout(actions_row)
        
        self._update_audio_toggles()

        sep_chat2 = QFrame(); sep_chat2.setFrameShape(QFrame.Shape.HLine)
        sep_chat2.setStyleSheet(f"color: {C.BORDER}; margin: 2px 0;")
        chat_col.addWidget(sep_chat2)

        # Provider and Model selector
        chat_col.addWidget(_sec("SELECCIONAR PROVEEDOR DE IA"))
        prov_row = QHBoxLayout(); prov_row.setSpacing(4)

        def _prov_btn(label, provider):
            btn = QPushButton(label)
            btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            btn.setFixedHeight(28)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda: self._switch_provider(provider))
            return btn

        self._ollama_btn = _prov_btn("OLLAMA (OLL)", "ollama")
        self._or_btn = _prov_btn("OPENROUTER (OR)", "openrouter")
        self._lm_btn = _prov_btn("LM STUDIO (LM)", "lmstudio")
        self._gemini_btn = QPushButton(); self._gemini_btn.hide() # Dummy for _highlight_provider

        for btn in [self._ollama_btn, self._or_btn, self._lm_btn]:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: #000d12; color: {C.TEXT_DIM};
                    border: 1px solid {C.BORDER}; border-radius: 3px;
                }}
                QPushButton:hover {{ color: {C.TEXT}; border-color: {C.BORDER_B}; }}
            """)
            prov_row.addWidget(btn)

        prov_row.addSpacing(12)

        self._llm_toggle_btn = QPushButton()
        self._llm_toggle_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self._llm_toggle_btn.setFixedHeight(28)
        self._llm_toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._llm_toggle_btn.clicked.connect(self._toggle_llm_state)
        prov_row.addWidget(self._llm_toggle_btn)

        chat_col.addLayout(prov_row)

        model_row = QHBoxLayout(); model_row.setSpacing(8)
        self._provider_lbl = QLabel("◈  OLLAMA")
        self._provider_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._provider_lbl.setStyleSheet(f"color: {C.PRI}; background: transparent;")
        model_row.addWidget(self._provider_lbl)

        self._right_model_combo = QComboBox()
        self._right_model_combo.setFont(QFont("Segoe UI", 10))
        self._right_model_combo.setFixedHeight(28)
        self._right_model_combo.setStyleSheet(_COMBO_STYLE)
        self._right_model_combo.currentIndexChanged.connect(self._on_right_model_changed)
        model_row.addWidget(self._right_model_combo, stretch=1)
        
        self._model_action_btn = QPushButton("📁")
        self._model_action_btn.setFont(QFont("Segoe UI", 10))
        self._model_action_btn.setFixedSize(28, 28)
        self._model_action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._model_action_btn.setStyleSheet(f"""
            QPushButton {{
                background: #000d12; color: {C.PRI};
                border: 1px solid {C.BORDER}; border-radius: 3px;
            }}
            QPushButton:hover {{ background: {C.PRI}; color: #000; }}
        """)
        self._model_action_btn.clicked.connect(self._on_model_action_clicked)
        model_row.addWidget(self._model_action_btn)
        chat_col.addLayout(model_row)

        saved_prov = cfg.get("selected_provider", "ollama")
        if saved_prov == "gemini": saved_prov = "ollama" # Since Gemini is removed
        self._refresh_right_model_combo(saved_prov)
        self._highlight_provider(saved_prov)

        sep_chat3 = QFrame(); sep_chat3.setFrameShape(QFrame.Shape.HLine)
        sep_chat3.setStyleSheet(f"color: {C.BORDER}; margin: 2px 0;")
        chat_col.addWidget(sep_chat3)

        chat_col.addWidget(_sec("ENTRADA DE COMANDOS / TEXTO"))
        chat_col.addLayout(self._build_input_row())

        console_lay.addLayout(chat_col, stretch=6)

        tabs.addTab(console_widget, "💬  CONSOLA INTERACTIVA")

        # ── TAB 2: AJUSTES ──
        from ui.config_toolbar import ConfigToolbar
        self._config_bar = ConfigToolbar(main_window=self)
        tabs.addTab(self._config_bar, "⚙  AJUSTES DE MOTOR Y VOZ")
        return tabs

    def _on_volume_changed(self, val: int):
        self._vol_label.setText(f"{val}%")
        try:
            save_config({"audio_volume": val})
            if hasattr(self, "_config_bar") and hasattr(self._config_bar, "_volume_slider"):
                self._config_bar._volume_slider.blockSignals(True)
                self._config_bar._volume_slider.setValue(val)
                self._config_bar._vol_label.setText(f"{val}%")
                self._config_bar._volume_slider.blockSignals(False)
        except Exception:
            pass

    def _build_input_row(self) -> QHBoxLayout:
        row = QHBoxLayout(); row.setSpacing(5)

        # The "+" Tools button
        self._tools_btn = QPushButton("+")
        self._tools_btn.setFixedSize(34, 34)
        self._tools_btn.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self._tools_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._tools_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C.PANEL}; color: {C.GREEN};
                border: 1px solid {C.GREEN}; border-radius: 3px;
            }}
            QPushButton:hover {{ background: {C.GREEN}22; border: 1px solid #00ffaa; }}
            QPushButton::menu-indicator {{ image: none; }}
        """)
        # Tools menu
        self._tools_menu = QMenu(self)
        self._tools_menu.setStyleSheet(f"""
            QMenu {{
                background-color: {C.DARK};
                color: {C.TEXT};
                border: 1px solid {C.BORDER_B};
                padding: 4px;
            }}
            QMenu::item {{
                padding: 6px 24px 6px 12px;
                background: transparent;
                font: bold 10pt "Segoe UI";
            }}
            QMenu::item:selected {{
                background-color: {C.PRI_GHO};
                color: {C.PRI};
            }}
        """)
        
        for action_name, cmd in [
            ("🖼 Crear imagen", "/imagen "),
            ("🎵 Crear audio", "/audio "),
            ("🎬 Crear video", "/video "),
            ("🤖 Agentes", "/agentes "),
            ("📁 Sesiones", "/sesiones ")
        ]:
            act = QAction(action_name, self)
            act.triggered.connect(lambda checked, c=cmd: self._insert_tool_cmd(c))
            self._tools_menu.addAction(act)
            
        self._tools_btn.setMenu(self._tools_menu)
        row.addWidget(self._tools_btn)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Type a command or question…")
        self._input.setFont(QFont("Segoe UI", 12))
        self._input.setFixedHeight(34)
        self._input.setStyleSheet(f"""
            QLineEdit {{
                background: #000d14; color: {C.WHITE};
                border: 1px solid {C.BORDER}; border-radius: 3px; padding: 3px 7px;
            }}
            QLineEdit:focus {{ border: 1px solid {C.PRI}; }}
        """)
        self._input.returnPressed.connect(self._send)
        row.addWidget(self._input)

        send = QPushButton("▸")
        send.setFixedSize(34, 34)
        send.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        send.setCursor(Qt.CursorShape.PointingHandCursor)
        send.setStyleSheet(f"""
            QPushButton {{
                background: {C.PANEL}; color: {C.PRI};
                border: 1px solid {C.PRI_DIM}; border-radius: 3px;
            }}
            QPushButton:hover {{ background: {C.PRI_GHO}; border: 1px solid {C.PRI}; }}
        """)
        send.clicked.connect(self._send)
        row.addWidget(send)
        return row

    def _insert_tool_cmd(self, cmd_prefix: str):
        self._input.setText(cmd_prefix)
        self._input.setFocus()
        
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
                QPushButton {{ background: {C.PRI}; color: #001a22; border: none; border-radius: 4px; }}
            """)
            self._audio_local_btn.setStyleSheet(f"""
                QPushButton {{ background: #000d12; color: {C.TEXT_DIM}; border: 1px solid {C.BORDER}; border-radius: 4px; }}
                QPushButton:hover {{ color: {C.TEXT}; border-color: {C.BORDER_B}; }}
            """)
        else:
            self._audio_local_btn.setStyleSheet(f"""
                QPushButton {{ background: {C.GREEN}; color: #001a0d; border: none; border-radius: 4px; }}
            """)
            self._audio_gemini_btn.setStyleSheet(f"""
                QPushButton {{ background: #000d12; color: {C.TEXT_DIM}; border: 1px solid {C.BORDER}; border-radius: 4px; }}
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
                    border: 1px solid {C.BORDER}; border-radius: 3px;
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
        """Toggle the active tab in the right panel between Chat and Config."""
        if hasattr(self, '_right_tabs'):
            current_idx = self._right_tabs.currentIndex()
            if current_idx == 0:
                self._right_tabs.setCurrentIndex(1)
                self._log.append_log("SYS: Se abrieron los ajustes en el panel derecho.")
            else:
                self._right_tabs.setCurrentIndex(0)
                self._log.append_log("SYS: Se cerraron los ajustes.")

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
            config_bar = getattr(self, '_config_bar', None)
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
        self._file_hint.setText(f"{icon}  {p.name}  ·  {size}  ·  Tell JARVIS what to do with it")
        self._log.append_log(f"FILE: {p.name} ({size}) loaded")
        if self.on_text_command:
            msg = (
                f"[FILE_UPLOADED] path={path} | name={p.name} | "
                f"type={p.suffix.lstrip('.')} | size={size} | "
                f"Briefly tell the user you can see the file '{p.name}' "
                f"({size}) has been uploaded and ask what they'd like to do with it."
            )
            threading.Thread(target=self.on_text_command, args=(msg,), daemon=True).start()

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
                    border: 1px solid {C.MUTED_C}; border-radius: 3px;
                }}
            """)
        else:
            self._mute_btn.setText("🎙  MICROPHONE ACTIVE")
            self._mute_btn.setStyleSheet(f"""
                QPushButton {{
                    background: #00140a; color: {C.GREEN};
                    border: 1px solid {C.GREEN}; border-radius: 3px;
                }}
                QPushButton:hover {{ background: #001f10; }}
            """)

    def _send(self):
        txt = self._input.text().strip()
        if not txt: return
        self._input.clear()
        self._log.append_log(f"You: {txt}")
        if self.on_text_command:
            threading.Thread(target=self.on_text_command, args=(txt,), daemon=True).start()

    def _apply_state(self, state: str):
        self._current_state = state
        self.hud.state    = state
        self.hud.speaking = (state == "SPEAKING")
        self._refresh_provider_buttons()

    def _update_provider_status(self, statuses: dict):
        self._provider_statuses = statuses
        self._refresh_provider_buttons()

    def _refresh_provider_buttons(self):
        if not hasattr(self, '_provider_statuses'): return
        cfg = load_config()
        active = cfg.get("selected_provider", "ollama")
        is_processing = self._current_state in ("THINKING", "SPEAKING")

        def _get_dot(prov_key: str) -> str:
            if active == prov_key and is_processing: return "🟡"
            return "🟢" if self._provider_statuses.get(prov_key, False) else "🔴"

        if hasattr(self, '_ollama_btn'):
            self._ollama_btn.setText(f"{_get_dot('ollama')} OLLAMA (OLL)")
        if hasattr(self, '_lm_btn'):
            self._lm_btn.setText(f"{_get_dot('lmstudio')} LM STUDIO (LM)")
        if hasattr(self, '_or_btn'):
            self._or_btn.setText(f"{_get_dot('openrouter')} OPENROUTER (OR)")

        if hasattr(self, '_provider_lbl'):
            prov_name = {"gemini": "GEMINI", "ollama": "OLLAMA", "openrouter": "OPENROUTER", "lmstudio": "LM STUDIO"}.get(active, active)
            dot_act = _get_dot(active)
            self._provider_lbl.setText(f"{dot_act}  {prov_name}")
            
            if hasattr(self, '_model_action_btn'):
                if active == "openrouter":
                    self._model_action_btn.setText("🌐")
                    self._model_action_btn.setToolTip("Abrir OpenRouter Models en el navegador")
                else:
                    self._model_action_btn.setText("📁")
                    self._model_action_btn.setToolTip(f"Abrir carpeta de modelos de {prov_name}")

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
        if hasattr(self, '_config_bar'):
            self._config_bar.update_status(provider)

    def closeEvent(self, event):
        if hasattr(self, "_status_worker") and self._status_worker:
            self._status_worker.stop()
        super().closeEvent(event)

    def _on_model_action_clicked(self):
        cfg = load_config()
        active = cfg.get("selected_provider", "ollama")
        if active == "ollama":
            path = "~/.ollama/models"
            if _OS == "Windows": path = "~/.ollama/models"
            elif _OS == "Darwin": path = "~/.ollama/models"
            else: path = "/usr/share/ollama/.ollama/models"
            path = os.path.expanduser(path)
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
            if _OS == "Windows": os.startfile(path)
            elif _OS == "Darwin": subprocess.run(["open", path])
            else: subprocess.run(["xdg-open", path])
            
        elif active == "lmstudio":
            path = os.path.expanduser("~/.cache/lm-studio/models")
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
            if _OS == "Windows": os.startfile(path)
            elif _OS == "Darwin": subprocess.run(["open", path])
            else: subprocess.run(["xdg-open", path])
            
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
        return self._win._drop_zone.current_file()

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
