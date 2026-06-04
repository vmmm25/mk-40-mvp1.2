"""Abstract base class for all JARVIS tools."""
from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """Abstract tool — each tool in its own file or inline."""

    name: str = ""
    description: str = ""
    parameters: dict = {}

    @abstractmethod
    def execute(self, args: dict, ui: Any) -> str:
        """Execute the tool and return result string."""
        ...
