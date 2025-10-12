# Data Model: Context-Efficient API-to-MCP Gateway

**Feature**: Context-Efficient API-to-MCP Gateway
**Branch**: `001-create-an-mcp`
**Date**: 2025-10-11
**Purpose**: Define data structures, validation rules, and state transitions for MCP server implementation

## Model Overview

This document defines the data models for the MCP server layer that wraps NSIPClient. The existing NSIP data models (in `nsip_client.models`) remain unchanged. New models are introduced for MCP-specific concerns: tool definitions, cached responses, context management, and transport configuration.

---

## 1. MCP Tool Definition

**Purpose**: Represents an MCP tool that wraps an NSIPClient method

**Source**: Derived from FR-010 (9 NSIPClient methods) and FR-002 (auto-generated tool descriptions)

```python
from dataclasses import dataclass
from typing import Dict, Any, Callable, Optional

@dataclass
class McpToolDefinition:
    """Defines an MCP tool that exposes an NSIPClient method."""

    name: str                          # MCP tool name (e.g., "nsip_get_animal")
    description: str                   # Human-readable description for LLMs
    method_name: str                   # NSIPClient method name (e.g., "get_animal_details")
    parameters: Dict[str, Any]         # JSON Schema for parameters
    handler: Callable                  # Function that executes the tool
    requires_context_management: bool  # Whether to apply token counting/summarization

    def validate_parameters(self, params: Dict[str, Any]) -> None:
        """Validate parameters against JSON Schema (FR-003)."""
        # Implementation uses jsonschema library
        pass

    def to_mcp_schema(self) -> Dict[str, Any]:
        """Convert to MCP tool schema format."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": self.parameters,
                "required": [k for k, v in self.parameters.items() if v.get("required", False)]
            }
        }
```

**Validation Rules**:
- `name` MUST be non-empty and follow pattern `nsip_*`
- `description` MUST be non-empty (minimum 10 characters)
- `parameters` MUST be valid JSON Schema
- `handler` MUST be callable
- `requires_context_management` MUST be boolean

**Tool Instances** (from FR-010):
1. `nsip_get_last_update` → NSIPClient.get_date_last_updated()
2. `nsip_list_breeds` → NSIPClient.get_available_breed_groups()
3. `nsip_get_statuses` → NSIPClient.get_statuses_by_breed_group()
4. `nsip_get_trait_ranges` → NSIPClient.get_trait_ranges_by_breed()
5. `nsip_search_animals` → NSIPClient.search_animals()
6. `nsip_get_animal` → NSIPClient.get_animal_details()
7. `nsip_get_lineage` → NSIPClient.get_lineage()
8. `nsip_get_progeny` → NSIPClient.get_progeny()
9. `nsip_search_by_lpn` → NSIPClient.search_by_lpn()

---

## 2. Cached Response

**Purpose**: Represents a cached API response with expiration metadata

**Source**: Derived from FR-009 (caching), Key Entity "Response Cache", and clarifications (1-hour TTL, cache key format)

```python
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

@dataclass
class CachedResponse:
    """Cached API response with expiration tracking."""

    cache_key: str          # Format: "method_name:sorted_json_params"
    value: Any              # Original API response (dict)
    created_at: datetime    # When cached
    expires_at: datetime    # When expires (created_at + TTL)
    token_count: int        # Token count of response (for metrics)
    access_count: int = 0   # Number of cache hits (for SC-006 metrics)

    @staticmethod
    def make_key(method_name: str, params: Dict[str, Any]) -> str:
        """Generate cache key from method name and parameters."""
        import json
        sorted_params = json.dumps(params, sort_keys=True)
        return f"{method_name}:{sorted_params}"

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return datetime.now() >= self.expires_at

    def record_hit(self) -> None:
        """Record cache access for metrics."""
        self.access_count += 1
```

**Validation Rules**:
- `cache_key` MUST be non-empty
- `created_at` MUST be ≤ current time
- `expires_at` MUST be > `created_at`
- `token_count` MUST be ≥ 0
- `access_count` MUST be ≥ 0

**State Transitions**:
```
[Created] → (TTL expires) → [Expired] → (Evicted)
          ← (Cache hit)   ← [Active]
```

**Cache Configuration** (from clarifications):
- Default TTL: 3600 seconds (1 hour)
- Max cache size: 1000 entries (prevent memory exhaustion per constraints)
- Eviction policy: FIFO when max size reached

---

## 3. Context-Managed Response

**Purpose**: Represents an API response after context management (token counting, optional summarization)

**Source**: Derived from FR-005 (summarization), FR-015 (pass-through), FR-005a/FR-005b (summarization rules)

