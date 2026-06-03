"""MARK XL — Abstract image generator interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Optional


class ImageGenerator(ABC):
    """Abstract interface for image generation backends."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        style: Optional[str] = None,
        size: Optional[str] = None,
        count: int = 1,
        **kwargs: Any,
    ) -> List[bytes]:
        """Generate image(s) from a text prompt.

        Returns a list of PNG image bytes.
        """
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is ready to generate."""
        ...
