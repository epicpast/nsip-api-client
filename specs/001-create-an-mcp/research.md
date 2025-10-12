# Technical Research: Context-Efficient API-to-MCP Gateway

**Feature**: Context-Efficient API-to-MCP Gateway
**Branch**: `001-create-an-mcp`
**Date**: 2025-10-11
**Purpose**: Resolve technical unknowns and establish best practices for implementation

## Research Overview

This document consolidates technical research for building an MCP server that wraps the NSIP client library. Key areas investigated: FastMCP 2.0 framework capabilities, tiktoken integration patterns, uv/uvx tooling, context-efficient summarization strategies, and multi-transport MCP server patterns.

---

## 1. FastMCP 2.0 Framework

### Decision
Use FastMCP 2.0 as the MCP server framework with its high-level decorator-based API for tool definitions.

### Rationale
- **Industry Leadership**: FastMCP is the leading Python library for MCP development, with FastMCP 1.0 incorporated into the official MCP SDK
- **Production Ready**: Powers production applications across thousands of developers
- **Minimal Boilerplate**: High-level Pythonic interface enables rapid development with less code
- **Complete Feature Set**: Built-in support for Resources, Tools, and Prompts in MCP protocol
- **Enterprise Auth Support**: Although not needed for NSIP (public API), provides future extensibility for multi-API support (User Story 4)
- **Active Development**: FastMCP 2.0 released in 2025 with modern patterns and comprehensive documentation at gofastmcp.com

### Alternatives Considered
1. **Official MCP Python SDK (`mcp` package)**: Lower-level API, more boilerplate code, steeper learning curve
2. **Custom MCP Implementation**: Unnecessary reinvention, would violate constitution's simplicity principle
3. **Other MCP Frameworks**: No mature Python alternatives with FastMCP's feature completeness

### Implementation Approach
```python
from fastmcp import FastMCP

# Server initialization
mcp = FastMCP("NSIP Sheep Breeding Data")

# Tool definition pattern (example)
@mcp.tool()
def nsip_get_animal(search_string: str) -> dict:
    """Get detailed information about a sheep by LPN or other identifier."""
    # Wrap NSIPClient.get_animal_details()
    # Apply context management (token counting, summarization)
    pass
```

**Key Patterns**:
- Use `@mcp.tool()` decorator for each of 9 NSIPClient methods
- Server startup via `mcp.run()` with transport configuration
- Tool descriptions auto-generated from docstrings (satisfies FR-002)

---

## 2. Token Counting with tiktoken

### Decision
Use `tiktoken` library with `cl100k_base` encoding (GPT-4 tokenizer) for measuring response sizes against 2000-token threshold.

### Rationale
- **Official OpenAI Library**: Maintained by OpenAI, ensures accurate token counting for GPT models
- **Fast BPE Tokenizer**: Rust-based implementation for high performance
- **cl100k_base Encoding**: Standard for GPT-4 and GPT-3.5-Turbo models (most common MCP client use case)
- **Production Patterns**: Well-documented caching and offline deployment strategies
- **Cost Awareness**: Enables accurate pre-flight cost estimation before API calls

### Alternatives Considered
1. **Character Count Estimation** (chars/4): Inaccurate, violates SC-002 measurement requirement
2. **Manual Tokenization**: Unnecessary complexity, reinventing the wheel
3. **Other Tokenizers**: Not aligned with GPT-4 encoding used by most LLM clients

### Implementation Approach
```python
import tiktoken

# Initialize once at server startup
encoding = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    """Count tokens in text using GPT-4 tokenizer."""
    return len(encoding.encode(text))

def should_summarize(response: dict) -> bool:
    """Determine if response exceeds 2000-token threshold."""
    response_text = json.dumps(response)
    return count_tokens(response_text) > 2000
```

**Best Practices**:
- **Caching**: Set `TIKTOKEN_CACHE_DIR` environment variable for offline/production deployments
- **Boundary Handling**: Responses at exactly 2000 tokens → pass through (per clarifications)
- **Thread Safety**: tiktoken encoding object is thread-safe, can be shared across concurrent connections
- **Unicode Safety**: Use `.decode_single_token_bytes()` for single-token operations to avoid lossy UTF-8 boundary issues

---

## 3. uv/uvx Package Management

### Decision
Use Astral's `uv` for dependency management and `uvx` for tool execution in development and deployment workflows.

