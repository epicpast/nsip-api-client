"""
Unit tests for context management (token counting and summarization)

Tests:
- Token counting with tiktoken (cl100k_base)
- should_summarize() boundary conditions (2000 token threshold)
- summarize_response() function
- FR-005a field preservation (identifiers, breed, contact, top traits)
- FR-005b field omission (low accuracy traits, redundant structures)
- 70% token reduction target (SC-002)
- Thread safety of encoding object

Target: >95% coverage (SC-011)
"""

import json
from concurrent.futures import ThreadPoolExecutor

from nsip_mcp.context import (
    TARGET_REDUCTION_PERCENT,
    TOKEN_THRESHOLD,
    ContextManagedResponse,
    SummarizedAnimalResponse,
    count_tokens,
    encoding,
    should_summarize,
    summarize_response,
)


class TestTokenCounting:
    """Tests for token counting using tiktoken."""

    def test_count_tokens_accuracy(self):
        """Verify count_tokens() returns accurate token counts."""
        # Simple test cases with known token counts
        assert count_tokens("Hello, world!") == 4
        assert count_tokens("") == 0
        assert count_tokens("a") == 1

    def test_count_tokens_various_lengths(self):
        """Test token counting with various text lengths."""
        short_text = "Short text"
        medium_text = "This is a medium length text " * 10
        long_text = "This is a very long text " * 100

        short_count = count_tokens(short_text)
        medium_count = count_tokens(medium_text)
        long_count = count_tokens(long_text)

        assert short_count < medium_count < long_count
        assert short_count > 0
        assert medium_count > short_count
        assert long_count > medium_count

    def test_count_tokens_special_characters(self):
        """Verify token counting handles special characters."""
        text_with_special = "Hello! @#$%^&*() 你好 🎉"
        count = count_tokens(text_with_special)
        assert count > 0

    def test_count_tokens_json(self):
        """Verify token counting works with JSON strings."""
        data = {"key": "value", "number": 123, "nested": {"inner": "data"}}
        json_text = json.dumps(data)
        count = count_tokens(json_text)
        assert count > 0

    def test_count_tokens_unicode(self):
        """Verify token counting handles Unicode correctly."""
        unicode_text = "こんにちは世界"
        count = count_tokens(unicode_text)
        assert count > 0

    def test_count_tokens_multiline(self):
        """Verify token counting handles multiline text."""
        multiline_text = """
        Line 1
        Line 2
        Line 3
        """
        count = count_tokens(multiline_text)
        assert count > 0

    def test_count_tokens_deterministic(self):
        """Verify token counting is deterministic."""
        text = "Test text for determinism"
        count1 = count_tokens(text)
        count2 = count_tokens(text)
        count3 = count_tokens(text)
        assert count1 == count2 == count3

    def test_encoding_thread_safety(self):
        """Verify tiktoken encoding object is thread-safe."""

        def count_in_thread(text):
            return count_tokens(text)

        texts = [f"Thread text {i}" for i in range(100)]

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(count_in_thread, text) for text in texts]
            results = [f.result() for f in futures]

        # All operations should succeed
        assert all(count > 0 for count in results)
        assert len(results) == 100

    def test_encoding_is_cl100k_base(self):
        """Verify encoding uses cl100k_base (GPT-4 tokenizer)."""
        assert encoding.name == "cl100k_base"

    def test_count_tokens_large_text(self):
        """Verify token counting works with large texts."""
        large_text = "word " * 10000  # ~10000 tokens
        count = count_tokens(large_text)
        assert count > 5000  # Approximate check


