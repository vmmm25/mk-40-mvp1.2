"""MARK XL — Spotify client for music playback control."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class SpotifyClient:
    """Spotify playback control via Spotipy.

    Requires Spotify API credentials configured in the environment
    or in ``config/spotify_credentials.json``.

    Credentials file format::

        {
            "client_id": "...",
            "client_secret": "...",
            "redirect_uri": "http://localhost:8888/callback"
        }
    """

    CREDENTIALS_PATH = Path("config/spotify_credentials.json")
    TOKEN_PATH = Path("config/spotify_token.json")
    SCOPE = (
        "user-read-playback-state "
        "user-modify-playback-state "
        "user-read-currently-playing "
        "user-library-read "
        "playlist-read-private"
    )

    def __init__(self) -> None:
        self._sp = None
        self._authenticate()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def play(self, query: Optional[str] = None) -> str:
        """Start or resume playback. If *query* is given, search and play."""
        if not self._sp:
            return "Spotify not authenticated."

        try:
            if query:
                results = self._sp.search(q=query, type="track", limit=1)
                tracks = results.get("tracks", {}).get("items", [])
                if tracks:
                    uri = tracks[0]["uri"]
                    self._sp.start_playback(uris=[uri])
                    track_name = tracks[0]["name"]
                    artists = ", ".join(a["name"] for a in tracks[0]["artists"])
                    return f"Now playing: {track_name} by {artists}"
                return f"No results found for '{query}'."
            else:
                devices = self._sp.devices()
                if devices.get("devices"):
                    self._sp.start_playback()
                    return "Playback resumed."
                return "No active Spotify device found."
        except Exception as exc:
            logger.error("Spotify play failed: %s", exc)
            return f"Playback error: {exc}"

    def pause(self) -> str:
        """Pause current playback."""
        if not self._sp:
            return "Spotify not authenticated."
        try:
            self._sp.pause_playback()
            return "Playback paused."
        except Exception as exc:
            return f"Pause error: {exc}"

    def next_track(self) -> str:
        """Skip to next track."""
        if not self._sp:
            return "Spotify not authenticated."
        try:
            self._sp.next_track()
            return "Skipped to next track."
        except Exception as exc:
            return f"Next track error: {exc}"

    def previous_track(self) -> str:
        """Go to previous track."""
        if not self._sp:
            return "Spotify not authenticated."
        try:
            self._sp.previous_track()
            return "Returned to previous track."
        except Exception as exc:
            return f"Previous track error: {exc}"

    def set_volume(self, volume: int) -> str:
        """Set volume 0–100."""
        if not self._sp:
            return "Spotify not authenticated."
        try:
            vol = max(0, min(100, volume))
            self._sp.volume(vol)
            return f"Volume set to {vol}%."
        except Exception as exc:
            return f"Volume error: {exc}"

    def current_playback(self) -> dict[str, Any]:
        """Return info about currently playing track."""
        if not self._sp:
            return {"error": "Spotify not authenticated."}
        try:
            playback = self._sp.current_playback()
            if playback and playback.get("item"):
                item = playback["item"]
                return {
                    "track": item.get("name", "Unknown"),
                    "artists": ", ".join(a["name"] for a in item.get("artists", [])),
                    "album": item.get("album", {}).get("name", ""),
                    "is_playing": playback.get("is_playing", False),
                    "progress_ms": playback.get("progress_ms", 0),
                    "duration_ms": item.get("duration_ms", 0),
                }
            return {"message": "Nothing currently playing."}
        except Exception as exc:
            return {"error": str(exc)}

    def search(self, query: str, type: str = "track", limit: int = 10) -> list[dict[str, Any]]:
        """Search for tracks, artists, or playlists."""
        if not self._sp:
            return []
        try:
            results = self._sp.search(q=query, type=type, limit=limit)
            items = results.get(f"{type}s", {}).get("items", [])
            formatted = []
            for item in items:
                entry = {
                    "id": item.get("id", ""),
                    "name": item.get("name", "Unknown"),
                    "uri": item.get("uri", ""),
                }
                if type == "track":
                    entry["artists"] = ", ".join(a["name"] for a in item.get("artists", []))
                    entry["album"] = item.get("album", {}).get("name", "")
                elif type == "artist":
                    entry["genres"] = item.get("genres", [])
                formatted.append(entry)
            return formatted
        except Exception as exc:
            logger.error("Spotify search error: %s", exc)
            return []

    def is_authenticated(self) -> bool:
        return self._sp is not None

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def _authenticate(self) -> None:
        """Authenticate with Spotify via OAuth."""
        try:
            import spotipy
            from spotipy.oauth2 import SpotifyOAuth
        except ImportError:
            logger.error("spotipy library not installed")
            return

        if not self.CREDENTIALS_PATH.exists():
            logger.warning(
                "Spotify credentials not found at %s. "
                "Create with client_id, client_secret, redirect_uri.",
                self.CREDENTIALS_PATH,
            )
            return

        try:
            creds = json.loads(self.CREDENTIALS_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Failed to load Spotify credentials: %s", exc)
            return

        auth_manager = SpotifyOAuth(
            client_id=creds["client_id"],
            client_secret=creds["client_secret"],
            redirect_uri=creds.get("redirect_uri", "http://localhost:8888/callback"),
            scope=self.SCOPE,
            cache_path=str(self.TOKEN_PATH),
            open_browser=False,
        )

        token = auth_manager.get_cached_token() or auth_manager.get_access_token()
        if token:
            self._sp = spotipy.Spotify(auth_manager=auth_manager)
            logger.info("Spotify authenticated")
        else:
            logger.error("Spotify authentication failed")
