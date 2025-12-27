"""Context management for efficient LLM token usage.

This module handles token counting, response summarization, and context window management
to prevent overwhelming LLM context limits.
"""

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional

import tiktoken

# Import metrics for tracking (avoid circular import)
if TYPE_CHECKING:
    from nsip_mcp.metrics import ServerMetrics

server_metrics: Optional["ServerMetrics"] = None  # type: ignore[assignment]
try:
    from nsip_mcp.metrics import server_metrics as _server_metrics

    server_metrics = _server_metrics
except ImportError:
    # Gracefully handle if metrics not available (e.g., during testing)
    pass


# Initialize tiktoken encoding at module level (thread-safe, reusable)
encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 tokenizer

# Token threshold for summarization (from FR-005, FR-015)
TOKEN_THRESHOLD = 2000

# Target reduction percentage for summarization (FR-005)
TARGET_REDUCTION_PERCENT = 70.0


def count_tokens(text: str) -> int:
    """Count tokens in text using GPT-4 tokenizer (cl100k_base).

    Args:
        text: Text to count tokens for

    Returns:
        Number of tokens in the text

    Example:
        >>> count_tokens("Hello, world!")
        4
    """
    return len(encoding.encode(text))


def should_summarize(response: dict, response_json: str | None = None) -> bool:
    """Determine if API response exceeds token threshold and needs summarization.

    Args:
        response: API response dictionary
        response_json: Pre-serialized JSON string (optional, to avoid redundant serialization)

    Returns:
        True if response exceeds 2000 tokens, False otherwise

    Note:
        - Responses ≤2000 tokens: pass through unmodified (FR-015)
        - Responses >2000 tokens: summarize (FR-005)
    """
    response_text = response_json if response_json is not None else json.dumps(response)
    token_count = count_tokens(response_text)
    return token_count > TOKEN_THRESHOLD


@dataclass
class ContextManagedResponse:
    """Tracks context management metadata for MCP tool responses.

    Attributes:
        original_response: The unmodified API response
        token_count: Number of tokens in original response
        was_summarized: True if response was summarized
        final_response: The response sent to LLM (original or summarized)
        reduction_percent: Percentage token reduction (if summarized)
    """

    original_response: dict[str, Any]
    token_count: int
    was_summarized: bool
    final_response: dict[str, Any]
    reduction_percent: float = 0.0

    @classmethod
    def create_passthrough(
        cls, response: dict[str, Any], response_json: str | None = None
    ) -> "ContextManagedResponse":
        """Create a pass-through response (≤2000 tokens, no summarization).

        Args:
            response: Original API response
            response_json: Pre-serialized JSON string (optional, to avoid redundant serialization)

        Returns:
            ContextManagedResponse with was_summarized=False

        Example:
            >>> response = {"breeds": [...]}
            >>> managed = ContextManagedResponse.create_passthrough(response)
            >>> managed.was_summarized
            False
        """
        # Reuse pre-serialized JSON if available to avoid redundant serialization
        response_text = response_json if response_json is not None else json.dumps(response)
        token_count = count_tokens(response_text)

        # Add metadata to final response
        final_response = {
            **response,
            "_summarized": False,
            "_original_token_count": token_count,
        }

        return cls(
            original_response=response,
            token_count=token_count,
            was_summarized=False,
            final_response=final_response,
            reduction_percent=0.0,
        )

    @classmethod
    def create_summarized(
        cls,
        original_response: dict[str, Any],
        summarized_response: dict[str, Any],
        original_json: str | None = None,
    ) -> "ContextManagedResponse":
        """Create a summarized response (>2000 tokens).

        Args:
            original_response: Original API response
            summarized_response: Summarized version of response
            original_json: Pre-serialized JSON string (optional, to avoid redundant serialization)

        Returns:
            ContextManagedResponse with was_summarized=True

        Example:
            >>> original = {"animal": {...}}  # 3000 tokens
            >>> summary = {"animal": {...}}   # 900 tokens
            >>> managed = ContextManagedResponse.create_summarized(original, summary)
            >>> managed.was_summarized
            True
            >>> managed.reduction_percent
            70.0
        """
        # Reuse pre-serialized JSON if available to avoid redundant serialization
        if original_json is not None:
            original_text = original_json
        else:
            original_text = json.dumps(original_response)
        original_tokens = count_tokens(original_text)

        summary_text = json.dumps(summarized_response)
        summary_tokens = count_tokens(summary_text)

        reduction = ((original_tokens - summary_tokens) / original_tokens) * 100.0

        # Record summarization metrics (SC-002)
        if server_metrics:
            server_metrics.record_summarization(reduction)

        # Add metadata to final response
        final_response = {
            **summarized_response,
            "_summarized": True,
            "_original_token_count": original_tokens,
            "_summary_token_count": summary_tokens,
            "_reduction_percent": round(reduction, 2),
        }

        return cls(
            original_response=original_response,
            token_count=original_tokens,
            was_summarized=True,
            final_response=final_response,
            reduction_percent=reduction,
        )

    def meets_target(self) -> bool:
        """Check if summarization meets 70% reduction target (SC-002).

        Returns:
            True if reduction >=70%, False otherwise

        Note:
            Always returns True for pass-through responses
        """
        if not self.was_summarized:
            return True

        return self.reduction_percent >= TARGET_REDUCTION_PERCENT