```python
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class ContextManagedResponse:
    """API response after context management processing."""

    original_response: dict         # Original API response
    token_count: int                # Token count of original response
    was_summarized: bool            # Whether summarization was applied
    final_response: dict            # Final response (summarized or pass-through)
    final_token_count: int          # Token count of final response
    reduction_percent: Optional[float] = None  # Token reduction % if summarized

    def meets_target(self) -> bool:
        """Check if summarization met 70% reduction target (SC-002)."""
        if not self.was_summarized:
            return True  # Pass-through responses auto-pass
        return self.reduction_percent and self.reduction_percent >= 70.0

    @classmethod
    def create_passthrough(cls, response: dict, token_count: int) -> 'ContextManagedResponse':
        """Create pass-through response (≤2000 tokens, FR-015)."""
        return cls(
            original_response=response,
            token_count=token_count,
            was_summarized=False,
            final_response=response,
            final_token_count=token_count,
            reduction_percent=None
        )

    @classmethod
    def create_summarized(cls, response: dict, original_tokens: int, summary: dict, summary_tokens: int) -> 'ContextManagedResponse':
        """Create summarized response (>2000 tokens, FR-005)."""
        reduction = ((original_tokens - summary_tokens) / original_tokens) * 100
        return cls(
            original_response=response,
            token_count=original_tokens,
            was_summarized=True,
            final_response=summary,
            final_token_count=summary_tokens,
            reduction_percent=reduction
        )
```

**Validation Rules**:
- `token_count` MUST be > 0
- `final_token_count` MUST be > 0
- If `was_summarized` is True:
  - `final_token_count` MUST be < `token_count`
  - `reduction_percent` MUST be ≥ 70.0 (SC-002 target)
- If `was_summarized` is False:
  - `token_count` MUST be ≤ 2000 (FR-015 threshold)
  - `final_response` MUST equal `original_response`

**State Transitions**:
```
[API Response] → (token_count ≤ 2000) → [Pass-Through]
               → (token_count > 2000) → [Summarized]
```

---

## 4. Summarized NSIP Response

**Purpose**: Represents a summarized NSIP API response following FR-005a/FR-005b rules

**Source**: Derived from FR-005a (preserve fields), FR-005b (omit fields), NSIP data structure

```python
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class SummarizedAnimalResponse:
    """Summarized NSIP animal details response (FR-005a/FR-005b)."""

    # FR-005a: MUST preserve
    lpn_id: str                      # Unique identifier
    sire: Optional[str]              # Sire identifier
    dam: Optional[str]               # Dam identifier
    breed: str                       # Breed information
    total_progeny: Optional[int]     # Total progeny count
    contact: Optional[Dict[str, Any]]  # All contact information (phone, email, farm)
    top_traits: List[Dict[str, Any]]  # Top 3 traits by accuracy

    # Metadata
    _summarized: bool = True
    _original_token_count: int = 0
    _summary_token_count: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary for MCP response."""
        return {
            "LpnId": self.lpn_id,
            "Sire": self.sire,
            "Dam": self.dam,
            "Breed": self.breed,
            "TotalProgeny": self.total_progeny,
            "Contact": self.contact,
            "TopTraits": self.top_traits,
            "_summarized": self._summarized,
            "_original_token_count": self._original_token_count,
            "_summary_token_count": self._summary_token_count,
        }
```

**FR-005a Validation Rules** (MUST preserve):
- `lpn_id` MUST be non-empty
- `breed` MUST be non-empty
- `contact` MUST include all original contact fields (no filtering per clarifications)
- `top_traits` MUST contain ≤3 items
- Each trait in `top_traits` MUST have accuracy ≥50 (FR-005b rule)

**FR-005b Omission Rules** (MUST omit):
- Traits with accuracy <50
- Redundant nested structures
- Detailed metadata unless specifically requested
- Low-priority fields not in FR-005a preserve list

**Top Traits Selection Algorithm**:
```python
def select_top_traits(traits: List[Dict], max_count: int = 3) -> List[Dict]:
    """Select top N traits by accuracy (FR-005a)."""
    # Filter accuracy >= 50 (FR-005b)
    valid_traits = [t for t in traits if t.get("accuracy", 0) >= 50]

    # Sort by accuracy descending
    sorted_traits = sorted(valid_traits, key=lambda t: t.get("accuracy", 0), reverse=True)

    # Take top N
    return sorted_traits[:max_count]
```

---

## 5. Transport Configuration

**Purpose**: Represents transport mechanism configuration for MCP server