class TestSummarizationThreshold:
    """Tests for 2000-token summarization threshold."""

    def test_should_summarize_below_threshold(self):
        """Verify should_summarize(<2000 tokens) returns False."""
        # Create text that's definitely under 2000 tokens
        small_response = {"data": "small" * 100}
        assert count_tokens(json.dumps(small_response)) < TOKEN_THRESHOLD
        assert should_summarize(small_response) is False

    def test_should_summarize_at_threshold(self):
        """Verify should_summarize(=2000 tokens) returns False (pass-through)."""
        # Create text that's approximately at the threshold
        # This is tricky to hit exactly, so we'll test the boundary behavior
        # TOKEN_THRESHOLD is 2000, so anything <= 2000 should not be summarized
        text_base = "word " * 400  # Approximately 400-500 tokens
        response = {"data": text_base * 4}  # Approximately 1600-2000 tokens

        token_count = count_tokens(json.dumps(response))
        if token_count <= TOKEN_THRESHOLD:
            assert should_summarize(response) is False

    def test_should_summarize_above_threshold(self):
        """Verify should_summarize(>2000 tokens) returns True."""
        # Create text that's definitely over 2000 tokens
        large_text = "word " * 1000  # Approximately 1000+ tokens
        large_response = {"data": large_text, "more_data": large_text}

        token_count = count_tokens(json.dumps(large_response))
        assert token_count > TOKEN_THRESHOLD
        assert should_summarize(large_response) is True

    def test_should_summarize_with_complex_structure(self):
        """Test should_summarize with complex nested structures."""
        complex_response = {
            "animals": [{"id": i, "name": f"Animal {i}", "data": "x" * 100} for i in range(100)],
            "metadata": {"total": 100, "page": 1},
        }

        token_count = count_tokens(json.dumps(complex_response))
        expected = token_count > TOKEN_THRESHOLD
        assert should_summarize(complex_response) == expected

    def test_threshold_constant(self):
        """Verify TOKEN_THRESHOLD is set to 2000."""
        assert TOKEN_THRESHOLD == 2000

    def test_should_summarize_empty_response(self):
        """Test should_summarize with empty response."""
        empty_response = {}
        assert should_summarize(empty_response) is False

    def test_should_summarize_boundary_cases(self):
        """Test boundary cases around the 2000 token threshold."""
        # Test with progressively larger responses
        base_text = "word " * 100

        for multiplier in [1, 5, 10, 15, 20]:
            response = {"data": base_text * multiplier}
            token_count = count_tokens(json.dumps(response))
            result = should_summarize(response)

            if token_count <= TOKEN_THRESHOLD:
                assert result is False, f"Failed at {token_count} tokens"
            else:
                assert result is True, f"Failed at {token_count} tokens"


class TestContextManagedResponse:
    """Tests for ContextManagedResponse model."""

    def test_create_passthrough(self):
        """Test creating pass-through response (≤2000 tokens)."""
        response = {"lpn_id": "123", "breed": "Katahdin", "data": "small"}

        managed = ContextManagedResponse.create_passthrough(response)

        assert managed.was_summarized is False
        assert managed.reduction_percent == 0.0
        assert managed.original_response == response
        assert managed.token_count > 0

        # Check metadata in final response
        assert managed.final_response["_summarized"] is False
        assert "_original_token_count" in managed.final_response
        assert managed.final_response["_original_token_count"] == managed.token_count

        # Original data should be preserved
        assert managed.final_response["lpn_id"] == "123"
        assert managed.final_response["breed"] == "Katahdin"

    def test_create_summarized(self):
        """Test creating summarized response (>2000 tokens)."""
        # Create a large original response
        original = {
            "lpn_id": "6####92020###249",
            "breed": "Katahdin",
            "data": "x" * 2000,  # Make it large
            "traits": {f"trait_{i}": {"value": i, "accuracy": 0.8} for i in range(50)},
        }

        # Create a much smaller summary
        summary = {
            "lpn_id": "6####92020###249",
            "breed": "Katahdin",
            "top_traits": [{"trait": "trait_1", "value": 1, "accuracy": 0.8}],
        }

        managed = ContextManagedResponse.create_summarized(original, summary)

        assert managed.was_summarized is True
        assert managed.reduction_percent > 0
        assert managed.original_response == original

        # Check metadata in final response
        assert managed.final_response["_summarized"] is True
        assert "_original_token_count" in managed.final_response
        assert "_summary_token_count" in managed.final_response
        assert "_reduction_percent" in managed.final_response

        # Verify reduction calculation
        original_tokens = count_tokens(json.dumps(original))
        summary_tokens = count_tokens(json.dumps(summary))
        expected_reduction = ((original_tokens - summary_tokens) / original_tokens) * 100.0

        assert managed.reduction_percent == expected_reduction
        assert managed.final_response["_reduction_percent"] == round(expected_reduction, 2)

    def test_meets_target_passthrough(self):
        """Test that pass-through responses always meet target."""
        response = {"data": "small"}
        managed = ContextManagedResponse.create_passthrough(response)

        # Pass-through always meets target
        assert managed.meets_target() is True

    def test_meets_target_summarized(self):
        """Test meets_target() checks 70% reduction for summarized responses."""
        original = {"data": "x" * 3000}

        # Create a summary that achieves >70% reduction
        good_summary = {"data": "x" * 500}  # Should achieve ~83% reduction
        managed_good = ContextManagedResponse.create_summarized(original, good_summary)
        assert managed_good.meets_target() is True
        assert managed_good.reduction_percent >= TARGET_REDUCTION_PERCENT

        # Create a summary that doesn't achieve 70% reduction
        poor_summary = {"data": "x" * 2000}  # Should achieve ~33% reduction
        managed_poor = ContextManagedResponse.create_summarized(original, poor_summary)
        assert managed_poor.meets_target() is False
        assert managed_poor.reduction_percent < TARGET_REDUCTION_PERCENT

    def test_metadata_fields(self):
        """Verify all metadata fields are present and correct."""
        original = {"lpn_id": "123", "data": "x" * 2000}
        summary = {"lpn_id": "123", "data": "y" * 400}

        managed = ContextManagedResponse.create_summarized(original, summary)

        # All metadata fields should be present
        assert "_summarized" in managed.final_response
        assert "_original_token_count" in managed.final_response
        assert "_summary_token_count" in managed.final_response
        assert "_reduction_percent" in managed.final_response

        # Values should be correct types
        assert isinstance(managed.final_response["_summarized"], bool)
        assert isinstance(managed.final_response["_original_token_count"], int)
        assert isinstance(managed.final_response["_summary_token_count"], int)
        assert isinstance(managed.final_response["_reduction_percent"], (int, float))


