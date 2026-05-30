"""WaveCanvas — 3-D stacked-line spectrogram visualiser.

Renders a perspective waterfall / terrain effect (like the reference image)
where each horizontal slice is a snapshot of the waveform in time.
The canvas reacts visually to four states:
    SPEAKING   — high amplitude, warm cyan glow, fast scroll
    LISTENING  — medium amplitude, soft green, medium scroll
    THINKING   — low sinusoidal pulse, muted teal, slow scroll
    MUTED / idle — near-flat lines, dim color
"""

from __future__ import annotations

import math
import random
import collections

from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QPainterPath,
    QLinearGradient, QBrush,
)
from PyQt6.QtWidgets import QWidget, QSizePolicy

from ui.theme import Theme, qcol


# ── tunables ────────────────────────────────────────────────────────────────
_NUM_SLICES   = 38          # how many horizontal lines (depth)
_POINTS       = 140         # horizontal resolution per line
_SKEW_X       = 0.55        # perspective lean (0 = flat, 1 = 45°)
_SKEW_Y       = 0.28        # vertical squash (perspective)
_SCROLL_RATE  = 1           # ticks between advancing the waterfall
_FPS_MS       = 16          # ~60 fps


class WaveCanvas(QWidget):
    """Perspective waterfall / terrain 3-D waveform display."""

    def __init__(self, face_path: str = "", parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        self.setMinimumSize(300, 260)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Public state flags (set by JarvisUI / main_window)
        self.muted    = False
        self.speaking = False
        self.state    = "INITIALISING"

        # Internal animation state
        self._tick    = 0
        self._phase   = 0.0          # continuous phase for wave functions
        self._scroll_acc = 0         # accumulator for waterfall scroll

        # Waterfall buffer: deque of amplitude arrays, newest at front
        empty = [0.0] * _POINTS
        self._slices: collections.deque[list[float]] = collections.deque(
            [empty[:] for _ in range(_NUM_SLICES)],
            maxlen=_NUM_SLICES,
        )

        # Smooth amplitude envelope
        self._amp      = 0.0         # current smoothed amplitude
        self._target   = 0.0         # target amplitude

        # Timer
        self._tmr = QTimer(self)
        self._tmr.timeout.connect(self._step)
        self._tmr.start(_FPS_MS)

    # ── Public API ────────────────────────────────────────────────────────

    def push_audio_chunk(self, chunk: bytes):
        """Feed raw PCM int16 bytes so the visualiser reacts to real audio.

        Call this from the audio callback whenever new audio data is available.
        It computes RMS amplitude and directly drives the waterfall with real data.
        """
        import struct
        n = len(chunk) // 2
        if n == 0:
            return
        samples = struct.unpack(f"{n}h", chunk[:n * 2])
        # RMS
        rms = math.sqrt(sum(s * s for s in samples) / n) / 32768.0
        self._target = min(1.0, rms * 4.0)

        # Build a waveform row from the samples (downsampled to _POINTS)
        step = max(1, n // _POINTS)
        row = []
        for i in range(_POINTS):
            idx = i * step
            row.append(samples[min(idx, n - 1)] / 32768.0)
        self._push_row(row)

    # ── Internal helpers ──────────────────────────────────────────────────

    def _push_row(self, row: list[float]):
        """Prepend a new waveform row into the waterfall buffer."""
        self._slices.appendleft(row[:_POINTS])

    def _generate_synthetic_row(self) -> list[float]:
        """Create a procedural waveform row based on current state."""
        amp = self._amp
        ph  = self._phase
        row = []
        for i in range(_POINTS):
            t = i / _POINTS
            if self.state == "SPEAKING":
                v  = math.sin(2 * math.pi * t * 6  + ph * 2.1) * 0.55
                v += math.sin(2 * math.pi * t * 13 + ph * 1.3) * 0.28
                v += math.sin(2 * math.pi * t * 27 + ph * 0.7) * 0.12
                v += (random.random() - 0.5) * 0.10
            elif self.state == "LISTENING":
                v  = math.sin(2 * math.pi * t * 4  + ph * 1.4) * 0.35
                v += math.sin(2 * math.pi * t * 9  + ph * 0.9) * 0.18
                v += (random.random() - 0.5) * 0.06
            elif self.state == "THINKING":
                v  = math.sin(2 * math.pi * t * 2  + ph * 0.5) * 0.20
                v += math.sin(2 * math.pi * t * 5  + ph * 0.3) * 0.10
            else:
                v  = math.sin(2 * math.pi * t * 1.5 + ph * 0.2) * 0.04
                v += (random.random() - 0.5) * 0.02
            row.append(v * amp)
        return row

    def _target_amplitude(self) -> float:
        if self.muted:
            return 0.04
        if self.speaking:
            return 0.80 + math.sin(self._tick * 0.08) * 0.15
        if self.state == "LISTENING":
            return 0.42 + math.sin(self._tick * 0.05) * 0.08
        if self.state == "THINKING":
            return 0.22 + math.sin(self._tick * 0.03) * 0.06
        return 0.07

    def _step(self):
        self._tick += 1

        # Speed of phase / scroll by state
        if self.speaking:
            phase_speed  = 0.22
            scroll_every = 1
        elif self.state == "LISTENING":
            phase_speed  = 0.13
            scroll_every = 2
        elif self.state == "THINKING":
            phase_speed  = 0.07
            scroll_every = 3
        else:
            phase_speed  = 0.03
            scroll_every = 5

        self._phase += phase_speed

        # Smooth amplitude
        self._target = self._target_amplitude()
        self._amp += (self._target - self._amp) * 0.12

        # Advance waterfall
        self._scroll_acc += 1
        if self._scroll_acc >= scroll_every:
            self._scroll_acc = 0
            self._push_row(self._generate_synthetic_row())

        self.update()

    # ── Colors ────────────────────────────────────────────────────────────

    def _slice_color(self, layer: int, total: int) -> QColor:
        """Return the pen color for a given layer (0=front … total-1=back)."""
        t = layer / max(1, total - 1)   # 0.0 (front) … 1.0 (back)

        if self.muted:
            # Grey / slate when muted
            v = int(80 - t * 60)
            return QColor(v, v, v + 15)

        if self.speaking:
            # Warm cyan → deep blue towards back
            r = int(lerp(0,   0,   t))
            g = int(lerp(210, 60,  t))
            b = int(lerp(220, 180, t))
            a = int(lerp(240, 30,  t))
        elif self.state == "LISTENING":
            # Soft green → navy
            r = int(lerp(40,  10,  t))
            g = int(lerp(210, 80,  t))
            b = int(lerp(140, 120, t))
            a = int(lerp(230, 25,  t))
        elif self.state == "THINKING":
            # Teal / cyan pulse
            r = int(lerp(20,  5,   t))
            g = int(lerp(180, 60,  t))
            b = int(lerp(200, 150, t))
            a = int(lerp(210, 20,  t))
        else:
            # Dim slate idle
            r = int(lerp(30,  10,  t))
            g = int(lerp(90,  30,  t))
            b = int(lerp(110, 70,  t))
            a = int(lerp(160, 15,  t))

        return QColor(r, g, b, a)

    def _fill_color(self, layer: int, total: int) -> QColor:
        """Return a very dim fill beneath each slice line for depth."""
        t = layer / max(1, total - 1)
        if self.muted:
            return QColor(10, 10, 20, 10)
        if self.speaking:
            return QColor(0, 40, 60, int(lerp(30, 0, t)))
        if self.state == "LISTENING":
            return QColor(0, 50, 40, int(lerp(20, 0, t)))
        return QColor(5, 20, 40, int(lerp(15, 0, t)))

    # ── Paint ─────────────────────────────────────────────────────────────

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        W, H = self.width(), self.height()

        # Background gradient — deep navy
        grad = QLinearGradient(0, 0, 0, H)
        grad.setColorAt(0.0, QColor("#08101F"))
        grad.setColorAt(1.0, QColor("#060D18"))
        p.fillRect(0, 0, W, H, QBrush(grad))

        slices = list(self._slices)   # front-to-back order
        n      = len(slices)
        if n == 0:
            return

        # Canvas margins
        margin_x = W * 0.06
        margin_top = H * 0.12
        margin_bot = H * 0.10

        draw_w = W - 2 * margin_x
        draw_h = H - margin_top - margin_bot

        # Perspective parameters
        # Each slice is shifted right (SKEW_X) and up (per layer depth)
        total_x_shift = draw_w * _SKEW_X
        total_y_shift = draw_h * 0.55          # total vertical compression for depth
        amp_scale     = draw_h * 0.16           # max wave peak height in pixels

        # Draw back-to-front (painter's algorithm)
        for layer in range(n - 1, -1, -1):
            row = slices[layer]
            t   = layer / max(1, n - 1)   # 0=front … 1=back

            # Baseline y for this layer (back layers are higher on screen)
            base_y = (margin_top + draw_h + margin_bot * 0.5) - t * total_y_shift

            # Horizontal offset (perspective lean to the right for back layers)
            off_x = margin_x + t * total_x_shift

            # Horizontal scale shrinks slightly for far layers
            h_scale = lerp(1.0, 0.55, t)

            path = QPainterPath()
            fill_pts: list[tuple[float, float]] = []

            for i, val in enumerate(row):
                px = off_x + (i / (_POINTS - 1)) * draw_w * h_scale
                py = base_y - val * amp_scale

                if i == 0:
                    path.moveTo(px, py)
                    fill_pts.append((px, py))
                else:
                    path.lineTo(px, py)
                    fill_pts.append((px, py))

            # Fill below line for depth illusion
            fill_path = QPainterPath(path)
            if fill_pts:
                last_px = fill_pts[-1][0]
                first_px = fill_pts[0][0]
                fill_path.lineTo(last_px, base_y + 2)
                fill_path.lineTo(first_px, base_y + 2)
                fill_path.closeSubpath()

            fc = self._fill_color(layer, n)
            p.fillPath(fill_path, QBrush(fc))

            # Draw waveform line
            col = self._slice_color(layer, n)
            # Thicker pen for front layers
            pen_w = lerp(1.8, 0.5, t)
            p.setPen(QPen(col, pen_w, Qt.PenStyle.SolidLine,
                          Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPath(path)

        # ── State label overlay ──────────────────────────────────────────
        self._draw_state_label(p, W, H)

    def _draw_state_label(self, p: QPainter, W: int, H: int):
        """Draw a small status text at bottom-left."""
        from PyQt6.QtGui import QFont
        if self.muted:
            txt, col = "MUTED", "#E76F51"
        elif self.speaking:
            txt, col = "SPEAKING", "#5BC0BE"
        elif self.state == "LISTENING":
            txt, col = "LISTENING", "#5BC0BE"
        elif self.state == "THINKING":
            txt, col = "THINKING", "#8B9BB4"
        elif self.state == "INITIALISING":
            txt, col = "INITIALISING", "#3A506B"
        else:
            txt, col = self.state, "#3A506B"

        p.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        p.setPen(QColor(col))
        p.drawText(int(W * 0.06), H - 8, txt)


# ── Utility ──────────────────────────────────────────────────────────────────

def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation clamped to [0, 1]."""
    t = max(0.0, min(1.0, t))
    return a + (b - a) * t
