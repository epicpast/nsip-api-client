"""
Unit tests for TTL cache infrastructure

Tests:
- Cache get/set operations
- TTL expiration behavior (1-hour default)
- FIFO eviction when max_size (1000) reached
- make_key determinism (same params → same key)
- Cache metrics tracking (hits/misses, hit rate)
- Thread safety for concurrent operations

Target: >90% coverage (SC-011)
"""

import time
from concurrent.futures import ThreadPoolExecutor

from nsip_mcp.cache import TtlCache, response_cache


class TestTtlCache:
    """Tests for TtlCache class."""

    def test_get_set_operations(self):
        """Verify basic cache get/set functionality."""
        cache = TtlCache(ttl_seconds=3600, max_size=100)

        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        cache.set("key2", {"data": "complex"})
        assert cache.get("key2") == {"data": "complex"}

    def test_cache_hit(self):
        """Verify cache returns value when key exists and not expired."""
        cache = TtlCache(ttl_seconds=3600)

        cache.set("test_key", "test_value")
        result = cache.get("test_key")

        assert result == "test_value"
        assert cache.hits == 1
        assert cache.misses == 0

    def test_cache_miss_nonexistent_key(self):
        """Verify cache returns None for nonexistent keys."""
        cache = TtlCache()

        result = cache.get("nonexistent")

        assert result is None
        assert cache.hits == 0
        assert cache.misses == 1

    def test_cache_miss_expired_entry(self):
        """Verify cache returns None for expired entries."""
        cache = TtlCache(ttl_seconds=1)  # 1 second TTL

        cache.set("expire_key", "expire_value")
        time.sleep(1.1)  # Wait for expiration
        result = cache.get("expire_key")

        assert result is None
        assert cache.misses == 1

    def test_multiple_get_increments_hits(self):
        """Verify multiple successful gets increment hit counter."""
        cache = TtlCache()

        cache.set("key", "value")
        cache.get("key")
        cache.get("key")
        cache.get("key")

        assert cache.hits == 3
        assert cache.misses == 0


class TestTtlExpiration:
    """Tests for TTL (Time-To-Live) expiration behavior."""

    def test_entry_expires_after_ttl(self):
        """Verify cache entries expire after TTL seconds."""
        cache = TtlCache(ttl_seconds=1)

        cache.set("key", "value")
        assert cache.get("key") == "value"  # Within TTL

        time.sleep(1.1)  # Wait for expiration
        assert cache.get("key") is None  # Expired

    def test_entry_accessible_before_expiration(self):
        """Verify cache entries accessible before TTL expires."""
        cache = TtlCache(ttl_seconds=2)

        cache.set("key", "value")
        time.sleep(0.5)  # Half the TTL

        assert cache.get("key") == "value"  # Still valid

    def test_expired_entry_auto_deleted(self):
        """Verify expired entries are automatically deleted on get."""
        cache = TtlCache(ttl_seconds=1)

        cache.set("key", "value")
        assert len(cache._cache) == 1

        time.sleep(1.1)  # Wait for expiration
        cache.get("key")  # Triggers deletion

        assert len(cache._cache) == 0  # Entry removed

    def test_different_ttl_values(self):
        """Verify TTL works with different durations."""
        short_cache = TtlCache(ttl_seconds=1)
        long_cache = TtlCache(ttl_seconds=10)

        short_cache.set("key", "value1")
        long_cache.set("key", "value2")

        time.sleep(1.5)

        assert short_cache.get("key") is None  # Expired
        assert long_cache.get("key") == "value2"  # Still valid

    def test_default_ttl_3600_seconds(self):
        """Verify default TTL is 3600 seconds (1 hour)."""
        cache = TtlCache()
        assert cache.ttl_seconds == 3600


class TestFifoEviction:
    """Tests for FIFO (First-In-First-Out) eviction policy."""

    def test_eviction_when_full(self):
        """Verify oldest entry evicted when max_size reached."""
        cache = TtlCache(max_size=3)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        cache.set("key4", "value4")  # Triggers eviction of key1

        assert cache.get("key1") is None  # Evicted
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"

    def test_eviction_order_fifo(self):
        """Verify eviction follows FIFO order (oldest first)."""
        cache = TtlCache(max_size=2)

        cache.set("first", "1")
        cache.set("second", "2")
        cache.set("third", "3")  # Evicts "first"

        assert cache.get("first") is None
        assert cache.get("second") == "2"
        assert cache.get("third") == "3"

        cache.set("fourth", "4")  # Evicts "second"

        assert cache.get("second") is None
        assert cache.get("third") == "3"
        assert cache.get("fourth") == "4"

    def test_max_size_enforcement(self):
        """Verify cache never exceeds max_size limit."""
        cache = TtlCache(max_size=5)

        for i in range(10):
            cache.set(f"key{i}", f"value{i}")
            assert len(cache._cache) <= 5

    def test_update_existing_key_no_eviction(self):
        """Verify updating existing key doesn't trigger eviction."""
        cache = TtlCache(max_size=3)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        cache.set("key1", "updated")  # Update, not eviction

        assert len(cache._cache) == 3
        assert cache.get("key1") == "updated"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

    def test_default_max_size_1000(self):
        """Verify default max_size is 1000."""
        cache = TtlCache()
        assert cache.max_size == 1000


