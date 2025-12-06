"""In-memory TTL cache for API responses.

This module implements a time-to-live cache with FIFO eviction for storing
NSIP API responses to reduce redundant calls.
"""

import json
import logging
import time
from typing import TYPE_CHECKING, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Import metrics for tracking (avoid circular import by importing at module level after logger)
if TYPE_CHECKING:
    from nsip_mcp.metrics import ServerMetrics

server_metrics: Optional["ServerMetrics"] = None  # type: ignore[assignment]
try:
    from nsip_mcp.metrics import server_metrics as _server_metrics

    server_metrics = _server_metrics
except ImportError:
    # Gracefully handle if metrics not available (e.g., during testing)
    pass


class TtlCache:
    """Time-based cache with expiration and size limits.

    Attributes:
        ttl_seconds: Time-to-live for cache entries in seconds
        max_size: Maximum number of entries before eviction
        hits: Number of cache hits (for metrics)
        misses: Number of cache misses (for metrics)
    """

    def __init__(self, ttl_seconds: int = 3600, max_size: int = 1000):
        """Initialize TTL cache.

        Args:
            ttl_seconds: TTL in seconds (default: 3600 = 1 hour)
            max_size: Maximum cache size (default: 1000 entries)
        """
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._cache: dict[str, tuple[Any, float]] = {}
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Any | None:
        """Retrieve value from cache if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value if found and not expired, None otherwise

        Note:
            Gracefully handles errors by logging warning and returning None
        """
        try:
            if key in self._cache:
                value, expiration = self._cache[key]
                if time.time() < expiration:
                    self.hits += 1
                    # Record cache hit in server metrics (SC-006)
                    if server_metrics:
                        server_metrics.record_cache_hit()
                    return value
                else:
                    # Expired, remove from cache
                    del self._cache[key]

            self.misses += 1
            # Record cache miss in server metrics (SC-006)
            if server_metrics:
                server_metrics.record_cache_miss()
            return None

        except Exception as e:
            # Log error and fail gracefully (T040)
            logger.warning(f"Cache get failed for key '{key}': {e}. Bypassing cache.")
            self.misses += 1
            # Record cache miss even on error
            if server_metrics:
                server_metrics.record_cache_miss()
            return None

    def set(self, key: str, value: Any) -> None:
        """Store value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache

        Note:
            Gracefully handles errors by logging warning and failing silently
        """
        try:
            # FIFO eviction if cache is full
            if len(self._cache) >= self.max_size and key not in self._cache:
                # Remove oldest entry (first inserted)
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]

            expiration = time.time() + self.ttl_seconds
            self._cache[key] = (value, expiration)

        except Exception as e:
            # Log error and fail gracefully (T040)
            logger.warning(f"Cache set failed for key '{key}': {e}. Skipping cache storage.")
            # Don't re-raise - just skip caching this value

    def make_key(self, method_name: str, **params) -> str:
        """Generate deterministic cache key from method name and parameters.

        The key format is: method_name:sorted_json_params
        Parameters are sorted by key to ensure the same parameters always
        generate the same key regardless of order.

        Args:
            method_name: Name of the API method
            **params: Method parameters

        Returns:
            Cache key string

        Example:
            >>> cache.make_key("get_animal_details", search_string="6####92020###249")
            "get_animal_details:{\"search_string\":\"6####92020###249\"}"
        """
        sorted_params = json.dumps(params, sort_keys=True)
        return f"{method_name}:{sorted_params}"

    def hit_rate(self) -> float:
        """Calculate cache hit rate as percentage.

        Returns:
            Hit rate as percentage (0-100), or 0.0 if no accesses
        """
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0

    def clear(self) -> None:
        """Clear all cache entries and reset metrics."""
        self._cache.clear()
        self.hits = 0
        self.misses = 0


# Global cache instance for API responses
response_cache = TtlCache(ttl_seconds=3600, max_size=1000)
