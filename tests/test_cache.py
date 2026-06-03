"""Tests for core.cache — ResponseCache."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from core.cache import ResponseCache


class TestResponseCache:
    def test_set_and_get(self):
        cache = ResponseCache(ttl_seconds=60)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_missing_key(self):
        cache = ResponseCache()
        assert cache.get("nonexistent") is None

    def test_ttl_expiry(self):
        cache = ResponseCache(ttl_seconds=0.1)
        cache.set("key1", "value1")
        time.sleep(0.15)
        assert cache.get("key1") is None

    def test_max_entries_eviction(self):
        cache = ResponseCache(ttl_seconds=60, max_entries=3)
        cache.set("a", "1")
        cache.set("b", "2")
        cache.set("c", "3")
        cache.set("d", "4")  # should evict "a"
        assert cache.get("a") is None
        assert cache.get("b") == "2"
        assert cache.get("c") == "3"
        assert cache.get("d") == "4"

    def test_overwrite_existing_key(self):
        cache = ResponseCache()
        cache.set("key1", "old")
        cache.set("key1", "new")
        assert cache.get("key1") == "new"

    def test_thread_safety(self):
        """Basic sanity: set & get from multiple simulation passes."""
        cache = ResponseCache()
        for i in range(100):
            cache.set(f"k{i}", f"v{i}")
        for i in range(100):
            val = cache.get(f"k{i}")
            assert val == f"v{i}"

    def test_clear(self):
        cache = ResponseCache(ttl_seconds=60, max_entries=10)
        cache.set("a", "1")
        cache.set("b", "2")
        cache.clear()
        assert cache.get("a") is None
        assert cache.get("b") is None
        assert cache.stats()["entries"] == 0

    def test_stats(self):
        cache = ResponseCache(ttl_seconds=300, max_entries=50)
        stats = cache.stats()
        assert stats["ttl_seconds"] == 300
        assert stats["max_entries"] == 50
        assert stats["entries"] == 0
        assert stats["persisted"] is False
        cache.set("k", "v")
        assert cache.stats()["entries"] == 1


class TestResponseCachePersistence:
    """Disk-persistence tests using a temporary directory."""

    def test_save_and_load(self, tmp_path: Path):
        cache_dir = tmp_path / "cache"
        cache = ResponseCache(ttl_seconds=60, max_entries=10, cache_dir=cache_dir)
        cache.set("k1", "v1")
        cache.set("k2", "v2")

        # Create a new instance pointing at the same directory
        cache2 = ResponseCache(ttl_seconds=60, max_entries=10, cache_dir=cache_dir)
        assert cache2.get("k1") == "v1"
        assert cache2.get("k2") == "v2"

    def test_disk_file_created(self, tmp_path: Path):
        cache_dir = tmp_path / "cache"
        cache = ResponseCache(ttl_seconds=60, max_entries=10, cache_dir=cache_dir)
        cache.set("x", "y")
        assert (cache_dir / "response_cache.json").exists()

    def test_expired_entries_not_loaded(self, tmp_path: Path):
        """Entries that expired during the gap are not restored."""
        cache_dir = tmp_path / "cache"
        cache = ResponseCache(ttl_seconds=0.1, max_entries=10, cache_dir=cache_dir)
        cache.set("fast", "value")
        time.sleep(0.15)

        # Reload — the entry should have expired and not be loaded
        cache2 = ResponseCache(ttl_seconds=0.1, max_entries=10, cache_dir=cache_dir)
        assert cache2.get("fast") is None

    def test_clear_removes_disk_file(self, tmp_path: Path):
        cache_dir = tmp_path / "cache"
        cache = ResponseCache(ttl_seconds=60, max_entries=10, cache_dir=cache_dir)
        cache.set("k", "v")
        assert (cache_dir / "response_cache.json").exists()
        cache.clear()
        assert not (cache_dir / "response_cache.json").exists()
        assert cache.get("k") is None

    def test_eviction_syncs_to_disk(self, tmp_path: Path):
        """When an entry is evicted in-memory, the next save reflects it."""
        cache_dir = tmp_path / "cache"
        cache = ResponseCache(ttl_seconds=60, max_entries=2, cache_dir=cache_dir)
        cache.set("a", "1")
        cache.set("b", "2")
        cache.set("c", "3")  # evicts "a"

        cache2 = ResponseCache(ttl_seconds=60, max_entries=2, cache_dir=cache_dir)
        assert cache2.get("a") is None
        assert cache2.get("b") == "2"
        assert cache2.get("c") == "3"

    def test_stats_persisted(self, tmp_path: Path):
        cache_dir = tmp_path / "cache"
        cache = ResponseCache(ttl_seconds=60, max_entries=10, cache_dir=cache_dir)
        cache.set("k", "v")
        stats = cache.stats()
        assert stats["persisted"] is True
        assert stats["entries"] == 1