class TestCacheKey:
    """Tests for cache key generation."""

    def test_make_key_format(self):
        """Verify cache key format: method_name:sorted_json_params."""
        cache = TtlCache()

        key = cache.make_key("get_animal", search_string="ABC123")

        assert key.startswith("get_animal:")
        assert "search_string" in key
        assert "ABC123" in key

    def test_make_key_determinism(self):
        """Verify same params always generate same key."""
        cache = TtlCache()

        key1 = cache.make_key("method", param1="value1", param2="value2")
        key2 = cache.make_key("method", param1="value1", param2="value2")

        assert key1 == key2

    def test_make_key_param_order_independence(self):
        """Verify param order doesn't affect cache key (sorted)."""
        cache = TtlCache()

        key1 = cache.make_key("method", a="1", b="2", c="3")
        key2 = cache.make_key("method", c="3", a="1", b="2")
        key3 = cache.make_key("method", b="2", c="3", a="1")

        assert key1 == key2 == key3

    def test_make_key_different_methods(self):
        """Verify different method names produce different keys."""
        cache = TtlCache()

        key1 = cache.make_key("method1", param="value")
        key2 = cache.make_key("method2", param="value")

        assert key1 != key2

    def test_make_key_different_params(self):
        """Verify different parameters produce different keys."""
        cache = TtlCache()

        key1 = cache.make_key("method", param="value1")
        key2 = cache.make_key("method", param="value2")

        assert key1 != key2

    def test_make_key_complex_params(self):
        """Verify cache key handles complex parameter types."""
        cache = TtlCache()

        key1 = cache.make_key("search", breed_id=123, filters={"active": True})
        key2 = cache.make_key("search", breed_id=123, filters={"active": True})

        assert key1 == key2

    def test_make_key_no_params(self):
        """Verify cache key works with no parameters."""
        cache = TtlCache()

        key = cache.make_key("get_all")

        assert key == "get_all:{}"


class TestCacheMetrics:
    """Tests for cache metrics tracking."""

    def test_hit_counter_increments(self):
        """Verify cache hit counter increments on hits."""
        cache = TtlCache()

        cache.set("key", "value")
        assert cache.hits == 0

        cache.get("key")
        assert cache.hits == 1

        cache.get("key")
        assert cache.hits == 2

    def test_miss_counter_increments(self):
        """Verify cache miss counter increments on misses."""
        cache = TtlCache()

        cache.get("nonexistent1")
        assert cache.misses == 1

        cache.get("nonexistent2")
        assert cache.misses == 2

    def test_hit_rate_calculation(self):
        """Verify cache hit rate calculation (SC-006 target: 40%)."""
        cache = TtlCache()

        # Initially 0% (no accesses)
        assert cache.hit_rate() == 0.0

        # Set up cache
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        # 2 hits, 0 misses = 100%
        cache.get("key1")
        cache.get("key2")
        assert cache.hit_rate() == 100.0

        # 2 hits, 2 misses = 50%
        cache.get("nonexistent1")
        cache.get("nonexistent2")
        assert cache.hit_rate() == 50.0

        # 3 hits, 2 misses = 60%
        cache.get("key1")
        assert cache.hit_rate() == 60.0

    def test_hit_rate_boundary_cases(self):
        """Test hit rate calculation edge cases."""
        cache = TtlCache()

        # No accesses
        assert cache.hit_rate() == 0.0

        # Only misses
        cache.get("miss1")
        cache.get("miss2")
        assert cache.hit_rate() == 0.0

        # Only hits
        cache.set("key", "value")
        cache.get("key")
        cache.get("key")
        # 2 hits, 2 misses from before
        total_hits = cache.hits
        total_accesses = cache.hits + cache.misses
        expected = (total_hits / total_accesses) * 100
        assert cache.hit_rate() == expected

    def test_clear_resets_metrics(self):
        """Verify clear() resets both cache and metrics."""
        cache = TtlCache()

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.get("key1")
        cache.get("nonexistent")

        assert cache.hits > 0
        assert cache.misses > 0
        assert len(cache._cache) > 0

        cache.clear()

        assert cache.hits == 0
        assert cache.misses == 0
        assert len(cache._cache) == 0
        assert cache.hit_rate() == 0.0