### Rationale
- **Extreme Speed**: 10-100x faster than pip/pip-tools for dependency resolution (Rust implementation)
- **Unified Tooling**: Single tool replaces pip, pip-tools, pipx, poetry, pyenv, virtualenv, and more
- **Python Version Management**: Automatically installs missing Python versions
- **Modern Standards**: Fully compatible with PEP 621 (pyproject.toml) and existing project structure
- **Single-File Script Support**: Can manage dependencies for standalone scripts (useful for MCP server CLI)
- **Active Development**: Regular releases in 2025 improving compatibility and features

### Alternatives Considered
1. **pip + pip-tools**: Slower, requires multiple tools for complete workflow
2. **Poetry**: Heavier, slower, introduces non-standard configuration patterns
3. **Traditional virtualenv + pip**: Manual Python version management, no modern conveniences

### Implementation Approach

**Development**:
```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run MCP server
uv run nsip-mcp-server

# Add new dependency
uv add fastmcp tiktoken
```

**Deployment** (via uvx for tool execution):
```bash
# Install MCP server from GitHub release
uvx --from git+https://github.com/USERNAME/nsip-api-client@v1.0.0 nsip-mcp-server

# Or from local wheel
uvx nsip_api_client-1.0.0-py3-none-any.whl nsip-mcp-server
```

**Configuration** (pyproject.toml updates):
```toml
[project]
dependencies = [
    "fastmcp>=2.0",
    "tiktoken>=0.8.0",
    # existing dependencies...
]

[project.scripts]
nsip-mcp-server = "nsip_mcp.cli:main"
```

---

## 4. Context-Efficient Summarization Strategy

### Decision
Implement rule-based summarization preserving critical fields (per FR-005a/FR-005b) with token-aware truncation.

### Rationale
- **Deterministic Output**: Rule-based approach ensures consistent, testable behavior
- **Domain-Specific**: Tailored to NSIP sheep breeding data structure (LpnId, Sire, Dam, traits)
- **Specification Compliance**: Directly implements FR-005a (preserve) and FR-005b (omit) requirements
- **No External Dependencies**: Avoids LLM-based summarization (cost, latency, non-determinism)
- **Measurable**: Can verify 70% token reduction (SC-002) in automated tests

### Alternatives Considered
1. **LLM-Based Summarization**: High cost, latency, non-deterministic, violates simplicity principle
2. **Generic Truncation**: Loses semantic meaning, fails "key information" retention requirement
3. **No Summarization**: Violates FR-005, context window overflows for large responses

### Implementation Approach

**Summarization Rules** (from FR-005a/FR-005b):
```python
def summarize_response(response: dict, token_budget: int = 600) -> dict:
    """
    Summarize NSIP API response to fit token budget (~70% reduction from 2000+ tokens).

    Preserves (FR-005a):
    - Unique identifiers: LpnId, Sire, Dam
    - Breed information
    - Total counts: TotalProgeny
    - Contact information (all fields)
    - Top 3 traits by accuracy

    Omits (FR-005b):
    - Traits with accuracy <50
    - Redundant nested structures
    - Detailed metadata unless specifically requested
    """
    summary = {
        "LpnId": response.get("LpnId"),
        "Sire": response.get("Sire"),
        "Dam": response.get("Dam"),
        "Breed": response.get("Breed"),
        "TotalProgeny": response.get("TotalProgeny"),
        "Contact": response.get("Contact"),  # Preserve all contact info per FR-015 clarification
    }

    # Filter and rank traits by accuracy
    traits = response.get("Traits", [])
    high_accuracy_traits = [t for t in traits if t.get("accuracy", 0) >= 50]
    top_traits = sorted(high_accuracy_traits, key=lambda t: t.get("accuracy", 0), reverse=True)[:3]
    summary["TopTraits"] = top_traits

    # Add metadata indicating summarization
    summary["_summarized"] = True
    summary["_original_token_count"] = count_tokens(json.dumps(response))
    summary["_summary_token_count"] = count_tokens(json.dumps(summary))

    return summary
```

**Validation Strategy**:
- Unit tests verify 70% reduction on sample NSIP responses
- Integration tests ensure all FR-005a fields present in summaries
- Contract tests verify LLM clients can parse summarized responses

---

## 5. Multi-Transport Support (stdio, HTTP SSE, WebSocket)

### Decision
Implement transport selection via `MCP_TRANSPORT` environment variable with FastMCP's built-in transport handlers.

