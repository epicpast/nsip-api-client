"""Server metrics tracking for MCP performance and success criteria validation.

This module implements ServerMetrics dataclass for tracking:
- Discovery times (SC-001: <5 seconds)
- Summarization reductions (SC-002: >=70%)
- Validation success rate (SC-003: >=95%)
- Cache hit rate (SC-006: >=40%)
- Concurrent connections (SC-005: support 50+)
"""

from dataclasses import dataclass, field
from threading import RLock
from typing import List


@dataclass
class ServerMetrics:
    """Server performance and success criteria metrics.

    Attributes:
        discovery_times: List of tool discovery times in seconds
        summarization_reductions: List of reduction percentages
        validation_attempts: Total validation attempts
        validation_successes: Successful validations (caught before API)
        cache_hits: Number of cache hits
        cache_misses: Number of cache misses
        concurrent_connections: Current number of active connections
        peak_connections: Maximum concurrent connections observed
        startup_time: Server startup time in seconds
    """

    discovery_times: List[float] = field(default_factory=list)
    summarization_reductions: List[float] = field(default_factory=list)
    validation_attempts: int = 0
    validation_successes: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    concurrent_connections: int = 0
    peak_connections: int = 0
    startup_time: float = 0.0
    _lock: RLock = field(default_factory=RLock, repr=False)

    def record_discovery_time(self, duration: float) -> None:
        """Record a tool discovery time.

        Args:
            duration: Discovery time in seconds
        """
        with self._lock:
            self.discovery_times.append(duration)

    def record_summarization(self, reduction_percent: float) -> None:
        """Record a summarization reduction percentage.

        Args:
            reduction_percent: Reduction percentage (0-100)
        """
        with self._lock:
            self.summarization_reductions.append(reduction_percent)

    def record_validation(self, success: bool) -> None:
        """Record a validation attempt.

        Args:
            success: True if validation caught invalid input
        """
        with self._lock:
            self.validation_attempts += 1
            if success:
                self.validation_successes += 1

    def record_cache_hit(self) -> None:
        """Record a cache hit."""
        with self._lock:
            self.cache_hits += 1

    def record_cache_miss(self) -> None:
        """Record a cache miss."""
        with self._lock:
            self.cache_misses += 1

    def increment_connections(self) -> None:
        """Increment concurrent connection count."""
        with self._lock:
            self.concurrent_connections += 1
            if self.concurrent_connections > self.peak_connections:
                self.peak_connections = self.concurrent_connections

    def decrement_connections(self) -> None:
        """Decrement concurrent connection count."""
        with self._lock:
            self.concurrent_connections = max(0, self.concurrent_connections - 1)

    def set_startup_time(self, duration: float) -> None:
        """Set server startup time.

        Args:
            duration: Startup time in seconds
        """
        with self._lock:
            self.startup_time = duration

    def get_avg_discovery_time(self) -> float:
        """Get average discovery time.

        Returns:
            Average discovery time in seconds, or 0 if no data
        """
        with self._lock:
            if not self.discovery_times:
                return 0.0
            return sum(self.discovery_times) / len(self.discovery_times)

    def get_avg_summarization_reduction(self) -> float:
        """Get average summarization reduction.

        Returns:
            Average reduction percentage, or 0 if no data
        """
        with self._lock:
            if not self.summarization_reductions:
                return 0.0
            return sum(self.summarization_reductions) / len(self.summarization_reductions)

    def get_validation_success_rate(self) -> float:
        """Get validation success rate.

        Returns:
            Success rate as percentage (0-100)
        """
        with self._lock:
            if self.validation_attempts == 0:
                return 0.0
            return (self.validation_successes / self.validation_attempts) * 100

    def get_cache_hit_rate(self) -> float:
        """Get cache hit rate.

        Returns:
            Hit rate as percentage (0-100)
        """
        with self._lock:
            total = self.cache_hits + self.cache_misses
            if total == 0:
                return 0.0
            return (self.cache_hits / total) * 100

    def meets_success_criteria(self) -> dict:
        """Check if metrics meet all success criteria.

        Returns:
            Dict with criteria names as keys and bool pass/fail as values

        Success Criteria:
            SC-001: Discovery time <5 seconds
            SC-002: Summarization reduction >=70%
            SC-003: Validation success rate >=95%
            SC-005: Support 50+ concurrent connections
            SC-006: Cache hit rate >=40%
            SC-007: Startup time <3 seconds
        """
        with self._lock:
            return {
                "SC-001 Discovery <5s": (
                    self.get_avg_discovery_time() < 5.0 if self.discovery_times else None
                ),
                "SC-002 Reduction >=70%": (
                    self.get_avg_summarization_reduction() >= 70.0
                    if self.summarization_reductions
                    else None
                ),
                "SC-003 Validation >=95%": (
                    self.get_validation_success_rate() >= 95.0
                    if self.validation_attempts > 0
                    else None
                ),
                "SC-005 Concurrent 50+": (
                    self.peak_connections >= 50 if self.peak_connections > 0 else None
                ),
                "SC-006 Cache >=40%": (
                    self.get_cache_hit_rate() >= 40.0
                    if (self.cache_hits + self.cache_misses) > 0
                    else None
                ),
                "SC-007 Startup <3s": self.startup_time < 3.0 if self.startup_time > 0 else None,
            }

    def to_dict(self) -> dict:
        """Convert metrics to dictionary for serialization.

        Returns:
            Dict containing all metrics and success criteria evaluation
        """
        with self._lock:
            return {
                "discovery": {
                    "avg_time_seconds": self.get_avg_discovery_time(),
                    "count": len(self.discovery_times),
                },
                "summarization": {
                    "avg_reduction_percent": self.get_avg_summarization_reduction(),
                    "count": len(self.summarization_reductions),
                },
                "validation": {
                    "success_rate_percent": self.get_validation_success_rate(),
                    "attempts": self.validation_attempts,
                    "successes": self.validation_successes,
                },
                "cache": {
                    "hit_rate_percent": self.get_cache_hit_rate(),
                    "hits": self.cache_hits,
                    "misses": self.cache_misses,
                },
                "connections": {
                    "current": self.concurrent_connections,
                    "peak": self.peak_connections,
                },
                "startup_time_seconds": self.startup_time,
                "success_criteria": self.meets_success_criteria(),
            }


# Global metrics instance
server_metrics = ServerMetrics()