**Source**: Derived from FR-008a (multiple transports), clarifications (MCP_TRANSPORT env var)

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class TransportType(Enum):
    """Supported MCP transport mechanisms."""
    STDIO = "stdio"           # Default, for CLI tools
    HTTP_SSE = "http-sse"     # For web applications
    WEBSOCKET = "websocket"   # For real-time bidirectional communication

@dataclass
class TransportConfig:
    """MCP server transport configuration."""

    transport_type: TransportType
    port: Optional[int] = None  # Required for HTTP_SSE and WEBSOCKET

    @classmethod
    def from_environment(cls) -> 'TransportConfig':
        """Load configuration from environment variables (FR-008a)."""
        import os

        transport_str = os.getenv("MCP_TRANSPORT", "stdio").lower()

        try:
            transport_type = TransportType(transport_str)
        except ValueError:
            raise ValueError(
                f"Invalid MCP_TRANSPORT: {transport_str}. "
                f"Valid values: stdio, http-sse, websocket"
            )

        port = None
        if transport_type in (TransportType.HTTP_SSE, TransportType.WEBSOCKET):
            port_str = os.getenv("MCP_PORT")
            if not port_str:
                raise ValueError(
                    f"MCP_PORT environment variable required for {transport_str} transport"
                )
            port = int(port_str)

        return cls(transport_type=transport_type, port=port)

    def validate(self) -> None:
        """Validate configuration."""
        if self.transport_type in (TransportType.HTTP_SSE, TransportType.WEBSOCKET):
            if self.port is None:
                raise ValueError(f"Port required for {self.transport_type.value} transport")
            if not (1024 <= self.port <= 65535):
                raise ValueError(f"Port must be between 1024 and 65535, got {self.port}")
```

**Validation Rules**:
- `transport_type` MUST be one of: STDIO, HTTP_SSE, WEBSOCKET
- If `transport_type` is HTTP_SSE or WEBSOCKET:
  - `port` MUST be specified
  - `port` MUST be in range [1024, 65535]
- If `transport_type` is STDIO:
  - `port` MUST be None

**Configuration Examples**:
```bash
# stdio (default)
MCP_TRANSPORT=stdio nsip-mcp-server

# HTTP SSE
MCP_TRANSPORT=http-sse MCP_PORT=8000 nsip-mcp-server

# WebSocket
MCP_TRANSPORT=websocket MCP_PORT=9000 nsip-mcp-server
```

---

## 6. MCP Error Response

**Purpose**: Represents structured error responses for LLM interpretation

**Source**: Derived from FR-007 (structured errors), SC-004 (80% retry success), JSON-RPC 2.0 standard

```python
from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import IntEnum

class McpErrorCode(IntEnum):
    """MCP error codes (JSON-RPC 2.0 standard + custom)."""

    # Standard JSON-RPC errors
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603

    # Custom MCP server errors
    NSIP_API_ERROR = -32000        # NSIP API call failed
    CACHE_ERROR = -32001            # Cache operation failed
    SUMMARIZATION_ERROR = -32002    # Summarization failed
    CONTEXT_ERROR = -32003          # Context management error
    TRANSPORT_ERROR = -32004        # Transport-specific error

@dataclass
class McpErrorData:
    """Additional error data to help LLM retry (FR-007, SC-004)."""

    parameter: Optional[str] = None      # Which parameter was invalid
    value: Optional[Any] = None          # Invalid value provided
    expected: Optional[str] = None       # Expected value/format
    suggestion: Optional[str] = None     # Suggested correction
    retry_after: Optional[int] = None    # Seconds to wait before retry

