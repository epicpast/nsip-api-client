"""Server metrics tracking for MCP performance and success criteria validation.

This module implements ServerMetrics dataclass for tracking:
- Discovery times (SC-001: <5 seconds)
- Summarization reductions (SC-002: >=70%)
- Validation success rate (SC-003: >=95%)
- Cache hit rate (SC-006: >=40%)
- Concurrent connections (SC-005: support 50+)
"""

from collections import deque
from dataclasses import dataclass, field
from threading import RLock

# Maximum entries to retain in rolling metric lists to prevent unbounded memory growth
MAX_METRIC_ENTRIES = 10000


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
        resource_accesses: Count of resource accesses by URI pattern
        resource_latencies: Resource access latencies in seconds
        prompt_executions: Count of prompt executions by name
        prompt_successes: Count of successful prompt completions
        prompt_failures: Count of failed prompt executions
        sampling_requests: Count of sampling requests
        sampling_tokens_in: Total input tokens for sampling
        sampling_tokens_out: Total output tokens from sampling
        kb_accesses: Count of knowledge base accesses by file
    """

    # Use bounded deques to prevent unbounded memory growth in long-running servers
    discovery_times: deque[float] = field(default_factory=lambda: deque(maxlen=MAX_METRIC_ENTRIES))
    summarization_reductions: deque[float] = field(
        default_factory=lambda: deque(maxlen=MAX_METRIC_ENTRIES)
    )
    validation_attempts: int = 0
    validation_successes: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    concurrent_connections: int = 0
    peak_connections: int = 0
    startup_time: float = 0.0

    # Resource metrics
    resource_accesses: dict[str, int] = field(default_factory=dict)
    resource_latencies: deque[float] = field(
        default_factory=lambda: deque(maxlen=MAX_METRIC_ENTRIES)
    )

    # Prompt metrics
    prompt_executions: dict[str, int] = field(default_factory=dict)
    prompt_successes: int = 0
    prompt_failures: int = 0

    # Sampling metrics
    sampling_requests: int = 0
    sampling_tokens_in: int = 0
    sampling_tokens_out: int = 0

    # Knowledge base metrics
    kb_accesses: dict[str, int] = field(default_factory=dict)

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
            success: True if input passed validation, False if invalid
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

    def record_resource_access(self, uri_pattern: str, latency: float) -> None:
        """Record a resource access.

        Args:
            uri_pattern: The resource URI pattern (e.g., 'nsip://animals/{lpn_id}')
            latency: Access latency in seconds
        """
        with self._lock:
            self.resource_accesses[uri_pattern] = self.resource_accesses.get(uri_pattern, 0) + 1
            self.resource_latencies.append(latency)

    def record_prompt_execution(self, prompt_name: str, success: bool) -> None:
        """Record a prompt execution.

        Args:
            prompt_name: Name of the prompt executed
            success: True if execution succeeded
        """
        with self._lock:
            self.prompt_executions[prompt_name] = self.prompt_executions.get(prompt_name, 0) + 1
            if success:
                self.prompt_successes += 1
            else:
                self.prompt_failures += 1

    def record_sampling(self, tokens_in: int, tokens_out: int) -> None:
        """Record a sampling request.

        Args:
            tokens_in: Input tokens used
            tokens_out: Output tokens generated
        """
        with self._lock:
            self.sampling_requests += 1
            self.sampling_tokens_in += tokens_in
            self.sampling_tokens_out += tokens_out

    def record_kb_access(self, filename: str) -> None:
        """Record a knowledge base file access.

        Args:
            filename: Name of the KB file accessed
        """
        with self._lock:
            self.kb_accesses[filename] = self.kb_accesses.get(filename, 0) + 1

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

    def get_avg_resource_latency(self) -> float:
        """Get average resource access latency.

        Returns:
            Average latency in seconds, or 0 if no data
        """
        with self._lock:
            if not self.resource_latencies:
                return 0.0
            return sum(self.resource_latencies) / len(self.resource_latencies)

    def get_total_resource_accesses(self) -> int:
        """Get total number of resource accesses.

        Returns:
            Total resource access count
        """
        with self._lock:
            return sum(self.resource_accesses.values())

    def get_prompt_success_rate(self) -> float:
        """Get prompt execution success rate.

        Returns:
            Success rate as percentage (0-100)
        """
        with self._lock:
            total = self.prompt_successes + self.prompt_failures
            if total == 0:
                return 0.0
            return (self.prompt_successes / total) * 100

    def get_total_prompt_executions(self) -> int:
        """Get total number of prompt executions.

        Returns:
            Total prompt execution count
        """
        with self._lock:
            return sum(self.prompt_executions.values())

    def get_sampling_token_ratio(self) -> float:
        """Get output to input token ratio for sampling.

        Returns:
            Ratio of output to input tokens, or 0 if no sampling
        """
        with self._lock:
            if self.sampling_tokens_in == 0:
                return 0.0
            return self.sampling_tokens_out / self.sampling_tokens_in

    def get_total_kb_accesses(self) -> int:
        """Get total number of knowledge base accesses.

        Returns:
            Total KB access count
        """
        with self._lock:
            return sum(self.kb_accesses.values())

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
            SC-008: Resource latency <2 seconds
            SC-009: Prompt success rate >=90%
            SC-010: Sampling token efficiency (output/input ratio <3)
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
                "SC-008 Resource <2s": (
                    self.get_avg_resource_latency() < 2.0 if self.resource_latencies else None
                ),
                "SC-009 Prompt >=90%": (
                    self.get_prompt_success_rate() >= 90.0
                    if (self.prompt_successes + self.prompt_failures) > 0
                    else None
                ),
                "SC-010 Sampling ratio <3": (
                    self.get_sampling_token_ratio() < 3.0 if self.sampling_requests > 0 else None
                ),
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
                "resources": {
                    "total_accesses": self.get_total_resource_accesses(),
                    "avg_latency_seconds": self.get_avg_resource_latency(),
                    "by_uri": dict(self.resource_accesses),
                },
                "prompts": {
                    "total_executions": self.get_total_prompt_executions(),
                    "success_rate_percent": self.get_prompt_success_rate(),
                    "successes": self.prompt_successes,
                    "failures": self.prompt_failures,
                    "by_name": dict(self.prompt_executions),
                },
                "sampling": {
                    "requests": self.sampling_requests,
                    "tokens_in": self.sampling_tokens_in,
                    "tokens_out": self.sampling_tokens_out,
                    "token_ratio": self.get_sampling_token_ratio(),
                },
                "knowledge_base": {
                    "total_accesses": self.get_total_kb_accesses(),
                    "by_file": dict(self.kb_accesses),
                },
                "success_criteria": self.meets_success_criteria(),
            }


# Global metrics instance
server_metrics = ServerMetrics()