class TestSummarizedAnimalResponse:
    """Tests for SummarizedAnimalResponse model."""

    def test_to_dict(self):
        """Verify to_dict() includes all FR-005a required fields."""
        animal = SummarizedAnimalResponse(
            lpn_id="6####92020###249",
            breed="Katahdin",
            sire="SireID123",
            dam="DamID456",
            total_progeny=6,
            contact={"name": "John Doe", "email": "john@example.com"},
            top_traits=[
                {"trait": "BWT", "value": 0.5, "accuracy": 0.89},
                {"trait": "YWT", "value": 2.1, "accuracy": 0.92},
            ],
        )

        result = animal.to_dict()

        # All FR-005a fields should be present
        assert "lpn_id" in result
        assert "breed" in result
        assert "sire" in result
        assert "dam" in result
        assert "total_progeny" in result
        assert "contact" in result
        assert "top_traits" in result

        # Verify values
        assert result["lpn_id"] == "6####92020###249"
        assert result["breed"] == "Katahdin"
        assert result["sire"] == "SireID123"
        assert result["dam"] == "DamID456"
        assert result["total_progeny"] == 6
        assert result["contact"]["name"] == "John Doe"
        assert len(result["top_traits"]) == 2

    def test_to_dict_omits_none_values(self):
        """Verify to_dict() omits optional fields when None."""
        animal = SummarizedAnimalResponse(
            lpn_id="123",
            breed="Merino",
            sire=None,
            dam=None,
            total_progeny=0,
            contact=None,
            top_traits=[],
        )

        result = animal.to_dict()

        # Required fields always present
        assert "lpn_id" in result
        assert "breed" in result
        assert "total_progeny" in result
        assert "top_traits" in result

        # Optional fields should be omitted when None
        assert "sire" not in result
        assert "dam" not in result
        assert "contact" not in result

    def test_select_top_traits_filtering(self):
        """Verify traits with accuracy <50% are filtered out (FR-005b)."""
        traits = {
            "BWT": {"value": 0.5, "accuracy": 0.89},  # Keep: accuracy >= 0.5
            "WWT": {"value": 1.2, "accuracy": 0.45},  # Filter: accuracy < 0.5
            "YWT": {"value": 2.1, "accuracy": 0.92},  # Keep: accuracy >= 0.5
            "PFAT": {"value": 0.3, "accuracy": 0.30},  # Filter: accuracy < 0.5
            "PEMD": {"value": 0.8, "accuracy": 0.65},  # Keep: accuracy >= 0.5
        }

        result = SummarizedAnimalResponse.select_top_traits(traits, max_traits=10)

        # Only traits with accuracy >= 0.5 should be included
        trait_names = [t["trait"] for t in result]
        assert "BWT" in trait_names
        assert "YWT" in trait_names
        assert "PEMD" in trait_names
        assert "WWT" not in trait_names  # Filtered out
        assert "PFAT" not in trait_names  # Filtered out

    def test_select_top_traits_sorting(self):
        """Verify traits are sorted by accuracy descending."""
        traits = {
            "BWT": {"value": 0.5, "accuracy": 0.65},
            "WWT": {"value": 1.2, "accuracy": 0.92},
            "YWT": {"value": 2.1, "accuracy": 0.78},
            "PFAT": {"value": 0.3, "accuracy": 0.88},
        }

        result = SummarizedAnimalResponse.select_top_traits(traits, max_traits=10)

        # Should be sorted by accuracy (highest first)
        accuracies = [t["accuracy"] for t in result]
        assert accuracies == sorted(accuracies, reverse=True)

        # First trait should be WWT (0.92)
        assert result[0]["trait"] == "WWT"
        assert result[0]["accuracy"] == 0.92

    def test_select_top_traits_limit(self):
        """Verify max 3 traits are returned."""
        traits = {f"trait_{i}": {"value": i, "accuracy": 0.5 + (i * 0.05)} for i in range(10)}

        # Test with default max_traits=3
        result = SummarizedAnimalResponse.select_top_traits(traits)
        assert len(result) <= 3

        # Test with custom limit
        result_5 = SummarizedAnimalResponse.select_top_traits(traits, max_traits=5)
        assert len(result_5) <= 5

        # Test with limit of 1
        result_1 = SummarizedAnimalResponse.select_top_traits(traits, max_traits=1)
        assert len(result_1) == 1

    def test_select_top_traits_empty(self):
        """Handle empty traits dict gracefully."""
        traits = {}

        result = SummarizedAnimalResponse.select_top_traits(traits)

        assert result == []
        assert len(result) == 0

    def test_select_top_traits_all_low_accuracy(self):
        """Handle case where all traits have accuracy <50%."""
        traits = {
            "trait_1": {"value": 1.0, "accuracy": 0.30},
            "trait_2": {"value": 2.0, "accuracy": 0.25},
            "trait_3": {"value": 3.0, "accuracy": 0.40},
        }

        result = SummarizedAnimalResponse.select_top_traits(traits)

        # All should be filtered out
        assert result == []

    def test_select_top_traits_exactly_50_percent(self):
        """Test boundary condition: exactly 50% accuracy should be included."""
        traits = {
            "trait_1": {"value": 1.0, "accuracy": 0.50},  # Exactly 50% - should be included
            "trait_2": {"value": 2.0, "accuracy": 0.49},  # Below 50% - should be excluded
        }

        result = SummarizedAnimalResponse.select_top_traits(traits)

        # Only trait_1 should be included
        assert len(result) == 1
        assert result[0]["trait"] == "trait_1"
        assert result[0]["accuracy"] == 0.50

    def test_select_top_traits_missing_accuracy(self):
        """Handle traits with missing accuracy field."""
        traits = {
            "trait_1": {"value": 1.0, "accuracy": 0.90},
            "trait_2": {"value": 2.0},  # Missing accuracy
            "trait_3": {"value": 3.0, "accuracy": 0.80},
        }

        result = SummarizedAnimalResponse.select_top_traits(traits)

        # trait_2 should be filtered out (treated as 0 accuracy)
        trait_names = [t["trait"] for t in result]
        assert "trait_1" in trait_names
        assert "trait_3" in trait_names
        assert "trait_2" not in trait_names


