"""Unit tests for server metrics tracking.

Tests ServerMetrics dataclass for tracking performance and success criteria:
- Discovery times (SC-001: <5 seconds)
- Summarization reductions (SC-002: >=70%)
- Validation success rate (SC-003: >=95%)
- Cache hit rate (SC-006: >=40%)
- Concurrent connections (SC-005: support 50+)
- Startup time (SC-007: <3 seconds)
"""

import pytest

from nsip_mcp.metrics import ServerMetrics


class TestMetricsRecording:
    """Test recording of various metrics."""

    def test_record_discovery_time(self):
        """Verify discovery time recording."""
        metrics = ServerMetrics()

        metrics.record_discovery_time(1.5)
        metrics.record_discovery_time(2.3)
        metrics.record_discovery_time(3.1)

        assert len(metrics.discovery_times) == 3
        assert metrics.discovery_times == [1.5, 2.3, 3.1]

    def test_record_summarization(self):
        """Verify summarization reduction recording."""
        metrics = ServerMetrics()

        metrics.record_summarization(75.5)
        metrics.record_summarization(80.2)
        metrics.record_summarization(70.0)

        assert len(metrics.summarization_reductions) == 3
        assert metrics.summarization_reductions == [75.5, 80.2, 70.0]

    def test_record_validation_success(self):
        """Verify validation success recording."""
        metrics = ServerMetrics()

        metrics.record_validation(success=True)
        metrics.record_validation(success=True)
        metrics.record_validation(success=False)
        metrics.record_validation(success=True)

        assert metrics.validation_attempts == 4
        assert metrics.validation_successes == 3

    def test_record_cache_operations(self):
        """Verify cache hit/miss recording."""
        metrics = ServerMetrics()

        metrics.record_cache_hit()
        metrics.record_cache_hit()
        metrics.record_cache_miss()
        metrics.record_cache_hit()

        assert metrics.cache_hits == 3
        assert metrics.cache_misses == 1

    def test_connection_tracking(self):
        """Verify concurrent connection tracking."""
        metrics = ServerMetrics()

        metrics.increment_connections()
        metrics.increment_connections()
        assert metrics.concurrent_connections == 2
        assert metrics.peak_connections == 2

        metrics.increment_connections()
        assert metrics.concurrent_connections == 3
        assert metrics.peak_connections == 3

        metrics.decrement_connections()
        assert metrics.concurrent_connections == 2
        assert metrics.peak_connections == 3  # Peak stays at max

    def test_connection_never_negative(self):
        """Verify connection count never goes negative."""
        metrics = ServerMetrics()

        metrics.decrement_connections()
        metrics.decrement_connections()

        assert metrics.concurrent_connections == 0

    def test_set_startup_time(self):
        """Verify startup time setting."""
        metrics = ServerMetrics()

        metrics.set_startup_time(1.234)

        assert metrics.startup_time == 1.234


class TestMetricsCalculations:
    """Test metric calculation methods."""

    def test_avg_discovery_time(self):
        """Verify average discovery time calculation."""
        metrics = ServerMetrics()

        # Empty case
        assert metrics.get_avg_discovery_time() == 0.0

        # With data
        metrics.record_discovery_time(1.0)
        metrics.record_discovery_time(2.0)
        metrics.record_discovery_time(3.0)

        assert metrics.get_avg_discovery_time() == 2.0

    def test_avg_summarization_reduction(self):
        """Verify average summarization reduction calculation."""
        metrics = ServerMetrics()

        # Empty case
        assert metrics.get_avg_summarization_reduction() == 0.0

        # With data
        metrics.record_summarization(70.0)
        metrics.record_summarization(80.0)
        metrics.record_summarization(75.0)

        assert metrics.get_avg_summarization_reduction() == 75.0

    def test_validation_success_rate(self):
        """Verify validation success rate calculation."""
        metrics = ServerMetrics()

        # Empty case
        assert metrics.get_validation_success_rate() == 0.0

        # With data
        metrics.record_validation(success=True)
        metrics.record_validation(success=True)
        metrics.record_validation(success=False)
        metrics.record_validation(success=True)

        # 3 successes out of 4 attempts = 75%
        assert metrics.get_validation_success_rate() == 75.0

    def test_cache_hit_rate(self):
        """Verify cache hit rate calculation."""
        metrics = ServerMetrics()

        # Empty case
        assert metrics.get_cache_hit_rate() == 0.0

        # With data
        metrics.record_cache_hit()
        metrics.record_cache_hit()
        metrics.record_cache_miss()
        metrics.record_cache_hit()

        # 3 hits out of 4 total = 75%
        assert metrics.get_cache_hit_rate() == 75.0