### Rationale
- **MCP Standard Compliance**: All three transports (stdio, HTTP SSE, WebSocket) are defined in MCP specification
- **Use Case Diversity**: Different clients prefer different transports (CLI tools use stdio, web apps use HTTP SSE/WebSocket)
- **FastMCP Built-in Support**: Framework provides transport abstraction, minimal custom code needed
- **Configuration Simplicity**: Single environment variable (FR-008a requirement)
- **Default Sensible**: stdio is default (most common for MCP tools)

### Alternatives Considered
1. **stdio Only**: Limits adoption, fails FR-008a multi-transport requirement
2. **Configuration File**: More complex than environment variable, violates simplicity
3. **Auto-Detection**: Fragile, non-explicit, harder to debug

### Implementation Approach

**Transport Configuration**:
```python
import os
from fastmcp import FastMCP
from fastmcp.transports import StdioTransport, HttpSseTransport, WebSocketTransport

def get_transport():
    """Get transport based on MCP_TRANSPORT environment variable."""
    transport_type = os.getenv("MCP_TRANSPORT", "stdio").lower()

    if transport_type == "stdio":
        return StdioTransport()
    elif transport_type == "http-sse":
        port = int(os.getenv("MCP_PORT", "8000"))
        return HttpSseTransport(port=port)
    elif transport_type == "websocket":
        port = int(os.getenv("MCP_PORT", "8000"))
        return WebSocketTransport(port=port)
    else:
        raise ValueError(f"Invalid MCP_TRANSPORT: {transport_type}. Use stdio, http-sse, or websocket.")

# Server initialization with transport
mcp = FastMCP("NSIP Sheep Breeding Data")
mcp.run(transport=get_transport())
```

**Usage Examples**:
```bash
# stdio (default)
nsip-mcp-server

# HTTP SSE
MCP_TRANSPORT=http-sse MCP_PORT=8000 nsip-mcp-server

# WebSocket
MCP_TRANSPORT=websocket MCP_PORT=9000 nsip-mcp-server
```

**Testing Strategy**:
- Unit tests mock transport layer
- Integration tests verify each transport can handle MCP protocol messages
- Contract tests ensure clients can connect via all three transports

---

## 6. In-Memory Caching Strategy

### Decision
Implement time-based in-memory cache with 1-hour TTL using Python's `functools.lru_cache` + custom expiration logic.

### Rationale
- **Simplicity**: No external dependencies (Redis, Memcached), follows constitution simplicity principle
- **Performance**: In-process memory access faster than network cache lookups
- **Specification Compliance**: 1-hour TTL per clarifications, session-based per constraints
- **Cache Key Format**: `method_name:sorted_json_params` per clarifications (deterministic, collision-free)
- **Bounded Memory**: Can set size limits to prevent resource exhaustion (constraint requirement)

### Alternatives Considered
1. **Redis/Memcached**: Overkill for single-server deployment, adds operational complexity
2. **Persistent Storage**: Violates "session-based caching only" constraint
3. **No Caching**: Fails FR-009 and SC-006 (40% API call reduction target)

### Implementation Approach

**Cache Implementation**:
```python
import json
import time
from functools import wraps
from typing import Any, Callable

class TtlCache:
    """Time-based cache with expiration."""

    def __init__(self, ttl_seconds: int = 3600, max_size: int = 1000):
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._cache = {}  # {cache_key: (value, expiration_time)}

    def get(self, key: str) -> Any | None:
        if key in self._cache:
            value, expiration = self._cache[key]
            if time.time() < expiration:
                return value
            else:
                del self._cache[key]  # Expired
        return None

    def set(self, key: str, value: Any):
        if len(self._cache) >= self.max_size:
            # Evict oldest entry (simple FIFO)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

        expiration = time.time() + self.ttl_seconds
        self._cache[key] = (value, expiration)

    def make_key(self, method_name: str, **params) -> str:
        """Generate cache key: method_name:sorted_json_params"""
        sorted_params = json.dumps(params, sort_keys=True)
        return f"{method_name}:{sorted_params}"

# Global cache instance
response_cache = TtlCache(ttl_seconds=3600, max_size=1000)

def cached_api_call(method_name: str):
    """Decorator to cache API responses."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(**kwargs):
            cache_key = response_cache.make_key(method_name, **kwargs)

            # Check cache
            cached_value = response_cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Call API
            result = func(**kwargs)

            # Store in cache
            response_cache.set(cache_key, result)
            return result

        return wrapper
    return decorator
```

**Usage Pattern**:
```python
@cached_api_call("get_animal_details")
def get_animal_details_cached(search_string: str) -> dict:
    client = NSIPClient()
    return client.get_animal_details(search_string)
```

