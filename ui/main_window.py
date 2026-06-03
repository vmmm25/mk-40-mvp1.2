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
    QTimer, QUrl, pyqtSignal,
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
from lmstudio_control import (
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


class _SysMetrics:
    def __init__(self):
        self.cpu  = 0.0
        self.mem  = 0.0
        self.net  = 0.0   
        self.gpu  = -1.0  
        self.tmp  = -1.0  
        self._lock = threading.Lock()
        self._last_net = psutil.net_io_counters()
        self._last_net_t = time.time()
        self._running = True
        t = threading.Thread(target=self._loop, daemon=True)
        t.start()

    def _loop(self):
        while self._running:
            try:
                self._update()
            except Exception:
                pass
            time.sleep(1.5)

    def _update(self):
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent

        nc  = psutil.net_io_counters()
        now = time.time()
        dt  = now - self._last_net_t
        if dt > 0:
            sent = (nc.bytes_sent - self._last_net.bytes_sent) / dt
            recv = (nc.bytes_recv - self._last_net.bytes_recv) / dt
            net  = (sent + recv) / (1024 * 1024)
        else:
            net = 0.0
        self._last_net   = nc
        self._last_net_t = now

        gpu = self._get_gpu()

        tmp = self._get_temp()

        with self._lock:
            self.cpu = cpu
            self.mem = mem
            self.net = net
            self.gpu = gpu
            self.tmp = tmp

    def _get_gpu(self) -> float:
        # NVIDIA
        try:
            r = subprocess.run(
                ["nvidia-smi", "--query-gpu=utilization.gpu",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=2
            )
            if r.returncode == 0:
                vals = [float(v.strip()) for v in r.stdout.strip().split("\n") if v.strip()]
                if vals:
                    return sum(vals) / len(vals)
        except Exception:
            pass

        # AMD (Linux)
        if _OS == "Linux":
            try:
                r = subprocess.run(
                    ["rocm-smi", "--showuse", "--csv"],
                    capture_output=True, text=True, timeout=2
                )
                if r.returncode == 0:
                    for line in r.stdout.strip().split("\n"):
                        parts = line.split(",")
                        if len(parts) >= 2:
                            try:
                                return float(parts[1].strip().replace("%", ""))
                            except ValueError:
                                pass
            except Exception:
                pass

            # Intel GPU (Linux)
            try:
                r = subprocess.run(
                    ["intel_gpu_top", "-J", "-s", "500"],
                    capture_output=True, text=True, timeout=1
                )
                if r.returncode == 0 and "Render/3D" in r.stdout:
                    import re
                    m = re.search(r'"busy":\s*([\d.]+)', r.stdout)
                    if m:
                        return float(m.group(1))
            except Exception:
                pass

        # macOS — powermetrics (GPU Engine)
        if _OS == "Darwin":
            try:
                r = subprocess.run(
                    ["sudo", "-n", "powermetrics", "-n", "1", "-i", "500",
                     "--samplers", "gpu_power"],
                    capture_output=True, text=True, timeout=2
                )
                if r.returncode == 0 and "GPU" in r.stdout:
                    import re
                    m = re.search(r'GPU\s+Active:\s+([\d.]+)%', r.stdout)
                    if m:
                        return float(m.group(1))
            except Exception:
                pass

        return -1.0

    def _get_temp(self) -> float:
        try:
            temps = psutil.sensors_temperatures()
            candidates = ["coretemp", "k10temp", "cpu_thermal", "acpitz",
                          "cpu-thermal", "zenpower", "it8688"]
            for name in candidates:
                if name in temps:
                    entries = temps[name]
                    if entries:
                        return entries[0].current
            for entries in temps.values():
                if entries:
                    return entries[0].current
        except Exception:
            pass
        if _OS == "Darwin":
            try:
                r = subprocess.run(
                    ["osx-cpu-temp"], capture_output=True, text=True, timeout=2
                )
                if r.returncode == 0:
                    import re
                    m = re.search(r"([\d.]+)", r.stdout)
                    if m:
                        return float(m.group(1))
            except Exception:
                pass

        if _OS == "Windows":
            try:
                r = subprocess.run(
                    ["powershell", "-Command",
                     "(Get-WmiObject MSAcpi_ThermalZoneTemperature -Namespace root/wmi).CurrentTemperature"],
                    capture_output=True, text=True, timeout=3
                )
                if r.returncode == 0 and r.stdout.strip():
                    raw = float(r.stdout.strip().split("\n")[0])
                    return (raw / 10.0) - 273.15
            except Exception:
                pass

        return -1.0

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "cpu": self.cpu,
                "mem": self.mem,
                "net": self.net,
                "gpu": self.gpu,
                "tmp": self.tmp,
            }


_metrics = _SysMetrics()


class MetricBar(QWidget):

    def __init__(self, label: str, color: str = C.PRI, parent=None):
        super().__init__(parent)
        self._label = label
        self._color = color
        self._value = 0.0       # 0–100
        self._text  = "--"
        self.setFixedHeight(38)
        self.setMinimumWidth(80)

    def set_value(self, pct: float, text: str):
        self._value = max(0.0, min(100.0, pct))
        self._text  = text
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        W, H = self.width(), self.height()

        p.setBrush(QBrush(qcol(C.PANEL2)))
        p.setPen(QPen(qcol(C.BORDER_A), 1))
        p.drawRoundedRect(QRectF(1, 1, W - 2, H - 2), 4, 4)

        bar_h   = 4
        bar_y   = H - bar_h - 5
        bar_w   = W - 12
        bar_x   = 6
        fill_w  = int(bar_w * self._value / 100)

        p.setBrush(QBrush(qcol(C.BAR_BG)))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(QRectF(bar_x, bar_y, bar_w, bar_h), 2, 2)

        if self._value > 85:
            bar_col = qcol(C.RED)
        elif self._value > 65:
            bar_col = qcol(C.ACC)
        else:
            bar_col = qcol(self._color)

        if fill_w > 0:
            p.setBrush(QBrush(bar_col))
            p.drawRoundedRect(QRectF(bar_x, bar_y, fill_w, bar_h), 2, 2)

        p.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        p.setPen(QPen(qcol(C.TEXT_DIM), 1))
        p.drawText(QRectF(8, 5, 50, 18), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self._label)

        p.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        p.setPen(QPen(bar_col if self._text != "--" else qcol(C.TEXT_DIM), 1))
        p.drawText(QRectF(0, 4, W - 6, 20), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, self._text)


class LogWidget(QTextEdit):
    _sig = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(QFont("Segoe UI", 12))
        self.setStyleSheet(f"""
            QTextEdit {{
                background: {C.PANEL};
                color: {C.TEXT};
                border: 1px solid {C.BORDER};
                border-radius: 4px;
                padding: 6px;
                selection-background-color: {C.PRI_GHO};
            }}
            QScrollBar:vertical {{
                background: {C.BG};
                width: 8px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background: {C.BORDER_B};
                border-radius: 4px;
                min-height: 20px;
            }}
        """)
        self._queue: list[str] = []
        self._typing  = False
        self._text    = ""
        self._pos     = 0
        self._tag     = "sys"
        self._tmr = QTimer(self)
        self._tmr.timeout.connect(self._step)
        self._sig.connect(self._enqueue)

    def append_log(self, text: str):
        self._sig.emit(text)

    def _enqueue(self, text: str):
        self._queue.append(text)
        if not self._typing:
            self._next()

    def _next(self):
        if not self._queue:
            self._typing = False
            return
        self._typing = True
        self._text   = self._queue.pop(0)
        self._pos    = 0
        tl = self._text.lower()
        if   tl.startswith("you:"):    self._tag = "you"
        elif tl.startswith("jarvis:"): self._tag = "ai"
        elif tl.startswith("file:"):   self._tag = "file"
        elif "err" in tl:              self._tag = "err"
        else:                          self._tag = "sys"
        self._tmr.start(6)

    def _step(self):
        if self._pos < len(self._text):
            ch  = self._text[self._pos]
            cur = self.textCursor()
            fmt = cur.charFormat()
            col = {
                "you":  qcol(C.WHITE),
                "ai":   qcol(C.PRI),
                "err":  qcol(C.RED),
                "file": qcol(C.GREEN),
                "sys":  qcol(C.ACC2),
            }.get(self._tag, qcol(C.TEXT))
            fmt.setForeground(QBrush(col))
            cur.movePosition(cur.MoveOperation.End)
            cur.insertText(ch, fmt)
            self.setTextCursor(cur)
            self.ensureCursorVisible()
            self._pos += 1
        else:
            self._tmr.stop()
            cur = self.textCursor()
            cur.movePosition(cur.MoveOperation.End)
            cur.insertText("\n")
            self.setTextCursor(cur)
            self.ensureCursorVisible()
            QTimer.singleShot(20, self._next)


_FILE_ICONS = {
    "image":   ("🖼", "#00d4ff"), "video":   ("🎬", "#ff6b00"),
    "audio":   ("🎵", "#cc44ff"), "pdf":     ("📄", "#ff4444"),
    "word":    ("📝", "#4488ff"), "excel":   ("📊", "#44bb44"),
    "code":    ("💻", "#ffcc00"), "archive": ("📦", "#ff8844"),
    "pptx":    ("📊", "#ff6622"), "text":    ("📃", "#aaaaaa"),
    "data":    ("🔧", "#88ddff"), "unknown": ("📎", "#888888"),
}
_EXT_TO_CAT = {
    **dict.fromkeys(["jpg","jpeg","png","gif","webp","bmp","tiff","svg","ico"], "image"),
    **dict.fromkeys(["mp4","avi","mov","mkv","wmv","flv","webm","m4v"],         "video"),
    **dict.fromkeys(["mp3","wav","ogg","m4a","aac","flac","wma","opus"],        "audio"),
    **dict.fromkeys(["pdf"],                                                     "pdf"),
    **dict.fromkeys(["doc","docx"],                                              "word"),
    **dict.fromkeys(["xls","xlsx","ods"],                                        "excel"),
    **dict.fromkeys(["ppt","pptx"],                                              "pptx"),
    **dict.fromkeys(["py","js","ts","jsx","tsx","html","css","java","c","cpp",
                     "cs","go","rs","rb","php","swift","kt","sh","sql","lua"],   "code"),
    **dict.fromkeys(["zip","rar","tar","gz","7z","bz2","xz"],                   "archive"),
    **dict.fromkeys(["txt","md","rst","log"],                                    "text"),
    **dict.fromkeys(["csv","tsv","json","xml"],                                  "data"),
}


def _file_category(path: Path) -> str:
    return _EXT_TO_CAT.get(path.suffix.lower().lstrip("."), "unknown")


def _fmt_size(size: int) -> str:
    if   size < 1024:    return f"{size} B"
    elif size < 1024**2: return f"{size/1024:.1f} KB"
    elif size < 1024**3: return f"{size/1024**2:.1f} MB"
    else:                return f"{size/1024**3:.1f} GB"


class FileDropZone(QWidget):
    file_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(100)
        self._current_file: str | None = None
        self._hovering  = False
        self._drag_over = False
        self._dash_offset = 0.0
        self._anim_tmr = QTimer(self)
        self._anim_tmr.timeout.connect(self._animate)
        self._anim_tmr.start(40)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._canvas = _DropCanvas(self)
        layout.addWidget(self._canvas)

    def _animate(self):
        self._dash_offset = (self._dash_offset + 0.8) % 20
        self._canvas.update()

    def dragEnterEvent(self, e: QDragEnterEvent):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
            self._drag_over = True; self._canvas.update()

    def dragLeaveEvent(self, e):
        self._drag_over = False; self._canvas.update()

    def dropEvent(self, e: QDropEvent):
        self._drag_over = False
        urls = e.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if Path(path).is_file():
                self._set_file(path)
        self._canvas.update()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._browse()

    def enterEvent(self, e):
        self._hovering = True; self._canvas.update()

    def leaveEvent(self, e):
        self._hovering = False; self._canvas.update()

    def current_file(self) -> str | None:
        return self._current_file

    def clear_file(self):
        self._current_file = None; self._canvas.update()

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select a file for JARVIS", str(Path.home()),
            "All Files (*.*);;"
            "Images (*.jpg *.jpeg *.png *.gif *.webp *.bmp *.svg);;"
            "Documents (*.pdf *.docx *.txt *.md *.pptx);;"
            "Data (*.csv *.xlsx *.json *.xml);;"
            "Code (*.py *.js *.ts *.html *.css *.java *.cpp *.go);;"
            "Audio (*.mp3 *.wav *.ogg *.m4a *.aac *.flac);;"
            "Video (*.mp4 *.avi *.mov *.mkv *.wmv *.webm);;"
            "Archives (*.zip *.rar *.tar *.gz *.7z)",
        )
        if path:
            self._set_file(path)

    def _set_file(self, path: str):
        self._current_file = path
        self._canvas.update()
        self.file_selected.emit(path)


