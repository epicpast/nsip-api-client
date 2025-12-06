"""
TypedDict schemas for NSIP hook input/output.

Provides type safety and documentation for hook data structures.
"""

from typing import Any, Dict, List, Optional

# Python 3.11+ has these in typing, fallback to typing_extensions for 3.10
try:
    from typing import NotRequired, TypedDict
except ImportError:
    from typing_extensions import NotRequired, TypedDict


# =============================================================================
# Core Hook I/O Types
# =============================================================================


class ToolInfo(TypedDict):
    """Tool information passed to hooks."""

    name: str
    parameters: Dict[str, Any]


class PreToolUseInput(TypedDict):
    """Input for PreToolUse hooks."""

    tool: ToolInfo
    metadata: NotRequired[Dict[str, Any]]


class PostToolUseInput(TypedDict):
    """Input for PostToolUse hooks."""

    tool: ToolInfo
    result: Dict[str, Any]
    metadata: NotRequired[Dict[str, Any]]


class UserPromptSubmitInput(TypedDict):
    """Input for UserPromptSubmit hooks."""

    prompt: str
    metadata: NotRequired[Dict[str, Any]]


class SessionStartInput(TypedDict):
    """Input for SessionStart hooks."""

    metadata: NotRequired[Dict[str, Any]]


class HookOutput(TypedDict):
    """Standard output for all hooks."""

    continue_: bool  # Note: 'continue' is reserved, use continue_ in code
    metadata: Dict[str, Any]
    context: NotRequired[str]
    warning: NotRequired[str]
    error: NotRequired[str]


# =============================================================================
# Validation Types
# =============================================================================


class LPNValidationResult(TypedDict):
    """Result of LPN validation."""

    is_valid: bool
    lpn_id: str
    error_message: NotRequired[str]
    normalized: NotRequired[str]


class IntentDetection(TypedDict):
    """Detected user intent from prompt analysis."""

    search_animal: bool
    get_lineage: bool
    get_progeny: bool
    compare_traits: bool
    trait_analysis: bool


class PromptAnalysis(TypedDict):
    """Result of prompt analysis."""

    detection_performed: bool
    ids_detected: int
    detected_ids: List[str]
    intents: IntentDetection
    suggestion_message: NotRequired[str]


# =============================================================================
# Cache Types
# =============================================================================


class CacheEntry(TypedDict):
    """Structure of a cached result."""

    tool: str
    parameters: Dict[str, Any]
    result: Dict[str, Any]
    cached_at: str  # ISO 8601 timestamp
    ttl_minutes: int


class CacheStats(TypedDict):
    """Cache statistics."""

    hits: int
    misses: int
    entries: int
    oldest_entry: NotRequired[str]


# =============================================================================
# Retry Types
# =============================================================================


class RetryResult(TypedDict):
    """Result of retry handling."""

    retry_needed: bool
    retry_count: NotRequired[int]
    status: NotRequired[str]
    reason: NotRequired[str]
    context_message: NotRequired[str]


# =============================================================================
# Health Check Types
# =============================================================================


class HealthCheckResult(TypedDict):
    """Result of API health check."""

    api_available: bool
    response_time_ms: NotRequired[float]
    error: NotRequired[str]
    timestamp: str


# =============================================================================
# Export Types
# =============================================================================


class ExportMetadata(TypedDict):
    """Metadata for exported files."""

    export_type: str  # 'csv', 'pedigree', 'report'
    file_path: str
    record_count: NotRequired[int]
    timestamp: str


# =============================================================================
# Breed/Trait Types
# =============================================================================


class BreedInfo(TypedDict):
    """Breed information for context injection."""

    id: int
    name: str
    group: str
    characteristics: List[str]
    key_traits: List[str]


class TraitDefinition(TypedDict):
    """Trait definition for dictionary lookup."""

    abbreviation: str
    full_name: str
    description: str
    unit: NotRequired[str]
    typical_range: NotRequired[str]
    category: str  # 'growth', 'maternal', 'carcass', 'wool', 'reproduction'


# =============================================================================
# Report Types
# =============================================================================


class BreedingReportSection(TypedDict):
    """Section of a breeding report."""

    title: str
    content: str


class BreedingReport(TypedDict):
    """Full breeding report structure."""

    lpn_id: str
    generated_at: str
    summary: BreedingReportSection
    traits: BreedingReportSection
    lineage: NotRequired[BreedingReportSection]
    recommendations: NotRequired[BreedingReportSection]