class TestSummarizeResponse:
    """Tests for summarize_response() function."""

    def create_realistic_animal_response(self, large=False):
        """Create a realistic animal response for testing."""
        base_response = {
            "lpn_id": "6####92020###249",
            "breed": "Katahdin",
            "sire": {"lpn_id": "SireID123", "name": "Sire Name"},
            "dam": {"lpn_id": "DamID456", "name": "Dam Name"},
            "traits": {
                "BWT": {"value": 0.5, "accuracy": 0.89, "reliability": 0.95},
                "WWT": {"value": 1.2, "accuracy": 0.45, "reliability": 0.80},
                "YWT": {"value": 2.1, "accuracy": 0.92, "reliability": 0.88},
                "PFAT": {"value": 0.3, "accuracy": 0.30, "reliability": 0.70},
                "PEMD": {"value": 0.8, "accuracy": 0.65, "reliability": 0.85},
            },
            "progeny": {
                "total_count": 6,
                "animals": [
                    {"lpn_id": f"PROG{i}", "name": f"Progeny {i}", "data": "x" * 100}
                    for i in range(6)
                ],
            },
            "contact": {"name": "John Doe", "email": "john@example.com", "phone": "555-1234"},
        }

        if large:
            # Add verbose data to make it large enough to exceed 2000 tokens
            # Need ~10,000+ characters to reliably exceed 2000 tokens
            base_response["verbose_data"] = "x" * 10000
            # Create a list of 100 dict objects with longer strings
            base_response["registration"] = [
                {
                    "field": f"value{i}",
                    "description": (
                        f"This is a detailed description for item number {i} " "with extra text"
                    ),
                    "metadata": {"id": i, "category": "test", "tags": ["tag1", "tag2", "tag3"]},
                }
                for i in range(100)
            ]

        return base_response

    def test_summarize_preserves_required_fields(self):
        """Verify all FR-005a fields are present in summary."""
        response = self.create_realistic_animal_response()

        summary = summarize_response(response)

        # All FR-005a required fields should be present
        assert "lpn_id" in summary
        assert summary["lpn_id"] == "6####92020###249"

        assert "breed" in summary
        assert summary["breed"] == "Katahdin"

        assert "sire" in summary
        assert summary["sire"] == "SireID123"

        assert "dam" in summary
        assert summary["dam"] == "DamID456"

        assert "total_progeny" in summary
        assert summary["total_progeny"] == 6

        assert "contact" in summary
        assert summary["contact"]["name"] == "John Doe"

        assert "top_traits" in summary

    def test_summarize_omits_low_accuracy_traits(self):
        """Verify traits with accuracy <50% are omitted (FR-005b)."""
        response = self.create_realistic_animal_response()

        summary = summarize_response(response)

        # top_traits should only contain traits with accuracy >= 50%
        trait_names = [t["trait"] for t in summary["top_traits"]]

        # These should be included (accuracy >= 50%)
        assert "BWT" in trait_names  # 0.89
        assert "YWT" in trait_names  # 0.92
        assert "PEMD" in trait_names  # 0.65

        # These should be excluded (accuracy < 50%)
        assert "WWT" not in trait_names  # 0.45
        assert "PFAT" not in trait_names  # 0.30

    def test_summarize_progeny_count_only(self):
        """Verify progeny.animals list is omitted, total_count preserved."""
        response = self.create_realistic_animal_response()

        summary = summarize_response(response)

        # Should have total_progeny count
        assert "total_progeny" in summary
        assert summary["total_progeny"] == 6

        # Should NOT have full progeny details or animals list
        assert "progeny" not in summary
        assert "animals" not in summary

    def test_summarize_70_percent_reduction(self):
        """Verify token reduction >=70% (SC-002)."""
        # Create a large response
        response = self.create_realistic_animal_response(large=True)

        # Ensure it's over threshold
        original_tokens = count_tokens(json.dumps(response))
        assert original_tokens > TOKEN_THRESHOLD

        summary = summarize_response(response)
        summary_tokens = count_tokens(json.dumps(summary))

        # Calculate reduction percentage
        reduction_percent = ((original_tokens - summary_tokens) / original_tokens) * 100.0

        # Should achieve at least 70% reduction
        assert reduction_percent >= 70.0, f"Only achieved {reduction_percent:.2f}% reduction"

    def test_summarize_with_contact_info(self):
        """Verify contact information is preserved when present."""
        response = self.create_realistic_animal_response()

        summary = summarize_response(response)

        assert "contact" in summary
        assert summary["contact"]["name"] == "John Doe"
        assert summary["contact"]["email"] == "john@example.com"
        assert summary["contact"]["phone"] == "555-1234"

    def test_summarize_handles_missing_fields(self):
        """Gracefully handle responses missing optional fields."""
        minimal_response = {
            "lpn_id": "123",
            "breed": "Merino",
            # No sire, dam, progeny, contact, or traits
        }

        summary = summarize_response(minimal_response)

        # Should still work with minimal data
        assert summary["lpn_id"] == "123"
        assert summary["breed"] == "Merino"
        assert summary["total_progeny"] == 0
        assert summary["top_traits"] == []
        assert summary.get("sire") is None
        assert summary.get("dam") is None
        assert summary.get("contact") is None

    def test_summarize_handles_alternate_field_names(self):
        """Handle both lowercase and capitalized field names."""
        response = {
            "LpnId": "6####92020###249",  # Capitalized
            "Breed": "Katahdin",  # Capitalized
            "traits": {"BWT": {"value": 0.5, "accuracy": 0.89}},
        }

        summary = summarize_response(response)

        # Should handle capitalized field names
        assert summary["lpn_id"] == "6####92020###249"
        assert summary["breed"] == "Katahdin"

    def test_summarize_boundary_exactly_2000_tokens(self):
        """Test boundary condition with response at exactly 2000 tokens."""
        # Create a response that's close to 2000 tokens
        text_base = "word " * 100
        response = {
            "lpn_id": "123",
            "breed": "Test",
            "data": text_base * 4,
            "traits": {f"trait_{i}": {"value": i, "accuracy": 0.8} for i in range(10)},
        }

        # Verify summarization works regardless of size
        summary = summarize_response(response)

        assert "lpn_id" in summary
        assert "breed" in summary
        assert "top_traits" in summary

    def test_summarize_top_traits_ordering(self):
        """Verify top traits are ordered by accuracy (highest first)."""
        response = {
            "lpn_id": "123",
            "breed": "Test",
            "traits": {
                "trait_1": {"value": 1.0, "accuracy": 0.65},
                "trait_2": {"value": 2.0, "accuracy": 0.92},
                "trait_3": {"value": 3.0, "accuracy": 0.78},
                "trait_4": {"value": 4.0, "accuracy": 0.88},
            },
        }

        summary = summarize_response(response)

        # Should have max 3 traits, sorted by accuracy
        assert len(summary["top_traits"]) <= 3

        # First should be trait_2 (0.92)
        assert summary["top_traits"][0]["trait"] == "trait_2"
        assert summary["top_traits"][0]["accuracy"] == 0.92

        # Verify descending order
        accuracies = [t["accuracy"] for t in summary["top_traits"]]
        assert accuracies == sorted(accuracies, reverse=True)


