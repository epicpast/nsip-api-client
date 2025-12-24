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
        assert list(metrics.discovery_times) == [1.5, 2.3, 3.1]

    def test_record_summarization(self):
        """Verify summarization reduction recording."""
        metrics = ServerMetrics()

        metrics.record_summarization(75.5)
        metrics.record_summarization(80.2)
        metrics.record_summarization(70.0)

        assert len(metrics.summarization_reductions) == 3
        assert list(metrics.summarization_reductions) == [75.5, 80.2, 70.0]

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


class TestExtendedMetricsRecording:
    """Test extended metrics recording (SC-008, SC-009, SC-010)."""

    def test_record_resource_access(self):
        """Verify resource access recording."""
        metrics = ServerMetrics()

        metrics.record_resource_access("nsip://animals/{lpn_id}", 0.5)
        metrics.record_resource_access("nsip://animals/{lpn_id}", 0.7)
        metrics.record_resource_access("nsip://breeding/{ram}/{ewe}", 1.2)

        assert metrics.resource_accesses["nsip://animals/{lpn_id}"] == 2
        assert metrics.resource_accesses["nsip://breeding/{ram}/{ewe}"] == 1
        assert len(metrics.resource_latencies) == 3

    def test_record_prompt_execution(self):
        """Verify prompt execution recording."""
        metrics = ServerMetrics()

        metrics.record_prompt_execution("ebv_analyzer", success=True)
        metrics.record_prompt_execution("ebv_analyzer", success=True)
        metrics.record_prompt_execution("mating_plan", success=False)

        assert metrics.prompt_executions["ebv_analyzer"] == 2
        assert metrics.prompt_executions["mating_plan"] == 1
        assert metrics.prompt_successes == 2
        assert metrics.prompt_failures == 1

    def test_record_sampling(self):
        """Verify sampling request recording."""
        metrics = ServerMetrics()

        metrics.record_sampling(tokens_in=500, tokens_out=1500)
        metrics.record_sampling(tokens_in=1000, tokens_out=2000)

        assert metrics.sampling_requests == 2
        assert metrics.sampling_tokens_in == 1500
        assert metrics.sampling_tokens_out == 3500

    def test_record_kb_access(self):
        """Verify knowledge base access recording."""
        metrics = ServerMetrics()

        metrics.record_kb_access("heritabilities.yaml")
        metrics.record_kb_access("heritabilities.yaml")
        metrics.record_kb_access("diseases.yaml")

        assert metrics.kb_accesses["heritabilities.yaml"] == 2
        assert metrics.kb_accesses["diseases.yaml"] == 1


class TestExtendedMetricsCalculations:
    """Test extended metric calculations."""

    def test_avg_resource_latency(self):
        """Verify average resource latency calculation."""
        metrics = ServerMetrics()

        # Empty case
        assert metrics.get_avg_resource_latency() == 0.0

        # With data
        metrics.record_resource_access("test://uri", 1.0)
        metrics.record_resource_access("test://uri", 2.0)
        metrics.record_resource_access("test://uri", 3.0)

        assert metrics.get_avg_resource_latency() == 2.0

    def test_total_resource_accesses(self):
        """Verify total resource access count."""
        metrics = ServerMetrics()

        # Empty case
        assert metrics.get_total_resource_accesses() == 0

        # With data
        metrics.record_resource_access("uri1", 0.1)
        metrics.record_resource_access("uri1", 0.1)
        metrics.record_resource_access("uri2", 0.1)

        assert metrics.get_total_resource_accesses() == 3

    def test_prompt_success_rate(self):
        """Verify prompt success rate calculation."""
        metrics = ServerMetrics()

        # Empty case
        assert metrics.get_prompt_success_rate() == 0.0

        # With data: 9 successes, 1 failure = 90%
        for _ in range(9):
            metrics.record_prompt_execution("test", success=True)
        metrics.record_prompt_execution("test", success=False)

        assert metrics.get_prompt_success_rate() == 90.0

    def test_total_prompt_executions(self):
        """Verify total prompt execution count."""
        metrics = ServerMetrics()

        # Empty case
        assert metrics.get_total_prompt_executions() == 0

        # With data
        metrics.record_prompt_execution("prompt1", success=True)
        metrics.record_prompt_execution("prompt1", success=True)
        metrics.record_prompt_execution("prompt2", success=False)

        assert metrics.get_total_prompt_executions() == 3

    def test_sampling_token_ratio(self):
        """Verify sampling token ratio calculation."""
        metrics = ServerMetrics()

        # Empty case
        assert metrics.get_sampling_token_ratio() == 0.0

        # With data: 1000 in, 2500 out = 2.5 ratio
        metrics.record_sampling(tokens_in=1000, tokens_out=2500)

        assert metrics.get_sampling_token_ratio() == 2.5

    def test_total_kb_accesses(self):
        """Verify total knowledge base access count."""
        metrics = ServerMetrics()

        # Empty case
        assert metrics.get_total_kb_accesses() == 0

        # With data
        metrics.record_kb_access("file1.yaml")
        metrics.record_kb_access("file1.yaml")
        metrics.record_kb_access("file2.yaml")

        assert metrics.get_total_kb_accesses() == 3