class TestSuccessCriteria:
    """Test success criteria evaluation."""

    def test_sc001_discovery_time(self):
        """Verify SC-001: Discovery time <5 seconds."""
        metrics = ServerMetrics()

        # No data yet
        criteria = metrics.meets_success_criteria()
        assert criteria["SC-001 Discovery <5s"] is None

        # Passing case
        metrics.record_discovery_time(2.5)
        metrics.record_discovery_time(3.0)
        criteria = metrics.meets_success_criteria()
        assert criteria["SC-001 Discovery <5s"] is True

        # Failing case
        metrics.record_discovery_time(10.0)
        criteria = metrics.meets_success_criteria()
        assert criteria["SC-001 Discovery <5s"] is False

    def test_sc002_summarization_reduction(self):
        """Verify SC-002: Summarization reduction >=70%."""
        metrics = ServerMetrics()

        # No data yet
        criteria = metrics.meets_success_criteria()
        assert criteria["SC-002 Reduction >=70%"] is None

        # Passing case
        metrics.record_summarization(75.0)
        metrics.record_summarization(80.0)
        criteria = metrics.meets_success_criteria()
        assert criteria["SC-002 Reduction >=70%"] is True

        # Failing case
        metrics.record_summarization(50.0)
        criteria = metrics.meets_success_criteria()
        assert criteria["SC-002 Reduction >=70%"] is False

    def test_sc003_validation_rate(self):
        """Verify SC-003: Validation success rate >=95%."""
        metrics = ServerMetrics()

        # No data yet
        criteria = metrics.meets_success_criteria()
        assert criteria["SC-003 Validation >=95%"] is None

        # Passing case
        for _ in range(19):
            metrics.record_validation(success=True)
        metrics.record_validation(success=False)
        criteria = metrics.meets_success_criteria()
        # 19/20 = 95%
        assert criteria["SC-003 Validation >=95%"] is True

        # Failing case
        metrics.record_validation(success=False)
        metrics.record_validation(success=False)
        criteria = metrics.meets_success_criteria()
        # 19/22 = 86.4%
        assert criteria["SC-003 Validation >=95%"] is False

    def test_sc005_concurrent_connections(self):
        """Verify SC-005: Support 50+ concurrent connections."""
        metrics = ServerMetrics()

        # No data yet
        criteria = metrics.meets_success_criteria()
        assert criteria["SC-005 Concurrent 50+"] is None

        # Passing case
        for _ in range(50):
            metrics.increment_connections()
        criteria = metrics.meets_success_criteria()
        assert criteria["SC-005 Concurrent 50+"] is True

        # Decrement doesn't affect peak
        for _ in range(40):
            metrics.decrement_connections()
        criteria = metrics.meets_success_criteria()
        assert criteria["SC-005 Concurrent 50+"] is True

    def test_sc006_cache_hit_rate(self):
        """Verify SC-006: Cache hit rate >=40%."""
        metrics = ServerMetrics()

        # No data yet
        criteria = metrics.meets_success_criteria()
        assert criteria["SC-006 Cache >=40%"] is None

        # Passing case
        for _ in range(8):
            metrics.record_cache_hit()
        for _ in range(2):
            metrics.record_cache_miss()
        criteria = metrics.meets_success_criteria()
        # 8/10 = 80%
        assert criteria["SC-006 Cache >=40%"] is True

        # Failing case
        for _ in range(10):
            metrics.record_cache_miss()
        criteria = metrics.meets_success_criteria()
        # 8/20 = 40% (edge case - should pass)
        assert criteria["SC-006 Cache >=40%"] is True

        # Actually failing
        for _ in range(10):
            metrics.record_cache_miss()
        criteria = metrics.meets_success_criteria()
        # 8/30 = 26.7%
        assert criteria["SC-006 Cache >=40%"] is False

    def test_sc007_startup_time(self):
        """Verify SC-007: Startup time <3 seconds."""
        metrics = ServerMetrics()

        # No data yet
        criteria = metrics.meets_success_criteria()
        assert criteria["SC-007 Startup <3s"] is None

        # Passing case
        metrics.set_startup_time(1.5)
        criteria = metrics.meets_success_criteria()
        assert criteria["SC-007 Startup <3s"] is True

        # Failing case
        metrics.set_startup_time(5.0)
        criteria = metrics.meets_success_criteria()
        assert criteria["SC-007 Startup <3s"] is False


class TestMetricsToDict:
    """Test metrics serialization."""

    def test_to_dict_empty_metrics(self):
        """Verify to_dict() with no recorded metrics."""
        metrics = ServerMetrics()

        data = metrics.to_dict()

        assert data["discovery"]["avg_time_seconds"] == 0.0
        assert data["discovery"]["count"] == 0
        assert data["summarization"]["avg_reduction_percent"] == 0.0
        assert data["validation"]["success_rate_percent"] == 0.0
        assert data["cache"]["hit_rate_percent"] == 0.0
        assert data["connections"]["current"] == 0
        assert data["connections"]["peak"] == 0
        assert data["startup_time_seconds"] == 0.0
        assert "success_criteria" in data

    def test_to_dict_with_metrics(self):
        """Verify to_dict() with recorded metrics."""
        metrics = ServerMetrics()

        # Record some metrics
        metrics.record_discovery_time(2.0)
        metrics.record_summarization(75.0)
        metrics.record_validation(success=True)
        metrics.record_validation(success=True)
        metrics.record_validation(success=False)
        metrics.record_cache_hit()
        metrics.record_cache_miss()
        metrics.increment_connections()
        metrics.set_startup_time(1.5)

        data = metrics.to_dict()

        assert data["discovery"]["avg_time_seconds"] == 2.0
        assert data["discovery"]["count"] == 1
        assert data["summarization"]["avg_reduction_percent"] == 75.0
        assert data["summarization"]["count"] == 1
        assert data["validation"]["success_rate_percent"] == pytest.approx(66.67, rel=0.01)
        assert data["validation"]["attempts"] == 3
        assert data["validation"]["successes"] == 2
        assert data["cache"]["hit_rate_percent"] == 50.0
        assert data["cache"]["hits"] == 1
        assert data["cache"]["misses"] == 1
        assert data["connections"]["current"] == 1
        assert data["connections"]["peak"] == 1
        assert data["startup_time_seconds"] == 1.5
        assert data["success_criteria"]["SC-001 Discovery <5s"] is True
        assert data["success_criteria"]["SC-007 Startup <3s"] is True