class TestCacheThreadSafety:
    """Tests for thread safety of cache operations."""

    def test_concurrent_reads(self):
        """Verify cache handles concurrent reads safely."""
        cache = TtlCache()
        cache.set("key", "value")

        def read_cache():
            return cache.get("key")

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(read_cache) for _ in range(100)]
            results = [f.result() for f in futures]

        # All reads should succeed
        assert all(result == "value" for result in results)
        assert cache.hits == 100

    def test_concurrent_writes(self):
        """Verify cache handles concurrent writes safely."""
        cache = TtlCache()

        def write_cache(i):
            cache.set(f"key{i}", f"value{i}")

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(write_cache, i) for i in range(100)]
            for f in futures:
                f.result()

        # All writes should succeed
        assert len(cache._cache) <= cache.max_size

    def test_concurrent_mixed_operations(self):
        """Verify cache handles mixed concurrent operations."""
        cache = TtlCache(max_size=50)

        def mixed_operations(i):
            cache.set(f"key{i}", f"value{i}")
            cache.get(f"key{i}")
            cache.get(f"nonexistent{i}")

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(mixed_operations, i) for i in range(50)]
            for f in futures:
                f.result()

        # Metrics should be consistent
        assert cache.hits + cache.misses > 0
        assert len(cache._cache) <= cache.max_size


class TestGlobalCacheInstance:
    """Tests for global response_cache instance."""

    def test_global_cache_initialized(self):
        """Verify global response_cache is initialized with correct settings."""
        assert response_cache.ttl_seconds == 3600
        assert response_cache.max_size == 1000

    def test_global_cache_is_singleton(self):
        """Verify response_cache is a singleton instance."""
        from nsip_mcp.cache import response_cache as cache2

        assert response_cache is cache2

    def test_global_cache_functional(self):
        """Verify global cache works for basic operations."""
        # Clear any existing data
        response_cache.clear()

        response_cache.set("test_key", "test_value")
        assert response_cache.get("test_key") == "test_value"

        # Clean up
        response_cache.clear()


class TestCacheEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_set_none_value(self):
        """Verify cache can store None values."""
        cache = TtlCache()

        cache.set("key", None)
        result = cache.get("key")

        assert result is None
        assert cache.hits == 1  # Should be a hit, not a miss

    def test_empty_string_key(self):
        """Verify cache handles empty string keys."""
        cache = TtlCache()

        cache.set("", "empty_key_value")
        assert cache.get("") == "empty_key_value"

    def test_large_value_storage(self):
        """Verify cache can store large values."""
        cache = TtlCache()
        large_value = "x" * 10000

        cache.set("large", large_value)
        assert cache.get("large") == large_value

    def test_unicode_keys_and_values(self):
        """Verify cache handles Unicode in keys and values."""
        cache = TtlCache()

        cache.set("日本語", "こんにちは")
        assert cache.get("日本語") == "こんにちは"

        key = cache.make_key("method", param="データ")
        # Accept either raw Unicode or JSON-encoded Unicode (\uXXXX format)
        assert "データ" in key or "\\u30c7\\u30fc\\u30bf" in key

    def test_get_exception_handling(self):
        """Verify cache.get handles exceptions gracefully."""
        cache = TtlCache()

        # Manually corrupt the cache to cause an exception
        # Store a value with a corrupted expiration
        cache._cache["bad_key"] = "not_a_tuple"  # Should be (value, expiration)

        # get should not raise, should return None and count as miss
        result = cache.get("bad_key")
        assert result is None
        assert cache.misses == 1

    def test_set_exception_handling(self):
        """Verify cache.set handles exceptions gracefully."""
        cache = TtlCache(max_size=2)

        # Store values before we replace the cache dict
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        # Create a mock dict that raises on setitem for key3
        original_cache = cache._cache.copy()

        class FailingDict(dict):
            def __setitem__(self, key, value):
                if key == "key3":
                    raise RuntimeError("Mock error")
                super().__setitem__(key, value)

        failing_dict = FailingDict(original_cache)
        cache._cache = failing_dict

        # This should not raise - just skip caching
        cache.set("key3", "value3")

        # Restore original cache and check values
        cache._cache = original_cache
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
