"""Chat log widget with typewriter animation effect."""
from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QBrush, QFont
from PyQt6.QtWidgets import QTextEdit

from ui.theme import Theme as C, qcol


class LogWidget(QTextEdit):
    """Animated typewriter chat log widget."""
    _sig = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        from PyQt6.QtWidgets import QLabel
        from PyQt6.QtCore import QTimer
        
        self.setReadOnly(True)
        self.setFont(QFont("Segoe UI", 12))
        
        # Overlay label for the spinner
        self._spinner_lbl = QLabel(self)
        self._spinner_lbl.setStyleSheet(f"color: {C.ACC2}; background: transparent; font-weight: bold;")
        self._spinner_lbl.hide()
        self._spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self._spinner_idx = 0
        self._spinner_timer = QTimer(self)
        self._spinner_timer.timeout.connect(self._update_spinner)
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
        self._typing = False
        self._text = ""
        self._pos = 0
        self._tag = "sys"
        self._tmr = QTimer(self)
        self._tmr.timeout.connect(self._step)
        self._sig.connect(self._enqueue)

    def _update_spinner(self):
        self._spinner_idx = (self._spinner_idx + 1) % len(self._spinner_chars)
        self._spinner_lbl.setText(f"Procesando {self._spinner_chars[self._spinner_idx]}")
        self._spinner_lbl.adjustSize()
        self._spinner_lbl.move(
            self.viewport().width() - self._spinner_lbl.width() - 10,
            self.viewport().height() - self._spinner_lbl.height() - 10
        )

    def set_thinking(self, thinking: bool):
        if thinking:
            self._spinner_lbl.show()
            self._spinner_timer.start(100)
            self._update_spinner()
        else:
            self._spinner_lbl.hide()
            self._spinner_timer.stop()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if self._spinner_lbl.isVisible():
            self._spinner_lbl.move(
                self.viewport().width() - self._spinner_lbl.width() - 10,
                self.viewport().height() - self._spinner_lbl.height() - 10
            )

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
        self._text = self._queue.pop(0)
        self._pos = 0
        tl = self._text.lower()
        if   tl.startswith("you:"):    self._tag = "you"
        elif tl.startswith("jarvis:"): self._tag = "ai"
        elif tl.startswith("file:"):   self._tag = "file"
        elif "err" in tl:              self._tag = "err"
        else:                          self._tag = "sys"
        self._tmr.start(6)

    def _step(self):
        if self._pos < len(self._text):
            ch = self._text[self._pos]
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