@dataclass
class SummarizedAnimalResponse:
    """Summarized representation of animal data preserving FR-005a required fields.

    This model implements the summarization strategy defined in FR-005a, preserving:
    - Identity: lpn_id, breed
    - Pedigree: sire, dam
    - Offspring: total_progeny
    - Contact: breeder contact information
    - Top traits: Best 3 traits by accuracy (>=50%, sorted by accuracy)

    Fields omitted per FR-005b:
    - Low-accuracy traits (accuracy <50%)
    - Verbose pedigree details
    - Full progeny lists (keep count only)
    - Registration metadata
    """

    lpn_id: str
    breed: str
    sire: str | None = None
    dam: str | None = None
    total_progeny: int = 0
    contact: dict[str, Any] | None = None
    top_traits: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dict representation of summarized animal data
        """
        result = {
            "lpn_id": self.lpn_id,
            "breed": self.breed,
            "total_progeny": self.total_progeny,
            "top_traits": self.top_traits,
        }

        if self.sire:
            result["sire"] = self.sire
        if self.dam:
            result["dam"] = self.dam
        if self.contact:
            result["contact"] = self.contact

        return result

    @staticmethod
    def select_top_traits(
        traits: dict[str, Any], max_traits: int = 3, min_accuracy: float = 0.5
    ) -> list[dict[str, Any]]:
        """Select top N traits by accuracy for inclusion in summary.

        Args:
            traits: Dict of trait name -> trait data (with 'accuracy' and 'value' keys)
            max_traits: Maximum number of traits to include (default: 3)
            min_accuracy: Minimum accuracy threshold (default: 0.5 = 50%)

        Returns:
            List of top traits sorted by accuracy (highest first)

        Example:
            >>> traits = {
            ...     "BWT": {"value": 0.5, "accuracy": 0.89},
            ...     "WWT": {"value": 1.2, "accuracy": 0.45},
            ...     "YWT": {"value": 2.1, "accuracy": 0.92}
            ... }
            >>> SummarizedAnimalResponse.select_top_traits(traits, max_traits=2)
            [
                {"trait": "YWT", "value": 2.1, "accuracy": 0.92},
                {"trait": "BWT", "value": 0.5, "accuracy": 0.89}
            ]
        """
        # Filter traits by minimum accuracy
        filtered_traits = [
            {"trait": name, **data}
            for name, data in traits.items()
            if data.get("accuracy", 0) >= min_accuracy
        ]

        # Sort by accuracy (descending)
        sorted_traits = sorted(filtered_traits, key=lambda t: t.get("accuracy", 0), reverse=True)

        # Return top N
        return sorted_traits[:max_traits]


def summarize_response(
    response: dict[str, Any], token_budget: int = TOKEN_THRESHOLD
) -> dict[str, Any]:
    """Summarize API response according to FR-005a/FR-005b rules.

    This function implements the summarization strategy:
    - Preserve FR-005a required fields (identity, pedigree, contact, top traits)
    - Omit FR-005b fields (low-accuracy traits, verbose details)
    - Target 70% token reduction (SC-002)

    Args:
        response: Original API response dictionary
        token_budget: Target token count (default: 2000)

    Returns:
        Summarized response dictionary

    Example:
        >>> response = {
        ...     "lpn_id": "6####92020###249",
        ...     "breed": "Katahdin",
        ...     "traits": {"BWT": {"value": 0.5, "accuracy": 0.89}, ...},
        ...     "progeny": {"animals": [...], "total_count": 6}
        ... }
        >>> summary = summarize_response(response)
        >>> "lpn_id" in summary
        True
        >>> "top_traits" in summary
        True
    """
    # Extract required fields per FR-005a
    lpn_id = response.get("lpn_id", response.get("LpnId", ""))
    breed = response.get("breed", response.get("Breed", ""))

    # Handle sire/dam - can be string or nested dict
    sire_value = response.get("sire_id") or response.get("sire")
    if isinstance(sire_value, dict):
        sire = sire_value.get("lpn_id")
    elif isinstance(sire_value, str):
        sire = sire_value
    else:
        sire = None

    dam_value = response.get("dam_id") or response.get("dam")
    if isinstance(dam_value, dict):
        dam = dam_value.get("lpn_id")
    elif isinstance(dam_value, str):
        dam = dam_value
    else:
        dam = None

    # Extract progeny count (not full list per FR-005b)
    progeny_data = response.get("progeny", {})
    total_progeny = progeny_data.get("total_count", 0) if isinstance(progeny_data, dict) else 0

    # Extract contact information - handle both nested dict and flat dict
    contact_raw = response.get("contact") or response.get("contact_info")
    contact = None
    if isinstance(contact_raw, dict):
        # Filter out None values to keep contact compact
        contact = {k: v for k, v in contact_raw.items() if v is not None}
        if not contact:  # If all values were None
            contact = None

    # Extract and filter traits - handle both formats:
    # Format 1: {"BWT": {"value": 0.5, "accuracy": 0.89}}  (from API)
    # Format 2: {"BWT": {"name": "BWT", "value": 0.5, "accuracy": 89}}  (dataclass)
    traits_raw = response.get("traits", {})
    traits_normalized = {}
    if isinstance(traits_raw, dict):
        for trait_name, trait_data in traits_raw.items():
            if isinstance(trait_data, dict):
                # Extract value and accuracy, handling both formats
                value = trait_data.get("value", 0)
                accuracy = trait_data.get("accuracy", 0)

                # Handle accuracy as percentage (0-100) or decimal (0-1)
                # If accuracy > 1, it's a percentage, convert to decimal
                if accuracy > 1:
                    accuracy = accuracy / 100.0

                traits_normalized[trait_name] = {
                    "value": value,
                    "accuracy": accuracy,
                }

    top_traits = SummarizedAnimalResponse.select_top_traits(
        traits_normalized, max_traits=3, min_accuracy=0.5
    )

    # Create summarized model
    summarized = SummarizedAnimalResponse(
        lpn_id=lpn_id,
        breed=breed,
        sire=sire,
        dam=dam,
        total_progeny=total_progeny,
        contact=contact,
        top_traits=top_traits,
    )

    return summarized.to_dict()