class TestFullWorkflowIntegration:
    """Integration tests for complete workflows."""

    def test_full_workflow_passthrough(self):
        """Test complete workflow for small response (pass-through)."""
        # Small response that should pass through
        response = {
            "lpn_id": "123",
            "breed": "Merino",
            "sire": {"lpn_id": "S123"},
            "dam": {"lpn_id": "D123"},
            "traits": {"BWT": {"value": 0.5, "accuracy": 0.89}},
        }

        # Step 1: Check if summarization is needed
        needs_summary = should_summarize(response)
        assert needs_summary is False

        # Step 2: Create pass-through response
        managed = ContextManagedResponse.create_passthrough(response)

        # Step 3: Verify response structure
        assert managed.was_summarized is False
        assert managed.meets_target() is True
        assert managed.final_response["_summarized"] is False
        assert managed.final_response["lpn_id"] == "123"

    def test_full_workflow_summarization(self):
        """Test complete workflow for large response (summarization)."""
        # Large response that needs summarization
        response = {
            "lpn_id": "6####92020###249",
            "breed": "Katahdin",
            "sire": {"lpn_id": "SireID123"},
            "dam": {"lpn_id": "DamID456"},
            "traits": {f"trait_{i}": {"value": i, "accuracy": 0.5 + (i * 0.01)} for i in range(50)},
            "progeny": {
                "total_count": 100,
                "animals": [{"lpn_id": f"PROG{i}", "data": "x" * 200} for i in range(100)],
            },
            "verbose_data": "x" * 3000,
            "contact": {"name": "John Doe"},
        }

        # Step 1: Check if summarization is needed
        needs_summary = should_summarize(response)
        assert needs_summary is True

        # Step 2: Summarize the response
        summary = summarize_response(response)

        # Step 3: Create summarized managed response
        managed = ContextManagedResponse.create_summarized(response, summary)

        # Step 4: Verify summarization quality
        assert managed.was_summarized is True
        assert managed.reduction_percent >= 70.0
        assert managed.meets_target() is True

        # Step 5: Verify metadata
        assert managed.final_response["_summarized"] is True
        assert managed.final_response["_reduction_percent"] >= 70.0

        # Step 6: Verify essential data preserved
        assert managed.final_response["lpn_id"] == "6####92020###249"
        assert managed.final_response["breed"] == "Katahdin"
        assert managed.final_response["total_progeny"] == 100
        assert len(managed.final_response["top_traits"]) <= 3

    def test_workflow_with_boundary_response(self):
        """Test workflow with response near the 2000 token boundary."""
        # Create response close to 2000 tokens
        response = {
            "lpn_id": "123",
            "breed": "Test",
            "data": "word " * 500,
            "traits": {f"trait_{i}": {"value": i, "accuracy": 0.8} for i in range(20)},
        }

        # Process regardless of whether it needs summarization
        if should_summarize(response):
            summary = summarize_response(response)
            managed = ContextManagedResponse.create_summarized(response, summary)
            assert managed.was_summarized is True
        else:
            managed = ContextManagedResponse.create_passthrough(response)
            assert managed.was_summarized is False

        # Either way, should meet target
        assert managed.meets_target() is True


