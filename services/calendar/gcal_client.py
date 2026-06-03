"""MARK XL — Google Calendar client."""

from __future__ import annotations

import datetime
import json
import logging
import os
from pathlib import Path
from typing import Any, List, Optional

logger = logging.getLogger(__name__)


class GoogleCalendarClient:
    """Google Calendar integration via the Google Calendar API.

    Uses OAuth2 with credentials stored in ``config/credentials.json``
    (downloaded from Google Cloud Console).  The token is cached in
    ``config/calendar_token.json``.
    """

    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    CREDENTIALS_PATH = Path("config/credentials.json")
    TOKEN_PATH = Path("config/calendar_token.json")

    def __init__(self) -> None:
        self.service = None
        self._authenticate()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def list_events(self, max_results: int = 10, days_ahead: int = 7) -> list[dict[str, Any]]:
        """Return upcoming events from the primary calendar."""
        if not self.service:
            logger.error("Calendar service not initialised")
            return []

        try:
            now = datetime.datetime.utcnow().isoformat() + "Z"
            later = (
                datetime.datetime.utcnow() + datetime.timedelta(days=days_ahead)
            ).isoformat() + "Z"

            events_result = (
                self.service.events()
                .list(
                    calendarId="primary",
                    timeMin=now,
                    timeMax=later,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])
            formatted = []
            for ev in events:
                start = ev.get("start", {}).get("dateTime", ev.get("start", {}).get("date", "?"))
                formatted.append({
                    "id": ev.get("id", ""),
                    "summary": ev.get("summary", "No title"),
                    "description": ev.get("description", ""),
                    "start": start,
                    "end": ev.get("end", {}).get("dateTime", ev.get("end", {}).get("date", "?")),
                    "location": ev.get("location", ""),
                    "htmlLink": ev.get("htmlLink", ""),
                })
            logger.info("Calendar: found %d upcoming events", len(formatted))
            return formatted
        except Exception as exc:
            logger.error("Calendar list_events failed: %s", exc)
            return []

    def create_event(
        self,
        summary: str,
        date: str,
        time: str = "12:00",
        duration_minutes: int = 60,
        description: str = "",
        attendees: Optional[list[str]] = None,
    ) -> dict[str, Any] | None:
        """Create a new calendar event."""
        if not self.service:
            logger.error("Calendar service not initialised")
            return None

        try:
            start_dt = datetime.datetime.fromisoformat(f"{date}T{time}:00")
            end_dt = start_dt + datetime.timedelta(minutes=duration_minutes)

            event: dict[str, Any] = {
                "summary": summary,
                "description": description,
                "start": {
                    "dateTime": start_dt.isoformat(),
                    "timeZone": "UTC",
                },
                "end": {
                    "dateTime": end_dt.isoformat(),
                    "timeZone": "UTC",
                },
            }

            if attendees:
                event["attendees"] = [{"email": a} for a in attendees]

            created = (
                self.service.events()
                .insert(calendarId="primary", body=event)
                .execute()
            )
            logger.info("Calendar event created: %s (id=%s)", summary, created.get("id"))
            return {
                "id": created.get("id"),
                "summary": created.get("summary"),
                "htmlLink": created.get("htmlLink"),
            }
        except Exception as exc:
            logger.error("Calendar create_event failed: %s", exc)
            return None

    def is_authenticated(self) -> bool:
        return self.service is not None

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def _authenticate(self) -> None:
        """Authenticate via OAuth2 using stored or fresh credentials."""
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
        except ImportError:
            logger.error("Google API client libraries not installed.")
            return

        creds = None
        if self.TOKEN_PATH.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(self.TOKEN_PATH), self.SCOPES)
            except Exception as exc:
                logger.warning("Failed to load calendar token: %s", exc)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as exc:
                    logger.warning("Token refresh failed: %s", exc)
                    creds = None

            if not creds:
                if not self.CREDENTIALS_PATH.exists():
                    logger.warning(
                        "Google Calendar credentials not found at %s. "
                        "Calendar disabled.", self.CREDENTIALS_PATH
                    )
                    return
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.CREDENTIALS_PATH), self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save token
            self.TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
            self.TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")

        self.service = build("calendar", "v3", credentials=creds)
        logger.info("Google Calendar authenticated")