@dataclass
class McpErrorResponse:
    """Structured MCP error response."""

    code: McpErrorCode
    message: str                  # Human-readable error message
    data: Optional[McpErrorData] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to MCP error response format."""
        result = {
            "error": {
                "code": self.code.value,
                "message": self.message,
            }
        }

        if self.data:
            result["error"]["data"] = {
                k: v for k, v in vars(self.data).items() if v is not None
            }

        return result

    @classmethod
    def invalid_params(cls, param: str, value: Any, expected: str, suggestion: str) -> 'McpErrorResponse':
        """Create invalid parameters error (FR-003 validation)."""
        return cls(
            code=McpErrorCode.INVALID_PARAMS,
            message=f"Invalid parameter: {param}",
            data=McpErrorData(
                parameter=param,
                value=value,
                expected=expected,
                suggestion=suggestion
            )
        )

    @classmethod
    def nsip_api_error(cls, method: str, error_msg: str) -> 'McpErrorResponse':
        """Create NSIP API error."""
        return cls(
            code=McpErrorCode.NSIP_API_ERROR,
            message=f"NSIP API call failed: {method}",
            data=McpErrorData(
                parameter="method",
                value=method,
                suggestion=f"Check NSIP API availability and parameters: {error_msg}"
            )
        )
```

**Validation Rules**:
- `code` MUST be valid McpErrorCode
- `message` MUST be non-empty
- If targeting 80% retry success (SC-004), `data.suggestion` SHOULD be provided

**Error Examples** (for testing FR-007, SC-004):
```python
# Invalid LPN ID format
McpErrorResponse.invalid_params(
    param="lpn_id",
    value="123",
    expected="Non-empty string with at least 5 characters",
    suggestion="Provide a valid LPN ID like '6401492020FLE249'"
)

# NSIP API unavailable
McpErrorResponse.nsip_api_error(
    method="get_animal_details",
    error_msg="Connection timeout after 30s"
)
```

---

## 7. Server Metrics

**Purpose**: Track server performance and cache effectiveness for success criteria validation

**Source**: Derived from SC-001 through SC-010 (measurable outcomes)

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict

@dataclass
class ServerMetrics:
    """Server performance and usage metrics."""

    # SC-001: Discovery time
    discovery_times: List[float] = field(default_factory=list)  # Seconds

    # SC-002: Summarization effectiveness
    summarization_reductions: List[float] = field(default_factory=list)  # Percentages

    # SC-003: Validation success rate
    validation_attempts: int = 0
    validation_successes: int = 0

    # SC-004: Error retry success rate
    error_retries: int = 0
    error_retry_successes: int = 0

    # SC-005: Concurrent connections
    current_connections: int = 0
    peak_connections: int = 0

    # SC-006: Cache effectiveness
    cache_hits: int = 0
    cache_misses: int = 0

    # SC-007: Startup time
    startup_time: Optional[float] = None  # Seconds

    # SC-009: API interaction logging
    api_calls_logged: int = 0

    # SC-010: Long-running operation updates
    long_running_updates_sent: int = 0

    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate (SC-006 target: 40%)."""
        total = self.cache_hits + self.cache_misses
        return (self.cache_hits / total * 100) if total > 0 else 0.0

    def validation_success_rate(self) -> float:
        """Calculate validation success rate (SC-003 target: 95%)."""
        return (self.validation_successes / self.validation_attempts * 100) if self.validation_attempts > 0 else 0.0

    def avg_summarization_reduction(self) -> float:
        """Calculate average summarization reduction (SC-002 target: 70%)."""
        return sum(self.summarization_reductions) / len(self.summarization_reductions) if self.summarization_reductions else 0.0

    def meets_success_criteria(self) -> Dict[str, bool]:
        """Check if server meets success criteria."""
        return {
            "SC-001": all(t < 5.0 for t in self.discovery_times),
            "SC-002": self.avg_summarization_reduction() >= 70.0,
            "SC-003": self.validation_success_rate() >= 95.0,
            "SC-006": self.cache_hit_rate() >= 40.0,
            "SC-007": self.startup_time is not None and self.startup_time < 3.0,
        }
```

**Metrics Collection**:
- Discovery time: Measured from client connection to tool list returned
- Summarization reduction: Token reduction percentage for each summarized response
- Validation: Track valid vs invalid parameter attempts
- Cache: Increment hit/miss counters on each cache lookup
- Startup: Measured from process start to server ready state

---

## Model Relationships

```
McpToolDefinition
    ├─> handler() returns API response
    └─> CachedResponse (via cache lookup)
            └─> ContextManagedResponse (after token counting)
                    ├─> [Pass-through] (≤2000 tokens)
                    └─> SummarizedAnimalResponse (>2000 tokens)

TransportConfig
    └─> Determines how MCP server communicates with clients

McpErrorResponse
    └─> Returned when any operation fails (FR-007)

ServerMetrics
    └─> Tracks all operations for SC validation
```

---

## Validation Summary

All data models include:
- ✅ **Type hints**: Full mypy type checking support (Principle IV)
- ✅ **Validation rules**: Input validation before processing (FR-003)
- ✅ **Testability**: All models easily testable in unit tests (Principle II)
- ✅ **Documentation**: Docstrings for all classes and methods (Principle V)
- ✅ **Immutability**: Use dataclasses for value objects where appropriate

All models align with:
- ✅ **Functional Requirements**: FR-001 through FR-015
- ✅ **Success Criteria**: SC-001 through SC-010
- ✅ **Constitution**: All 5 principles satisfied
- ✅ **Specification Entities**: Derived from Key Entities section in spec.md

Ready to proceed with contract generation (Phase 1 continuation).