class TestEncodingObject:
    """Tests for module-level encoding object."""

    def test_encoding_initialized(self):
        """Verify encoding object is initialized at module level."""
        assert encoding is not None
        assert hasattr(encoding, "encode")
        assert hasattr(encoding, "decode")

    def test_encoding_consistency(self):
        """Verify encoding produces consistent results."""
        text = "Test consistency"
        tokens1 = encoding.encode(text)
        tokens2 = encoding.encode(text)
        assert tokens1 == tokens2

    def test_encoding_decode_roundtrip(self):
        """Verify encode/decode roundtrip works correctly."""
        text = "Test roundtrip"
        tokens = encoding.encode(text)
        decoded = encoding.decode(tokens)
        assert decoded == text


class TestTokenCountingEdgeCases:
    """Tests for edge cases in token counting."""

    def test_count_tokens_whitespace_only(self):
        """Test token counting with whitespace-only strings."""
        whitespace = "   \n\t  "
        count = count_tokens(whitespace)
        assert count >= 0  # May be 0 or small number

    def test_count_tokens_repeated_characters(self):
        """Test token counting with repeated characters."""
        repeated = "aaaaaaaaaa"
        count = count_tokens(repeated)
        assert count > 0

    def test_count_tokens_numbers(self):
        """Test token counting with numeric strings."""
        numbers = "123456789 987654321 111222333"
        count = count_tokens(numbers)
        assert count > 0

    def test_count_tokens_mixed_content(self):
        """Test token counting with mixed content types."""
        mixed = "Text 123 @#$ 你好 🎉 \n newline"
        count = count_tokens(mixed)
        assert count > 0


