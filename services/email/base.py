"""MARK XL — Abstract email service interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Optional


class EmailService(ABC):
    """Abstract interface for email providers."""

    @abstractmethod
    def send_email(self, to: str, subject: str, body: str, cc: Optional[str] = None) -> bool:
        """Send an email. Returns True on success."""
        ...

    @abstractmethod
    def read_emails(self, max_results: int = 10, query: str = "") -> List[dict[str, Any]]:
        """Read emails matching optional query."""
        ...

    @abstractmethod
    def is_authenticated(self) -> bool:
        """Check if the service is authenticated and ready."""
        ...
