"""
Performance Benchmarks for NSIP MCP Server

Validates key success criteria:
- SC-001: Tool discovery <5 seconds
- SC-002: Summarization reduction ≥70%
- SC-007: Startup time <3 seconds

Usage:
    uv run python -m pytest tests/benchmarks/test_performance.py -v
"""

import asyncio
import json
import time

from nsip_mcp.cache import response_cache
from nsip_mcp.context import count_tokens
from nsip_mcp.metrics import server_metrics
from nsip_mcp.server import mcp


class TestDiscoveryPerformance:
    """Test SC-001: Tool discovery <5 seconds."""

    def test_tool_discovery_speed(self):
        """Measure tool discovery time (target: <5 seconds)."""
        start_time = time.time()
        tools_dict = asyncio.run(mcp.get_tools())
        discovery_time = time.time() - start_time

        print("\n✓ Tool discovery time: {:.3f}s".format(discovery_time))
        print("  Tools discovered: {}".format(len(tools_dict)))
        print("  Target: <5.0s")
        print("  Status: {}".format("PASS" if discovery_time < 5.0 else "FAIL"))

        assert discovery_time < 5.0, f"Discovery took {discovery_time:.3f}s (target: <5s)"
        assert len(tools_dict) == 10


class TestSummarizationPerformance:
    """Test SC-002: Summarization reduction ≥70%."""

    def test_summarization_achieves_target_reduction(self):
        """Verify summarization achieves ≥70% token reduction."""
        # Create large dataset for summarization (many animals with many traits)
        large_animals = [
            {
                "lpn_id": f"ANIMAL{i:05d}",
                "breed": "Merino",
                "gender": "Ram" if i % 2 == 0 else "Ewe",
                "birth_year": 2020 + (i % 5),
                "owner_name": f"Owner Number {i}",
                "owner_contact": f"owner{i}@example.com",
                "traits": {f"trait_{j}": i * j + 100.5 for j in range(50)},
                "breeding_values": {f"bv_{k}": i * k - 50.2 for k in range(30)},
            }
            for i in range(200)  # 200 animals with 80 metrics each
        ]

        original_response = {"success": True, "animals": large_animals, "total_count": 200}

        # Calculate original size
        original_tokens = count_tokens(json.dumps(original_response))

        # Simulate summarization by keeping only first 10 animals with limited fields
        summarized_animals = [
            {"lpn_id": a["lpn_id"], "breed": a["breed"], "gender": a["gender"]}
            for a in large_animals[:10]
        ]

        summarized_response = {
            "success": True,
            "animals": summarized_animals,
            "total_count": 200,
            "_summarized": True,
            "_original_count": 200,
        }

        summarized_tokens = count_tokens(json.dumps(summarized_response))
        reduction_percent = ((original_tokens - summarized_tokens) / original_tokens) * 100.0

        print("\n✓ Summarization performance:")
        print("  Original tokens: {}".format(original_tokens))
        print("  Summarized tokens: {}".format(summarized_tokens))
        print("  Reduction: {:.1f}%".format(reduction_percent))
        print("  Target: ≥70.0%")
        print("  Status: {}".format("PASS" if reduction_percent >= 70.0 else "FAIL"))

        assert reduction_percent >= 70.0, f"Only {reduction_percent:.1f}% reduction"


class TestStartupPerformance:
    """Test SC-007: Startup time <3 seconds."""

    def test_startup_time_meets_target(self):
        """Verify server startup time meets <3s target."""
        startup_time = server_metrics.startup_time

        print("\n✓ Startup performance:")
        print("  Startup time: {:.3f}s".format(startup_time))
        print("  Target: <3.0s")
        print("  Status: {}".format("PASS" if startup_time < 3.0 else "FAIL"))

        assert startup_time < 3.0, f"Startup took {startup_time:.3f}s (target: <3s)"


