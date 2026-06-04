"""JARVIS Tool System — Registry + backwards-compatible exports.

This module initializes the ToolRegistry and registers all existing
handler functions from handlers.py for full backward compatibility.
New tools should subclass BaseTool and be auto-discovered.

Usage:
    from tools import TOOL_DECLARATIONS, TOOL_IMPLEMENTATIONS
    from tools import registry
"""
import logging

from tools.registry import ToolRegistry
from tools.handlers import TOOL_IMPLEMENTATIONS as _LEGACY_IMPLS

logger = logging.getLogger(__name__)

# ── Create global registry ──
registry = ToolRegistry()

# ── Register all legacy handlers ──
for name, handler in _LEGACY_IMPLS.items():
    registry.register_handler(name, handler)

# ── Auto-discover BaseTool subclasses (future) ──
# When tools are migrated to BaseTool classes, they will be
# discovered automatically here via pkgutil.walk_packages.

# ── Backwards-compatible exports ──
from tools.declarations import TOOL_DECLARATIONS  # noqa: F401, E402

TOOL_IMPLEMENTATIONS = registry.get_implementations()

__all__ = ["TOOL_DECLARATIONS", "TOOL_IMPLEMENTATIONS", "registry"]
