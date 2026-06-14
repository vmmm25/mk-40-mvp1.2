"""
CollapsibleSection — Reusable accordion widget with smooth animation.

A clickable header that expands/collapses its content area with a
QPropertyAnimation on maximumHeight.
"""
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame,
    QSizePolicy,
)
from ui.theme import Theme as C


class CollapsibleSection(QWidget):
    """Accordion section: clickable header + animated content toggle."""

    toggled = pyqtSignal(bool)  # True = expanded

    def __init__(self, title: str, icon: str = "", expanded: bool = False, parent=None):
        super().__init__(parent)
        self._expanded = expanded
        self._title = title
        self._icon = icon
        self._animation_duration = 200

        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)

        # ── Header button ──
        self._header = QPushButton()
        self._header.setFixedHeight(32)
        self._header.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self._header.setCursor(Qt.CursorShape.PointingHandCursor)
        self._header.clicked.connect(self.toggle)
        self._update_header()
        main_lay.addWidget(self._header)

        # ── Separator ──
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {C.BORDER}; border: none;")
        main_lay.addWidget(sep)

        # ── Content container ──
        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(8, 6, 8, 6)
        self._content_layout.setSpacing(6)
        self._content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        main_lay.addWidget(self._content)

        # ── Animation ──
        self._anim = QPropertyAnimation(self._content, b"maximumHeight")
        self._anim.setDuration(self._animation_duration)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # Initial state
        if not expanded:
            self._content.setMaximumHeight(0)
        else:
            self._content.setMaximumHeight(16777215)  # QWIDGETSIZE_MAX

    @property
    def content_layout(self) -> QVBoxLayout:
        """Access the layout inside the collapsible content area."""
        return self._content_layout

    def add_widget(self, widget: QWidget):
        """Add a widget to the content area."""
        self._content_layout.addWidget(widget)

    def add_layout(self, layout):
        """Add a layout to the content area."""
        self._content_layout.addLayout(layout)

    def toggle(self):
        """Toggle expanded/collapsed state."""
        self._expanded = not self._expanded
        self._update_header()

        if self._expanded:
            # Expand: measure real content height
            self._content.setMaximumHeight(0)
            self._content.adjustSize()
            target = self._content.sizeHint().height()
            if target < 40:
                target = 300  # fallback
            self._anim.setStartValue(0)
            self._anim.setEndValue(target)
            self._anim.finished.connect(self._on_expand_done)
        else:
            # Collapse
            self._anim.setStartValue(self._content.height())
            self._anim.setEndValue(0)
            try:
                self._anim.finished.disconnect(self._on_expand_done)
            except TypeError:
                pass

        self._anim.start()
        self.toggled.emit(self._expanded)

    def _on_expand_done(self):
        """Remove height constraint after expanding so content can grow."""
        self._content.setMaximumHeight(16777215)
        try:
            self._anim.finished.disconnect(self._on_expand_done)
        except TypeError:
            pass

    def set_expanded(self, expanded: bool):
        """Programmatically set state without animation."""
        if self._expanded != expanded:
            self._expanded = expanded
            self._update_header()
            if expanded:
                self._content.setMaximumHeight(16777215)
            else:
                self._content.setMaximumHeight(0)
            self.toggled.emit(self._expanded)

    def _update_header(self):
        arrow = "▼" if self._expanded else "▶"
        prefix = f"{self._icon}  " if self._icon else ""
        self._header.setText(f"  {arrow}  {prefix}{self._title}")
        if self._expanded:
            self._header.setStyleSheet(f"""
                QPushButton {{
                    background: {C.PANEL2}; color: {C.PRI};
                    border: none; border-radius: 0px;
                    text-align: left; padding-left: 8px;
                }}
                QPushButton:hover {{ background: {C.PRI_GHO}; }}
            """)
        else:
            self._header.setStyleSheet(f"""
                QPushButton {{
                    background: {C.PANEL}; color: {C.TEXT_MED};
                    border: none; border-radius: 0px;
                    text-align: left; padding-left: 8px;
                }}
                QPushButton:hover {{ color: {C.PRI}; background: {C.PANEL2}; }}
            """)
