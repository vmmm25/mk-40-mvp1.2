"""MARK XL — Abstract calendar service interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Optional


class CalendarService(ABC):
    """Abstract interface for calendar providers."""

    @abstractmethod
    def list_events(self, max_results: int = 10, days_ahead: int = 7) -> list[dict[str, Any]]:
        """List upcoming calendar events."""
        ...

    @abstractmethod
    def create_event(
        self,
        summary: str,
        date: str,
        time: str = "12:00",
        duration_minutes: int = 60,
        description: str = "",
        attendees: Optional[list[str]] = None,
    ) -> dict[str, Any] | None:
        """Create a new calendar event. Returns event data or None."""
        ...

    @abstractmethod
    def is_authenticated(self) -> bool:
        """Check if the service is authenticated."""
        ...