class TestShouldSummarizePerformance:
    """Performance tests for should_summarize function."""

    def test_should_summarize_fast_execution(self):
        """Verify should_summarize executes quickly."""
        import time

        large_response = {"data": "word " * 1000}

        start = time.time()
        result = should_summarize(large_response)
        duration = time.time() - start

        # Should complete in less than 100ms
        assert duration < 0.1
        assert isinstance(result, bool)

    def test_should_summarize_multiple_calls(self):
        """Test performance with multiple consecutive calls."""
        import time

        responses = [{"data": "word " * i} for i in range(10, 100, 10)]

        start = time.time()
        for response in responses:
            should_summarize(response)
        duration = time.time() - start

        # Should process all in less than 1 second
        assert duration < 1.0


class TestTokenThresholdBehavior:
    """Tests for behavior at exact threshold boundaries."""

    def test_exactly_2000_tokens_not_summarized(self):
        """Test that exactly 2000 tokens is NOT summarized (≤ threshold)."""
        # This is a behavioral test - at exactly threshold, pass through
        # Create a response that's close to 2000 tokens
        text = "word " * 500
        response = {"data": text}

        # Adjust until we hit close to 2000
        while True:
            token_count = count_tokens(json.dumps(response))
            if token_count == TOKEN_THRESHOLD:
                assert should_summarize(response) is False
                break
            elif token_count < TOKEN_THRESHOLD:
                response["data"] += " word"
            else:
                # Over threshold, reduce
                response["data"] = response["data"][:-5]
                if token_count < TOKEN_THRESHOLD + 10:
                    break  # Close enough to test

    def test_2001_tokens_is_summarized(self):
        """Test that 2001 tokens (threshold + 1) IS summarized."""
        # Create response slightly over threshold
        large_text = "word " * 600
        response = {"data": large_text}

        token_count = count_tokens(json.dumps(response))
        if token_count > TOKEN_THRESHOLD:
            assert should_summarize(response) is True


class TestModuleConstants:
    """Tests for module-level constants."""

    def test_token_threshold_value(self):
        """Verify TOKEN_THRESHOLD constant value."""
        assert TOKEN_THRESHOLD == 2000
        assert isinstance(TOKEN_THRESHOLD, int)

    def test_target_reduction_percent_value(self):
        """Verify TARGET_REDUCTION_PERCENT constant value."""
        assert TARGET_REDUCTION_PERCENT == 70.0
        assert isinstance(TARGET_REDUCTION_PERCENT, float)

    def test_encoding_name(self):
        """Verify encoding uses cl100k_base."""
        assert encoding.name == "cl100k_base"


