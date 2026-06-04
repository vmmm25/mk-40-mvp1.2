"""JARVIS Tool System — Registry + backwards-compatible exports.

This module initializes the ToolRegistry and registers all tool classes
from tools.chat_tools for full backward compatibility.
"""
import logging

from tools.registry import ToolRegistry
from tools.chat_tools import ALL_TOOLS

logger = logging.getLogger(__name__)

# ── Create global registry ──
registry = ToolRegistry()

# ── Register all tools ──
for tool in ALL_TOOLS:
    registry.register(tool.__class__)

# ── Backwards-compatible exports ──
from tools.declarations import TOOL_DECLARATIONS  # noqa: F401, E402

TOOL_IMPLEMENTATIONS = registry.get_implementations()

__all__ = ["TOOL_DECLARATIONS", "TOOL_IMPLEMENTATIONS", "registry"]