**Cache Metrics** (for SC-006 validation):
- Track cache hits/misses
- Log cache hit rate in server metrics
- Target: 40%+ hit rate in typical usage

---

## 7. Error Handling and Structured Error Messages

### Decision
Implement MCP-compliant error responses with structured error codes, human-readable messages, and suggested actions.

### Rationale
- **FR-007 Requirement**: Structured error messages that LLMs can interpret and act upon
- **SC-004 Target**: 80% of errors should enable LLM to retry with corrected parameters
- **MCP Protocol**: Defines error response format in JSON-RPC 2.0 standard
- **Debuggability**: FR-011 logging requirement satisfied by structured errors

### Implementation Approach

**Error Response Structure**:
```python
from enum import Enum

class McpErrorCode(Enum):
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    NSIP_API_ERROR = -32000
    CACHE_ERROR = -32001
    SUMMARIZATION_ERROR = -32002

class McpError(Exception):
    """MCP-compliant structured error."""

    def __init__(self, code: McpErrorCode, message: str, data: dict = None):
        self.code = code.value
        self.message = message
        self.data = data or {}
        super().__init__(message)

    def to_mcp_response(self) -> dict:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "data": self.data
            }
        }

# Usage examples
def validate_lpn_id(lpn_id: str):
    if not lpn_id or len(lpn_id) < 5:
        raise McpError(
            code=McpErrorCode.INVALID_PARAMS,
            message="Invalid LPN ID format",
            data={
                "parameter": "lpn_id",
                "value": lpn_id,
                "expected": "Non-empty string with at least 5 characters",
                "suggestion": "Provide a valid LPN ID like '6####92020###249'"
            }
        )
```

**Logging Integration** (FR-011):
```python
import logging

logger = logging.getLogger("nsip_mcp")

def log_api_interaction(method: str, params: dict, result: Any = None, error: Exception = None):
    """Log all API interactions for debugging and auditing."""
    log_entry = {
        "timestamp": time.time(),
        "method": method,
        "params": params,
        "success": error is None,
    }

    if error:
        log_entry["error"] = str(error)
        logger.error(f"API call failed: {method}", extra=log_entry)
    else:
        log_entry["token_count"] = count_tokens(json.dumps(result)) if result else 0
        logger.info(f"API call succeeded: {method}", extra=log_entry)
```

---

## 8. Concurrency and Connection Management

### Decision
Use FastMCP's built-in async support with Python's `asyncio` for handling 50 concurrent connections (SC-005).

### Rationale
- **Python asyncio**: Native async/await support, well-suited for I/O-bound MCP server operations
- **FastMCP Async Tools**: Framework supports async tool definitions with `async def`
- **Connection Pooling**: NSIPClient can be wrapped with connection pooling if needed
- **Performance**: Async I/O enables high concurrency without thread overhead

### Implementation Approach

**Async Tool Definitions**:
```python
@mcp.tool()
async def nsip_get_animal(search_string: str) -> dict:
    """Async MCP tool wrapper."""
    # NSIPClient operations can be wrapped in thread pool if synchronous
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _sync_get_animal, search_string)
    return result

def _sync_get_animal(search_string: str) -> dict:
    """Synchronous implementation."""
    client = NSIPClient()
    return client.get_animal_details(search_string)
```

**Connection Limits** (SC-005 requirement):
```python
# FastMCP handles connection management internally
# Monitor via health check endpoint (FR-014)
```

---

## Research Summary

All technical unknowns from Phase 0 have been resolved:

| Area | Decision | Rationale |
|------|----------|-----------|
| **MCP Framework** | FastMCP 2.0 | Leading Python MCP library, minimal boilerplate, production-ready |
| **Token Counting** | tiktoken (cl100k_base) | Official OpenAI library, accurate GPT-4 token counting |
| **Package Management** | uv/uvx | 10-100x faster than pip, unified tooling, modern standards |
| **Summarization** | Rule-based (FR-005a/FR-005b) | Deterministic, domain-specific, testable |
| **Transport** | Multi-transport (stdio/HTTP SSE/WebSocket) | MCP standard compliance, use case diversity |
| **Caching** | In-memory TTL cache | Simple, fast, specification-compliant |
| **Error Handling** | MCP-compliant structured errors | Enables LLM retry with corrections |
| **Concurrency** | Python asyncio + FastMCP async tools | Handles 50 concurrent connections efficiently |

All decisions align with constitutional principles (simplicity, testing, quality) and specification requirements. Ready to proceed to Phase 1 (design artifacts).