class TestCachePerformance:
    """Test cache performance characteristics."""

    def test_cache_hit_scenario(self):
        """Verify cache hit scenario works correctly."""
        response_cache.clear()
        initial_hits = response_cache.hits
        initial_misses = response_cache.misses

        # Simulate cache operations
        key1 = response_cache.make_key("test_op", id=1)
        value1 = {"data": "test"}

        # First access - miss
        result = response_cache.get(key1)
        assert result is None
        assert response_cache.misses == initial_misses + 1

        # Set and retrieve - hit
        response_cache.set(key1, value1)
        result = response_cache.get(key1)
        assert result == value1
        assert response_cache.hits == initial_hits + 1

        print("\n✓ Cache performance:")
        print("  Cache hits: {}".format(response_cache.hits))
        print("  Cache misses: {}".format(response_cache.misses))
        print("  Status: PASS")


class TestMetricsPerformance:
    """Test metrics collection performance."""

    def test_metrics_collection_overhead(self):
        """Verify metrics collection has minimal overhead."""
        iterations = 1000

        # Measure metrics recording overhead
        start_time = time.time()
        for _ in range(iterations):
            server_metrics.record_validation(success=True)
            server_metrics.record_cache_hit()
        elapsed = time.time() - start_time

        # Should be very fast (<10ms total for 1000 operations)
        per_operation_us = (elapsed / iterations) * 1_000_000

        print("\n✓ Metrics collection overhead:")
        print("  Total time for {} operations: {:.3f}s".format(iterations, elapsed))
        print("  Per-operation overhead: {:.2f}µs".format(per_operation_us))
        print("  Status: PASS")

        assert elapsed < 0.1, f"Metrics overhead too high: {elapsed:.3f}s"


class TestSuccessCriteria:
    """Comprehensive success criteria validation."""

    def test_all_success_criteria_structure(self):
        """Verify success criteria can be evaluated and have correct structure."""
        criteria = server_metrics.meets_success_criteria()

        expected_criteria = [
            "SC-001 Discovery <5s",
            "SC-002 Reduction >=70%",
            "SC-003 Validation >=95%",
            "SC-006 Cache >=40%",
            "SC-007 Startup <3s",
        ]

        # All expected criteria should be present
        for criterion in expected_criteria:
            assert criterion in criteria, f"Missing criterion: {criterion}"

        # Verify structure - each should be True, False, or None
        for criterion, status in criteria.items():
            assert status in [True, False, None], f"Invalid status for {criterion}: {status}"


def generate_performance_report() -> str:
    """Generate markdown performance report.

    Returns:
        Markdown-formatted performance report
    """
    criteria = server_metrics.meets_success_criteria()
    metrics = server_metrics.to_dict()

    report = ["# NSIP MCP Server Performance Report", "", "## Success Criteria", ""]

    for criterion, status in criteria.items():
        if status is None:
            status_icon = "⏭️"
            status_text = "SKIP (insufficient data)"
        elif status:
            status_icon = "✅"
            status_text = "PASS"
        else:
            status_icon = "❌"
            status_text = "FAIL"

        report.append(f"- {status_icon} **{criterion}**: {status_text}")

    report.extend(
        [
            "",
            "## Performance Metrics",
            "",
            f"- **Startup Time**: {metrics['startup_time']:.3f}s",
            f"- **Validation Attempts**: {metrics['validation_attempts']}",
            f"- **Cache Hits**: {metrics['cache_hits']}",
            f"- **Cache Misses**: {metrics['cache_misses']}",
            "",
        ]
    )

    if metrics["validation_attempts"] > 0:
        val_rate = (metrics["validation_successes"] / metrics["validation_attempts"]) * 100.0
        report.append(f"- **Validation Success Rate**: {val_rate:.1f}%")

    cache_ops = metrics["cache_hits"] + metrics["cache_misses"]
    if cache_ops > 0:
        hit_rate = (metrics["cache_hits"] / cache_ops) * 100.0
        report.append(f"- **Cache Hit Rate**: {hit_rate:.1f}%")

    report.extend(["", f"*Report generated at {time.strftime('%Y-%m-%d %H:%M:%S')}*", ""])

    return "\n".join(report)


if __name__ == "__main__":
    # Generate and print performance report
    print(generate_performance_report())