class _DropCanvas(QWidget):
    def __init__(self, zone: FileDropZone):
        super().__init__(zone)
        self._z = zone

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        z    = self._z
        W, H = self.width(), self.height()
        pad  = 6
        rect = QRectF(pad, pad, W - pad * 2, H - pad * 2)

        bg_col = qcol("#001a24" if z._drag_over else ("#001218" if z._hovering else C.PANEL))
        p.setBrush(QBrush(bg_col)); p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(rect, 6, 6)

        if z._current_file:   border_col = qcol(C.GREEN, 200)
        elif z._drag_over:    border_col = qcol(C.PRI, 230)
        elif z._hovering:     border_col = qcol(C.BORDER_B, 200)
        else:                 border_col = qcol(C.BORDER, 160)

        pen = QPen(border_col, 1.5, Qt.PenStyle.DashLine)
        pen.setDashOffset(z._dash_offset)
        p.setPen(pen); p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(rect, 6, 6)

        if z._current_file:   self._paint_file(p, W, H)
        elif z._drag_over:    self._paint_drag_over(p, W, H)
        else:                 self._paint_idle(p, W, H, z._hovering)

    def _paint_idle(self, p, W, H, hover):
        cx, cy = W / 2, H / 2
        col = qcol(C.PRI_DIM if not hover else C.PRI)
        p.setPen(QPen(col, 2)); p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawLine(QPointF(cx, cy - 14), QPointF(cx, cy + 4))
        p.drawLine(QPointF(cx - 8, cy - 6), QPointF(cx, cy - 14))
        p.drawLine(QPointF(cx + 8, cy - 6), QPointF(cx, cy - 14))
        p.drawLine(QPointF(cx - 14, cy + 4), QPointF(cx + 14, cy + 4))
        p.setFont(QFont("Segoe UI", 11))
        p.setPen(QPen(qcol(C.PRI_DIM if not hover else C.TEXT), 1))
        p.drawText(QRectF(0, cy + 8, W, 16), Qt.AlignmentFlag.AlignCenter,
                   "Drop file here  or  Click to Browse")
        p.setFont(QFont("Segoe UI", 10))
        p.setPen(QPen(qcol("#1a4a5a"), 1))
        p.drawText(QRectF(0, cy + 24, W, 14), Qt.AlignmentFlag.AlignCenter,
                   "Images · Video · Audio · PDF · Docs · Code · Data")

    def _paint_drag_over(self, p, W, H):
        cx, cy = W / 2, H / 2
        p.setFont(QFont("Segoe UI", 20))
        p.setPen(QPen(qcol(C.PRI), 1))
        p.drawText(QRectF(0, cy - 24, W, 32), Qt.AlignmentFlag.AlignCenter, "⬇")
        p.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        p.setPen(QPen(qcol(C.PRI), 1))
        p.drawText(QRectF(0, cy + 12, W, 20), Qt.AlignmentFlag.AlignCenter, "Release to load")

    def _paint_file(self, p, W, H):
        path = Path(self._z._current_file)
        cat  = _file_category(path)
        icon, icon_col = _FILE_ICONS.get(cat, _FILE_ICONS["unknown"])
        size_str = _fmt_size(path.stat().st_size)
        ext_str  = path.suffix.upper().lstrip(".") or "FILE"

        block_x, block_w = 10, 60
        p.setFont(QFont("Segoe UI Emoji", 22) if _OS == "Windows" else QFont("Arial", 22))
        p.setPen(QPen(qcol(icon_col), 1))
        p.drawText(QRectF(block_x, 0, block_w, H), Qt.AlignmentFlag.AlignCenter, icon)

        tx = block_x + block_w + 6
        tw = W - tx - 38

        p.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        p.setPen(QPen(qcol(C.WHITE), 1))
        name = path.name if len(path.name) <= 34 else path.name[:31] + "..."
        p.drawText(QRectF(tx, H * 0.18, tw, 16),
                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, name)

        p.setFont(QFont("Segoe UI", 10))
        p.setPen(QPen(qcol(C.TEXT_DIM), 1))
        p.drawText(QRectF(tx, H * 0.18 + 18, tw, 14),
                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                   f"{ext_str}  ·  {size_str}")

        p.setFont(QFont("Segoe UI", 12))
        p.setPen(QPen(qcol("#1e5c6a"), 1))
        par = str(path.parent)
        if len(par) > 42: par = "…" + par[-41:]
        p.drawText(QRectF(tx, H * 0.18 + 34, tw, 12),
                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, par)

        p.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        p.setPen(QPen(qcol(C.RED, 180), 1))
        p.drawText(QRectF(W - 34, 0, 28, H), Qt.AlignmentFlag.AlignCenter, "✕")

    def mousePressEvent(self, e):
        z = self._z
        if z._current_file and e.pos().x() > self.width() - 34:
            z.clear_file()
        else:
            z.mousePressEvent(e)


