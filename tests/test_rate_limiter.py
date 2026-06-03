"""Tests for core.rate_limiter — RateLimiter."""

from __future__ import annotations

import asyncio

import pytest

from core.rate_limiter import RateLimiter, RateLimitExceeded


class TestRateLimiter:
    def test_no_limit_configured(self):
        rl = RateLimiter()
        assert rl.is_allowed("anything") is True

    def test_basic_limit(self):
        rl = RateLimiter()
        rl.set_limit("test", max_requests=2, window_seconds=60)

        assert rl.is_allowed("test") is True
        assert rl.is_allowed("test") is True
        # Two tokens consumed — third should be blocked
        assert rl.is_allowed("test") is False

    def test_remaining(self):
        rl = RateLimiter()
        rl.set_limit("test", max_requests=3, window_seconds=60)

        assert rl.remaining("test") == 3
        rl.is_allowed("test")
        assert rl.remaining("test") == 2
        rl.is_allowed("test")
        assert rl.remaining("test") == 1
        rl.is_allowed("test")
        assert rl.remaining("test") == 0

    def test_reset(self):
        rl = RateLimiter()
        rl.set_limit("test", max_requests=1, window_seconds=60)
        rl.is_allowed("test")
        assert rl.is_allowed("test") is False
        rl.reset("test")
        assert rl.is_allowed("test") is True

    def test_window_expires(self):
        """After the window passes, tokens should refresh."""
        rl = RateLimiter()
        rl.set_limit("test", max_requests=1, window_seconds=0.1)

        assert rl.is_allowed("test") is True
        assert rl.is_allowed("test") is False
        time.sleep(0.15)
        assert rl.is_allowed("test") is True

    def test_multiple_keys_independent(self):
        rl = RateLimiter()
        rl.set_limit("a", max_requests=1, window_seconds=60)
        rl.set_limit("b", max_requests=5, window_seconds=60)

        assert rl.is_allowed("a") is True
        assert rl.is_allowed("a") is False  # a exhausted

        assert rl.is_allowed("b") is True   # b not affected
        assert rl.is_allowed("b") is True

    def test_remove_limit(self):
        rl = RateLimiter()
        rl.set_limit("test", max_requests=1, window_seconds=60)
        rl.is_allowed("test")
        assert rl.is_allowed("test") is False
        rl.remove_limit("test")
        assert rl.is_allowed("test") is True  # no limit → always allowed

    # --- Async context-manager ---

    @pytest.mark.asyncio
    async def test_async_acquire_allowed(self):
        rl = RateLimiter()
        rl.set_limit("test", max_requests=5, window_seconds=60)
        async with rl.acquire("test"):
            pass  # should not raise

    @pytest.mark.asyncio
    async def test_async_acquire_blocks_then_continues(self):
        rl = RateLimiter()
        rl.set_limit("test", max_requests=1, window_seconds=0.1)
        async with rl.acquire("test"):
            pass  # first token consumed

        # Second acquire should block until window expires
        t0 = asyncio.get_running_loop().time()
        async with rl.acquire("test"):
            elapsed = asyncio.get_running_loop().time() - t0
            assert elapsed >= 0.08  # should have waited ~0.1s


import time  # noqa: E402 (needed for test_window_expires)
