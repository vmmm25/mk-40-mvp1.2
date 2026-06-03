"""MARK XL — Structured logging configuration.

Provides rotating file handlers, console output, and JSON-formatted
logs suitable for both development and production use.

Usage::

    from core.logging_config import setup_logging
    setup_logging()
"""
from __future__ import annotations

import logging
import logging.handlers
import os
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Custom formatters
# ---------------------------------------------------------------------------

class ColoredConsoleFormatter(logging.Formatter):
    """Add ANSI colour to console log records based on severity."""

    _LEVEL_COLORS = {
        logging.DEBUG: "\x1b[38;5;245m",      # grey
        logging.INFO: "\x1b[38;5;39m",        # blue
        logging.WARNING: "\x1b[38;5;214m",    # orange
        logging.ERROR: "\x1b[38;5;196m",      # red
        logging.CRITICAL: "\x1b[38;5;196m\x1b[1m",  # bold red
    }
    _RESET = "\x1b[0m"

    COLUMN_WIDTHS = {1: 17, 2: 8}  # name, levelname

    def format(self, record: logging.LogRecord) -> str:
        color = self._LEVEL_COLORS.get(record.levelno, self._RESET)
        record.msg = f"{color}{record.msg}{self._RESET}"
        return super().format(record)


_CONSOLE_FMT = "%(asctime)s [%(name)-18s] %(levelname)-8s %(message)s"
_FILE_FMT = (
    "%(asctime)s.%(msecs)03d [%(name)s] %(levelname)s: %(message)s  "
    "[%(filename)s:%(lineno)d]"
)
_DATE_FMT = "%H:%M:%S"


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

def setup_logging(
    log_dir: str | Path = "logs",
    log_file: str = "jarvis.log",
    level: int = logging.INFO,
    max_bytes: int = 10 * 1024 * 1024,   # 10 MB
    backup_count: int = 5,
    json_format: bool = False,
) -> None:
    """Configure application-wide logging.

    Parameters
    ----------
    log_dir : str or Path
        Directory for log files (created if missing).
    log_file : str
        Base name of the log file.
    level : int
        Minimum logging level (default ``logging.INFO``).
    max_bytes : int
        Maximum size per log file before rotation.
    backup_count : int
        Number of rotated backups to keep.
    json_format : bool
        When *True*, emit JSON lines to the file handler.
    """
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    file_path = log_path / log_file

    # ---- Handlers ----
    handlers: list[logging.Handler] = []

    # Console handler (coloured)
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(ColoredConsoleFormatter(_CONSOLE_FMT, datefmt=_DATE_FMT))
    handlers.append(console)

    # Rotating file handler (always UTF-8)
    file_handler = logging.handlers.RotatingFileHandler(
        file_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    if json_format:
        file_handler.setFormatter(_JsonFormatter())
    else:
        file_handler.setFormatter(
            logging.Formatter(_FILE_FMT, datefmt="%Y-%m-%dT%H:%M:%S")
        )
    handlers.append(file_handler)

    # Apply to root logger
    logging.basicConfig(level=level, handlers=handlers, force=True)

    # Suppress noisy third-party loggers by default
    for noisy in ("httpx", "httpcore", "urllib3", "chardet", "chromadb"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    logging.getLogger(__name__).info(
        "Logging initialised — file: %s  level: %s",
        file_path.resolve(),
        logging.getLevelName(level),
    )


# ---------------------------------------------------------------------------
# JSON formatter (for structured log analysis)
# ---------------------------------------------------------------------------

class _JsonFormatter(logging.Formatter):
    """Emit JSON lines for machine consumption."""

    def format(self, record: logging.LogRecord) -> str:
        import json
        import traceback

        obj: dict = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0]:
            obj["exception"] = "".join(
                traceback.format_exception(*record.exc_info)
            ).strip()
        return json.dumps(obj, ensure_ascii=False)
