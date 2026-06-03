"""MARK XL — Rate Limiter.

Thread-safe rate limiter using a sliding-window token-bucket
algorithm.  Supports per-endpoint limits with configurable
window size and max requests per window.
"""

from __future__ import annotations

import time
import asyncio
import logging
from threading import Lock
from typing import Dict, Optional

log = logging.getLogger(__name__)


class RateLimitExceeded(Exception):
    """Raised when a rate limit is hit."""


class RateLimiter:
    """Sliding-window token-bucket rate limiter.

    Usage::

        rl = RateLimiter()
        rl.set_limit("ollama:chat", max_requests=30, window_seconds=60)

        async def chat():
            async with rl.acquire("ollama:chat"):
                return await do_chat()
    """

    def __init__(self) -> None:
        self._limits: Dict[str, tuple[int, float]] = {}      # key → (max_req, window_sec)
        self._buckets: Dict[str, list[float]] = {}            # key → [timestamps]
        self._lock = Lock()

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def set_limit(
        self, key: str, max_requests: int, window_seconds: float = 60.0
    ) -> None:
        """Configure a rate limit for *key*."""
        with self._lock:
            self._limits[key] = (max_requests, window_seconds)
            if key not in self._buckets:
                self._buckets[key] = []

    def remove_limit(self, key: str) -> None:
        """Remove a previously configured limit."""
        with self._lock:
            self._limits.pop(key, None)
            self._buckets.pop(key, None)

    # ------------------------------------------------------------------
    # Sync check
    # ------------------------------------------------------------------

    def try_acquire(self, key: str) -> bool:
        """Non-blocking acquire — returns **True** if token was consumed."""
        allowed, _ = self._acquire_or_wait(key)
        return allowed

    def is_allowed(self, key: str) -> bool:
        """Alias for :meth:`try_acquire`. Returns **True** if within limits."""
        return self.try_acquire(key)

    def remaining(self, key: str) -> int:
        """How many requests are still allowed in the current window."""
        with self._lock:
            limit, window = self._limits.get(key, (0, 60.0))
            if limit == 0:
                return 0
            now = time.monotonic()
            timestamps = self._buckets.get(key, [])
            cutoff = now - window
            # Prune expired entries
            timestamps = [t for t in timestamps if t > cutoff]
            self._buckets[key] = timestamps
            return max(0, limit - len(timestamps))

    def reset(self, key: Optional[str] = None) -> None:
        """Reset counters for *key* (or all keys)."""
        with self._lock:
            if key:
                self._buckets.pop(key, None)
            else:
                self._buckets.clear()

    # ------------------------------------------------------------------
    # Async context-manager (preferred)
    # ------------------------------------------------------------------

    def acquire(self, key: str) -> "_Ctx":
        """Return an async context manager that blocks when over limit."""
        return self._Ctx(self, key)

    class _Ctx:
        def __init__(self, outer: "RateLimiter", key: str) -> None:
            self._outer = outer
            self._key = key
            self._waited = False

        async def __aenter__(self) -> None:
            max_retries = 600  # ~60s at minimum 0.01s sleep
            for _ in range(max_retries):
                allowed, wait = self._outer._acquire_or_wait(self._key)
                if allowed:
                    return
                self._waited = True
                await asyncio.sleep(wait)
            # Fallback: try one last time and proceed anyway
            self._outer.reset(self._key)

        async def __aexit__(self, *_: object) -> None:
            pass

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _acquire_or_wait(self, key: str) -> tuple[bool, float]:
        """Try to acquire; return (allowed, seconds_to_wait)."""
        with self._lock:
            limit, window = self._limits.get(key, (0, 60.0))
            if limit == 0:
                return True, 0.0  # no limit configured → always allowed

            now = time.monotonic()
            cutoff = now - window
            timestamps = self._buckets.get(key, [])
            timestamps = [t for t in timestamps if t > cutoff]

            if len(timestamps) < limit:
                timestamps.append(now)
                self._buckets[key] = timestamps
                return True, 0.0

            # How long until the oldest timestamp expires?
            oldest = timestamps[0] if timestamps else now
            wait = max(0.01, oldest + window - now)
            log.warning(
                "Rate limit exceeded for %r — wait %.1fs (limit %d / %.0fs)",
                key, wait, limit, window,
            )
            return False, wait

    def _check(self, key: str) -> bool:
        """Check without consuming a token (for peek)."""
        limit, window = self._limits.get(key, (0, 60.0))
        if limit == 0:
            return True
        now = time.monotonic()
        cutoff = now - window
        timestamps = self._buckets.get(key, [])
        timestamps = [t for t in timestamps if t > cutoff]
        self._buckets[key] = timestamps
        return len(timestamps) < limit


# Global singleton
rate_limiter = RateLimiter()