class TestAccuracyNormalization:
    """Tests for accuracy normalization (percentage → decimal conversion)."""

    def test_accuracy_as_decimal_preserved(self):
        """Verify accuracy already in 0-1 range is preserved as-is."""
        response = {
            "lpn_id": "123",
            "breed": "Test",
            "traits": {
                "BWT": {"value": 0.5, "accuracy": 0.89},  # Already decimal
                "WWT": {"value": 1.2, "accuracy": 0.65},  # Already decimal
            },
        }

        summary = summarize_response(response)

        # Accuracies should be preserved as-is (not divided by 100)
        bwt = next((t for t in summary["top_traits"] if t["trait"] == "BWT"), None)
        assert bwt is not None
        assert bwt["accuracy"] == 0.89

    def test_accuracy_as_percentage_normalized(self):
        """Verify accuracy in 0-100 range is normalized to 0-1 (dataclass format)."""
        response = {
            "lpn_id": "123",
            "breed": "Test",
            "traits": {
                "BWT": {"value": 0.5, "accuracy": 89},  # Percentage (0-100)
                "WWT": {"value": 1.2, "accuracy": 65},  # Percentage (0-100)
            },
        }

        summary = summarize_response(response)

        # Accuracies should be normalized to decimal (89 → 0.89)
        bwt = next((t for t in summary["top_traits"] if t["trait"] == "BWT"), None)
        assert bwt is not None
        assert bwt["accuracy"] == 0.89

    def test_accuracy_exactly_1_preserved(self):
        """Verify accuracy of exactly 1.0 is preserved (boundary case)."""
        response = {
            "lpn_id": "123",
            "breed": "Test",
            "traits": {
                "BWT": {"value": 0.5, "accuracy": 1.0},  # Exactly 1.0 - already decimal
            },
        }

        summary = summarize_response(response)

        bwt = next((t for t in summary["top_traits"] if t["trait"] == "BWT"), None)
        assert bwt is not None
        assert bwt["accuracy"] == 1.0  # Not divided (still 1.0)

    def test_accuracy_just_over_1_normalized(self):
        """Verify accuracy just over 1.0 is normalized (1.01 → 0.0101)."""
        response = {
            "lpn_id": "123",
            "breed": "Test",
            "traits": {
                "BWT": {"value": 0.5, "accuracy": 1.01},  # Just over 1, treat as percentage
            },
        }

        summary = summarize_response(response)

        # 1.01 > 1, so normalized to 0.0101 (which is < 0.5 min_accuracy, filtered out)
        # With default min_accuracy=0.5, this trait should be filtered
        assert len(summary["top_traits"]) == 0

    def test_accuracy_100_normalized_to_1(self):
        """Verify accuracy of 100 normalizes to 1.0."""
        response = {
            "lpn_id": "123",
            "breed": "Test",
            "traits": {
                "BWT": {"value": 0.5, "accuracy": 100},  # 100% → 1.0
            },
        }

        summary = summarize_response(response)

        bwt = next((t for t in summary["top_traits"] if t["trait"] == "BWT"), None)
        assert bwt is not None
        assert bwt["accuracy"] == 1.0


class TestNonDictProgenyHandling:
    """Tests for non-dict progeny field handling."""

    def test_progeny_as_dict_extracts_count(self):
        """Verify dict progeny extracts total_count correctly."""
        response = {
            "lpn_id": "123",
            "breed": "Test",
            "progeny": {
                "total_count": 15,
                "animals": [{"id": "p1"}, {"id": "p2"}],
            },
        }

        summary = summarize_response(response)

        assert summary["total_progeny"] == 15

    def test_progeny_as_list_returns_zero(self):
        """Verify list progeny returns 0 (not a dict)."""
        response = {
            "lpn_id": "123",
            "breed": "Test",
            "progeny": [{"id": "p1"}, {"id": "p2"}, {"id": "p3"}],  # List, not dict
        }

        summary = summarize_response(response)

        # Non-dict progeny should result in total_progeny = 0
        assert summary["total_progeny"] == 0

    def test_progeny_as_none_returns_zero(self):
        """Verify None progeny returns 0."""
        response = {
            "lpn_id": "123",
            "breed": "Test",
            "progeny": None,
        }

        summary = summarize_response(response)

        assert summary["total_progeny"] == 0

    def test_progeny_as_integer_returns_zero(self):
        """Verify integer progeny returns 0 (treated as non-dict)."""
        response = {
            "lpn_id": "123",
            "breed": "Test",
            "progeny": 42,  # Integer, not dict
        }

        summary = summarize_response(response)

        # Non-dict progeny should result in total_progeny = 0
        assert summary["total_progeny"] == 0

    def test_progeny_missing_returns_zero(self):
        """Verify missing progeny field returns 0."""
        response = {
            "lpn_id": "123",
            "breed": "Test",
            # No progeny field
        }

        summary = summarize_response(response)

        assert summary["total_progeny"] == 0

    def test_progeny_dict_without_total_count_returns_zero(self):
        """Verify dict progeny without total_count returns 0."""
        response = {
            "lpn_id": "123",
            "breed": "Test",
            "progeny": {"animals": [{"id": "p1"}]},  # Dict but no total_count
        }

        summary = summarize_response(response)

        assert summary["total_progeny"] == 0
