"""MARK XL — Outlook / Microsoft Graph email client."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, List, Optional

logger = logging.getLogger(__name__)


class OutlookClient:
    """Simple Outlook email client via Microsoft Graph REST API.

    Uses device-code OAuth flow.  Credentials are stored in
    ``config/outlook_token.json``.

    Requires the ``requests`` library (already in requirements).
    """

    TOKEN_PATH = Path("config/outlook_token.json")
    CLIENT_ID = "your-client-id-here"  # Replace with your Azure App registration ID
    AUTHORITY = "https://login.microsoftonline.com/common"
    SCOPE = ["https://graph.microsoft.com/Mail.ReadWrite", "https://graph.microsoft.com/Mail.Send"]

    def __init__(self) -> None:
        self.access_token: str | None = None
        self._authenticate()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def send_email(self, to: str, subject: str, body: str, cc: str | None = None) -> bool:
        """Send an email via Microsoft Graph."""
        token = self._get_token()
        if not token:
            logger.error("Outlook: no access token")
            return False

        import requests

        message: dict[str, Any] = {
            "message": {
                "subject": subject,
                "body": {"contentType": "Text", "content": body},
                "toRecipients": [{"emailAddress": {"address": to}}],
            }
        }
        if cc:
            message["message"]["ccRecipients"] = [
                {"emailAddress": {"address": addr.strip()}}
                for addr in cc.split(",")
            ]

        try:
            resp = requests.post(
                "https://graph.microsoft.com/v1.0/me/sendMail",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json=message,
                timeout=30,
            )
            if resp.status_code in (202, 200):
                logger.info("Outlook email sent to %s", to)
                return True
            logger.error("Outlook send failed: %s — %s", resp.status_code, resp.text)
            return False
        except requests.RequestException as exc:
            logger.error("Outlook send error: %s", exc)
            return False

    def read_emails(self, max_results: int = 10, query: str = "") -> list[dict[str, Any]]:
        """Read messages from the inbox."""
        token = self._get_token()
        if not token:
            return []

        import requests

        url = "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages"
        params: dict[str, Any] = {
            "$top": max_results,
            "$orderby": "receivedDateTime DESC",
            "$select": "id,subject,from,receivedDateTime,bodyPreview",
        }
        if query:
            params["$search"] = f'"{query}"'

        try:
            resp = requests.get(
                url,
                headers={"Authorization": f"Bearer {token}"},
                params=params,
                timeout=30,
            )
            if resp.status_code == 200:
                data = resp.json()
                emails = []
                for msg in data.get("value", []):
                    sender = msg.get("from", {}).get("emailAddress", {}).get("address", "Unknown")
                    emails.append({
                        "id": msg.get("id", ""),
                        "sender": sender,
                        "subject": msg.get("subject", "No Subject"),
                        "snippet": msg.get("bodyPreview", ""),
                        "received": msg.get("receivedDateTime", ""),
                    })
                return emails
            logger.error("Outlook read failed: %s — %s", resp.status_code, resp.text)
            return []
        except requests.RequestException as exc:
            logger.error("Outlook read error: %s", exc)
            return []

    def is_authenticated(self) -> bool:
        return self.access_token is not None or self.TOKEN_PATH.exists()

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def _authenticate(self) -> None:
        """Load token from disk or prompt device-code flow."""
        if self.TOKEN_PATH.exists():
            try:
                data = json.loads(self.TOKEN_PATH.read_text(encoding="utf-8"))
                self.access_token = data.get("access_token")
                logger.info("Outlook token loaded from disk")
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("Failed to load Outlook token: %s", exc)

    def _get_token(self) -> str | None:
        """Return a valid access token (placeholder — real impl needs MSAL)."""
        return self.access_token
