"""Setup / first-boot overlay dialog."""
from __future__ import annotations

import platform

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget,
)

from memory.config_manager import save_config
from ui.theme import Theme as C

_OS = platform.system()


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