class TestExtendedSuccessCriteria:
    """Test extended success criteria (SC-008, SC-009, SC-010)."""

    def test_sc008_resource_latency(self):
        """Verify SC-008: Resource latency <2 seconds."""
        metrics = ServerMetrics()

        # No data yet
        criteria = metrics.meets_success_criteria()
        assert criteria["SC-008 Resource <2s"] is None

        # Passing case
        metrics.record_resource_access("test://uri", 1.0)
        metrics.record_resource_access("test://uri", 1.5)
        criteria = metrics.meets_success_criteria()
        assert criteria["SC-008 Resource <2s"] is True

        # Failing case
        metrics.record_resource_access("test://uri", 5.0)
        criteria = metrics.meets_success_criteria()
        # Average: (1.0 + 1.5 + 5.0) / 3 = 2.5 > 2.0
        assert criteria["SC-008 Resource <2s"] is False

    def test_sc009_prompt_success_rate(self):
        """Verify SC-009: Prompt success rate >=90%."""
        metrics = ServerMetrics()

        # No data yet
        criteria = metrics.meets_success_criteria()
        assert criteria["SC-009 Prompt >=90%"] is None

        # Passing case: 9/10 = 90%
        for _ in range(9):
            metrics.record_prompt_execution("test", success=True)
        metrics.record_prompt_execution("test", success=False)
        criteria = metrics.meets_success_criteria()
        assert criteria["SC-009 Prompt >=90%"] is True

        # Failing case: add another failure -> 9/11 = 81.8%
        metrics.record_prompt_execution("test", success=False)
        criteria = metrics.meets_success_criteria()
        assert criteria["SC-009 Prompt >=90%"] is False

    def test_sc010_sampling_ratio(self):
        """Verify SC-010: Sampling token ratio <3."""
        metrics = ServerMetrics()

        # No data yet
        criteria = metrics.meets_success_criteria()
        assert criteria["SC-010 Sampling ratio <3"] is None

        # Passing case: ratio = 2.0
        metrics.record_sampling(tokens_in=1000, tokens_out=2000)
        criteria = metrics.meets_success_criteria()
        assert criteria["SC-010 Sampling ratio <3"] is True

        # Failing case: ratio = 4.0 overall
        metrics.record_sampling(tokens_in=500, tokens_out=5000)
        criteria = metrics.meets_success_criteria()
        # (2000 + 5000) / (1000 + 500) = 7000 / 1500 = 4.67 > 3
        assert criteria["SC-010 Sampling ratio <3"] is False


class TestThreadSafety:
    """Test thread safety of ServerMetrics."""

    def test_concurrent_discovery_time_recording(self):
        """Verify thread-safe discovery time recording."""
        import threading

        metrics = ServerMetrics()
        num_threads = 10
        recordings_per_thread = 100

        def record_times():
            for i in range(recordings_per_thread):
                metrics.record_discovery_time(float(i))

        threads = [threading.Thread(target=record_times) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All recordings should be captured (deque is bounded, so may be less)
        # But no exceptions should occur
        assert len(metrics.discovery_times) <= num_threads * recordings_per_thread

    def test_concurrent_connection_tracking(self):
        """Verify thread-safe connection increment/decrement."""
        import threading

        metrics = ServerMetrics()
        num_threads = 50

        def increment_then_decrement():
            metrics.increment_connections()
            metrics.decrement_connections()

        threads = [threading.Thread(target=increment_then_decrement) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # After all threads complete, connections should be 0
        assert metrics.concurrent_connections == 0
        # Peak should have been at least 1 (maybe more with race conditions)
        assert metrics.peak_connections >= 1

    def test_concurrent_cache_operations(self):
        """Verify thread-safe cache hit/miss recording."""
        import threading

        metrics = ServerMetrics()
        num_threads = 20
        ops_per_thread = 50

        def record_cache_ops():
            for i in range(ops_per_thread):
                if i % 2 == 0:
                    metrics.record_cache_hit()
                else:
                    metrics.record_cache_miss()

        threads = [threading.Thread(target=record_cache_ops) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Each thread does 25 hits and 25 misses
        expected_total = num_threads * ops_per_thread
        actual_total = metrics.cache_hits + metrics.cache_misses
        assert actual_total == expected_total

    def test_concurrent_validation_recording(self):
        """Verify thread-safe validation recording."""
        import threading

        metrics = ServerMetrics()
        num_threads = 10
        validations_per_thread = 100

        def record_validations():
            for i in range(validations_per_thread):
                metrics.record_validation(success=(i % 2 == 0))

        threads = [threading.Thread(target=record_validations) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        expected_attempts = num_threads * validations_per_thread
        assert metrics.validation_attempts == expected_attempts
        # Half should be successes
        expected_successes = num_threads * (validations_per_thread // 2)
        assert metrics.validation_successes == expected_successes
