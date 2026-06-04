"""Central registry for all JARVIS tools.

Provides backwards-compatible access via TOOL_DECLARATIONS and TOOL_IMPLEMENTATIONS
while internally using the new BaseTool pattern for future tools.
"""
import logging
from typing import Any, Callable

from tools.base import BaseTool

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Central registry for all tools."""

    def __init__(self):
        self._declarations: list[dict] = []
        self._implementations: dict[str, BaseTool | Callable] = {}

    def register(self, tool_class: type[BaseTool]):
        """Register a BaseTool subclass."""
        instance = tool_class()
        self._declarations.append({
            "name": instance.name,
            "description": instance.description,
            "parameters": instance.parameters,
        })
        self._implementations[instance.name] = instance
        logger.debug("Registered tool: %s", instance.name)

    def register_handler(self, name: str, handler: Callable):
        """Register a legacy handler function (backwards compatibility)."""
        self._implementations[name] = handler

    def get_declarations(self) -> list[dict]:
        return list(self._declarations)

    def get_implementations(self) -> dict[str, Callable]:
        """Return dict compatible with existing TOOL_IMPLEMENTATIONS format."""
        result = {}
        for name, impl in self._implementations.items():
            if isinstance(impl, BaseTool):
                result[name] = impl.execute
            else:
                result[name] = impl
        return result

    def execute(self, name: str, args: dict, ui: Any) -> str:
        impl = self._implementations.get(name)
        if not impl:
            return f"Unknown tool: {name}"
        if isinstance(impl, BaseTool):
            return impl.execute(args, ui)
        return impl(args, ui) or "Done."
