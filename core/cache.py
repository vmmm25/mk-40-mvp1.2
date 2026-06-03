"""MARK XL — Response cache with optional disk persistence.

Thread-safe in-memory cache with TTL eviction, LRU-style max-entry eviction,
and optional JSON file persistence via a configurable cache directory.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from threading import Lock
from typing import Optional

log = logging.getLogger(__name__)

CACHE_VERSION = 1


class ResponseCache:
    """Thread-safe response cache with optional disk persistence.

    Parameters
    ----------
    ttl_seconds : int
        Time-to-live for each entry in seconds (default 300 / 5 min).
    max_entries : int
        Maximum in-memory entries before oldest is evicted (default 100).
    cache_dir : str or Path, optional
        If provided, the cache is persisted to *cache_dir*/response_cache.json
        and reloaded on instantiation.
    """

    def __init__(
        self,
        ttl_seconds: int = 300,
        max_entries: int = 100,
        cache_dir: Optional[str | Path] = None,
    ) -> None:
        self.cache: dict[str, dict] = {}
        self.ttl = ttl_seconds
        self.max_entries = max_entries
        self.lock = Lock()
        self._cache_file: Path | None = None

        if cache_dir is not None:
            path = Path(cache_dir)
            path.mkdir(parents=True, exist_ok=True)
            self._cache_file = path / "response_cache.json"
            self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, key: str) -> Optional[str]:
        """Return cached *value* for *key*, or *None* if missing/expired."""
        with self.lock:
            entry = self.cache.get(key)
            if entry is None:
                return None
            if time.time() - entry["time"] >= self.ttl:
                del self.cache[key]
                return None
            return entry["value"]

    def set(self, key: str, value: str) -> None:
        """Store *value* for *key*, evicting oldest entry if at capacity."""
        with self.lock:
            if len(self.cache) >= self.max_entries and key not in self.cache:
                oldest = min(
                    self.cache.keys(), key=lambda k: self.cache[k]["time"]
                )
                del self.cache[oldest]
            self.cache[key] = {"value": value, "time": time.time()}
            if self._cache_file is not None:
                self._save()

    def clear(self) -> None:
        """Remove all entries and delete the cache file if persisted."""
        with self.lock:
            self.cache.clear()
            if self._cache_file is not None and self._cache_file.exists():
                self._cache_file.unlink(missing_ok=True)

    def stats(self) -> dict:
        """Return snapshot stats about the current cache state."""
        with self.lock:
            now = time.time()
            expired = sum(
                1 for e in self.cache.values()
                if now - e["time"] >= self.ttl
            )
            return {
                "entries": len(self.cache),
                "max_entries": self.max_entries,
                "ttl_seconds": self.ttl,
                "expired_count": expired,
                "persisted": self._cache_file is not None,
            }

    # ------------------------------------------------------------------
    # Disk persistence
    # ------------------------------------------------------------------

    def _save(self) -> None:
        """Write cache to JSON file."""
        try:
            data = {
                "version": CACHE_VERSION,
                "ttl": self.ttl,
                "entries": {
                    k: {"value": v["value"], "time": v["time"]}
                    for k, v in self.cache.items()
                },
            }
            self._cache_file.write_text(
                json.dumps(data, indent=2), encoding="utf-8"
            )
        except OSError as exc:
            log.warning("Failed to save cache: %s", exc)

    def _load(self) -> None:
        """Restore cache from JSON file, discarding already-expired entries."""
        if self._cache_file is None or not self._cache_file.exists():
            return
        try:
            raw = self._cache_file.read_text(encoding="utf-8")
            data = json.loads(raw)
            if data.get("version") != CACHE_VERSION:
                return  # incompatible format → skip load
            now = time.time()
            loaded = 0
            for key, entry in data.get("entries", {}).items():
                entry_time = entry.get("time", 0)
                if now - entry_time < self.ttl:
                    self.cache[key] = {"value": entry["value"], "time": entry_time}
                    loaded += 1
            log.debug("Loaded %d entries from %s", loaded, self._cache_file)
        except (json.JSONDecodeError, OSError) as exc:
            log.warning("Failed to load cache from %s: %s", self._cache_file, exc)


# Global singleton for simple import-and-use scenarios
response_cache = ResponseCache()