class SetupOverlay(QWidget):
    done = pyqtSignal(str, str, str, str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"""
            SetupOverlay {{
                background: rgba(0, 6, 10, 245);
                border: 1px solid {C.BORDER_B};
                border-radius: 6px;
            }}
        """)

        detected = {"darwin": "mac", "windows": "windows"}.get(
            _OS.lower(), "linux"
        )
        self._sel_os = detected
        self._sel_provider = "gemini"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(6)

        def _lbl(txt, font_size=9, bold=False, color=C.PRI,
                 align=Qt.AlignmentFlag.AlignCenter):
            w = QLabel(txt)
            w.setAlignment(align)
            w.setFont(QFont("Segoe UI", font_size,
                            QFont.Weight.Bold if bold else QFont.Weight.Normal))
            w.setStyleSheet(f"color: {color}; background: transparent;")
            return w

        layout.addWidget(_lbl("◈  INITIALISATION REQUIRED", 12, True))
        layout.addWidget(_lbl("Configure MARK XL before first boot.", 8, color=C.PRI_DIM))
        layout.addSpacing(4)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {C.BORDER};"); layout.addWidget(sep)
        layout.addSpacing(4)

        # ── Provider Selection ──
        layout.addWidget(_lbl("AI PROVIDER", 8, color=C.TEXT_DIM,
                               align=Qt.AlignmentFlag.AlignLeft))
        prov_row = QHBoxLayout(); prov_row.setSpacing(4)
        self._prov_btns: dict[str, QPushButton] = {}
        for key, label, col in [
            ("gemini",    "GEMINI",    C.PRI),
            ("ollama",    "OLLAMA",   C.ACC2),
            ("openrouter","OPENROUTER", C.GREEN),
            ("lmstudio",  "LM STUDIO", C.ACC),
        ]:
            btn = QPushButton(label)
            btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            btn.setFixedHeight(32)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, k=key: self._sel_prov(k))
            prov_row.addWidget(btn)
            self._prov_btns[key] = btn
        layout.addLayout(prov_row)
        layout.addSpacing(4)

        # ── Stacked config fields ──
        self._config_stack = QVBoxLayout(); self._config_stack.setSpacing(4)

        # Gemini fields
        self._gemini_widget = QWidget()
        gw = QVBoxLayout(self._gemini_widget); gw.setContentsMargins(0,0,0,0); gw.setSpacing(4)
        gw.addWidget(_lbl("GEMINI API KEY", 7, color=C.PRI_DIM, align=Qt.AlignmentFlag.AlignLeft))
        self._gemini_key = QLineEdit()
        self._gemini_key.setEchoMode(QLineEdit.EchoMode.Password)
        self._gemini_key.setPlaceholderText("AIza…")
        self._gemini_key.setFont(QFont("Segoe UI", 12))
        self._gemini_key.setFixedHeight(28)
        self._gemini_key.setStyleSheet(f"""
            QLineEdit {{ background: #000d12; color: {C.TEXT};
                border: 1px solid {C.BORDER}; border-radius: 3px; padding: 3px 6px; }}
            QLineEdit:focus {{ border: 1px solid {C.PRI}; }}
        """)
        gw.addWidget(self._gemini_key)
        # Gemini supports live audio - show badge
        gw.addWidget(_lbl("✓ Live Audio · Vision · Tools", 6, color=C.GREEN_D))

        # Ollama fields
        self._ollama_widget = QWidget()
        ow = QVBoxLayout(self._ollama_widget); ow.setContentsMargins(0,0,0,0); ow.setSpacing(4)
        ow.addWidget(_lbl("OLLAMA URL", 7, color=C.ACC2, align=Qt.AlignmentFlag.AlignLeft))
        self._ollama_url = QLineEdit()
        self._ollama_url.setPlaceholderText("http://localhost:11434")
        self._ollama_url.setText("http://localhost:11434")
        self._ollama_url.setFont(QFont("Segoe UI", 12))
        self._ollama_url.setFixedHeight(28)
        self._ollama_url.setStyleSheet(f"""
            QLineEdit {{ background: #000d12; color: {C.TEXT};
                border: 1px solid {C.BORDER}; border-radius: 3px; padding: 3px 6px; }}
            QLineEdit:focus {{ border: 1px solid {C.ACC2}; }}
        """)
        ow.addWidget(self._ollama_url)
        ow.addWidget(_lbl("✓ Local Models · No API Key Needed", 6, color=C.GREEN_D))

        # OpenRouter fields
        self._or_widget = QWidget()
        orw = QVBoxLayout(self._or_widget); orw.setContentsMargins(0,0,0,0); orw.setSpacing(4)
        orw.addWidget(_lbl("OPENROUTER API KEY", 7, color=C.GREEN, align=Qt.AlignmentFlag.AlignLeft))
        self._or_key = QLineEdit()
        self._or_key.setEchoMode(QLineEdit.EchoMode.Password)
        self._or_key.setPlaceholderText("sk-or-v1-…")
        self._or_key.setFont(QFont("Segoe UI", 12))
        self._or_key.setFixedHeight(28)
        self._or_key.setStyleSheet(f"""
            QLineEdit {{ background: #000d12; color: {C.TEXT};
                border: 1px solid {C.BORDER}; border-radius: 3px; padding: 3px 6px; }}
            QLineEdit:focus {{ border: 1px solid {C.GREEN}; }}
        """)
        orw.addWidget(self._or_key)
        orw.addWidget(_lbl("✓ 300+ Models · Vision · Tools", 6, color=C.GREEN_D))

        # LM Studio fields
        self._lm_widget = QWidget()
        lmw = QVBoxLayout(self._lm_widget); lmw.setContentsMargins(0,0,0,0); lmw.setSpacing(4)
        lmw.addWidget(_lbl("LM STUDIO SERVER URL", 7, color=C.ACC, align=Qt.AlignmentFlag.AlignLeft))
        self._lm_url = QLineEdit()
        self._lm_url.setPlaceholderText("http://localhost:1234")
        self._lm_url.setText("http://localhost:1234")
        self._lm_url.setFont(QFont("Segoe UI", 12))
        self._lm_url.setFixedHeight(28)
        self._lm_url.setStyleSheet(f"""
            QLineEdit {{ background: #000d12; color: {C.TEXT};
                border: 1px solid {C.BORDER}; border-radius: 3px; padding: 3px 6px; }}
            QLineEdit:focus {{ border: 1px solid {C.ACC}; }}
        """)
        lmw.addWidget(self._lm_url)
        lmw.addWidget(_lbl("✓ Local Models · No API Key Needed · Vision-capable", 6, color=C.GREEN_D))

        self._config_stack.addWidget(self._gemini_widget)
        self._config_stack.addWidget(self._ollama_widget)
        self._config_stack.addWidget(self._or_widget)
        self._config_stack.addWidget(self._lm_widget)
        self._sel_prov("gemini")
        layout.addLayout(self._config_stack)
        layout.addSpacing(4)

        sep2 = QFrame(); sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet(f"color: {C.BORDER};"); layout.addWidget(sep2)
        layout.addSpacing(4)

        layout.addWidget(_lbl("OPERATING SYSTEM", 8, color=C.TEXT_DIM,
                               align=Qt.AlignmentFlag.AlignLeft))
        det_name = {"windows": "Windows", "mac": "macOS", "linux": "Linux"}[detected]
        layout.addWidget(_lbl(f"Auto-detected: {det_name}", 8, color=C.ACC2,
                               align=Qt.AlignmentFlag.AlignLeft))

        os_row = QHBoxLayout(); os_row.setSpacing(6)
        self._os_btns: dict[str, QPushButton] = {}
        for key, label in [("windows","⊞  Windows"),("mac","  macOS"),("linux","🐧  Linux")]:
            btn = QPushButton(label)
            btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            btn.setFixedHeight(30)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, k=key: self._sel_os_fn(k))
            os_row.addWidget(btn)
            self._os_btns[key] = btn
        layout.addLayout(os_row)
        self._sel_os_fn(detected)
        layout.addSpacing(8)

        init_btn = QPushButton("▸  INITIALISE SYSTEMS")
        init_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        init_btn.setFixedHeight(34)
        init_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        init_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {C.PRI};
                border: 1px solid {C.PRI_DIM}; border-radius: 3px;
            }}
            QPushButton:hover {{
                background: {C.PRI_GHO}; border: 1px solid {C.PRI};
            }}
        """)
        init_btn.clicked.connect(self._submit)
        layout.addWidget(init_btn)

    def _sel_prov(self, key: str):
        self._sel_provider = key
        pal = {"gemini":(C.PRI,"#001a22"),"ollama":(C.ACC2,"#1a1400"),"openrouter":(C.GREEN,"#001a0d"),"lmstudio":(C.ACC,"#1a0e00")}
        for k, btn in self._prov_btns.items():
            if k == key:
                fg, bg = pal.get(k, (C.PRI, "#001a22"))
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
        # Show/hide config fields
        self._gemini_widget.setVisible(key == "gemini")
        self._ollama_widget.setVisible(key == "ollama")
        self._or_widget.setVisible(key == "openrouter")
        self._lm_widget.setVisible(key == "lmstudio")

    def _sel_os_fn(self, key: str):
        self._sel_os = key
        pal = {"windows":(C.PRI,"#001a22"),"mac":(C.ACC2,"#1a1400"),"linux":(C.GREEN,"#001a0d")}
        for k, btn in self._os_btns.items():
            if k == key:
                fg, bg = pal[k]
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

    def _submit(self):
        provider = self._sel_provider
        os_name = self._sel_os
        gemini_key = self._gemini_key.text().strip()
        ollama_url = self._ollama_url.text().strip()
        or_key = self._or_key.text().strip()
        lmstudio_url = self._lm_url.text().strip() or "http://localhost:1234"

        # Validate required field for selected provider
        if provider == "gemini" and not gemini_key:
            self._gemini_key.setStyleSheet(
                self._gemini_key.styleSheet() +
                f" QLineEdit {{ border: 1px solid {C.RED}; }}"
            )
            return
        if provider == "openrouter" and not or_key:
            self._or_key.setStyleSheet(
                self._or_key.styleSheet() +
                f" QLineEdit {{ border: 1px solid {C.RED}; }}"
            )
            return
        # Ollama / LM Studio are always valid with default URLs

        # Pre-save LM Studio URL so main window picks it up
        if provider == "lmstudio":
            save_config({"lmstudio_url": lmstudio_url})

        self.done.emit(provider, os_name, gemini_key, ollama_url, or_key, "")


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
        self._highlight_provider(provider)
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

        for txt, col in [
            ("AI CORE\nACTIVE",     C.GREEN),
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
        
    def _set_audio_engine(self, mode: str):
        if mode == "gemini":
            save_config({"stt_engine": "gemini", "tts_engine": "gemini"})
            self._log.append_log("SYS: Motores de audio configurados a Gemini Cloud.")
        else:
            save_config({"stt_engine": "whisper", "tts_engine": "piper"})
            self._log.append_log("SYS: Motores de audio configurados a Whisper / Piper local.")
        
        self._update_audio_toggles()
        
        if hasattr(self, '_on_provider_changed') and self._on_provider_changed:
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
            ollama_models = [
                ("llama3.2", "Llama 3.2 (8B)"),
                ("llama3.1", "Llama 3.1 (70B)"),
                ("mistral",  "Mistral (7B)"),
                ("mixtral",  "Mixtral (8x7B)"),
                ("qwen2.5",  "Qwen 2.5"),
                ("phi4",     "Phi-4"),
                ("deepseek-r1", "DeepSeek R1"),
                ("codellama", "CodeLlama"),
                ("gemma2",   "Gemma 2"),
            ]
            for mid, desc in ollama_models:
                self._right_model_combo.addItem(desc, mid)
            for i in range(self._right_model_combo.count()):
                if self._right_model_combo.itemData(i) == saved_model:
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
            # Trigger engine restart so the new model takes effect
            if hasattr(self, '_on_provider_changed') and self._on_provider_changed:
                self._on_provider_changed(provider)

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
        if self._muted:
            self._apply_state("MUTED")
            self._log.append_log("SYS: Microphone muted.")
        else:
            self._apply_state("LISTENING")
            self._log.append_log("SYS: Microphone active.")

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
        self.hud.state    = state
        self.hud.speaking = (state == "SPEAKING")

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
