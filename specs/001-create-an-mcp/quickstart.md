# Quickstart Guide: NSIP MCP Server

**Feature**: Context-Efficient API-to-MCP Gateway
**Branch**: `001-create-an-mcp`
**Date**: 2025-10-11
**Audience**: Developers integrating NSIP sheep breeding data with LLM applications

## Overview

The NSIP MCP Server exposes NSIP sheep breeding data through the Model Context Protocol (MCP), enabling LLM applications to query genetic information, lineage data, and trait evaluations in a context-efficient manner. The server automatically manages response sizes using intelligent summarization to prevent context window overflow.

**Key Features**:
- 🚀 9 MCP tools wrapping NSIP API operations
- 🔄 Automatic response summarization for large datasets (>2000 tokens)
- ⚡ In-memory caching with 1-hour TTL (40%+ cache hit rate)
- 🌐 Multiple transport options: stdio (CLI), HTTP SSE (web), WebSocket (real-time)
- 📊 Context-aware: Preserves key information while reducing token usage by 70%

---

## Installation

### Prerequisites

- **Python 3.8+** (check: `python --version`)
- **uv package manager** (install: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **Git** (for cloning repository)

### Install from GitHub Release

```bash
# Using uvx (recommended for tool execution)
uvx --from git+https://github.com/USERNAME/nsip-api-client@v1.0.0 nsip-mcp-server --help

# Or install locally with uv
uv pip install git+https://github.com/USERNAME/nsip-api-client@v1.0.0
```

### Install from Source (Development)

```bash
# Clone repository
git clone https://github.com/USERNAME/nsip-api-client.git
cd nsip-api-client

# Install dependencies
uv sync

# Run server
uv run nsip-mcp-server
```

---

## Quick Start

### 1. Start the MCP Server (stdio mode)

The default transport is **stdio** (standard input/output), ideal for CLI tools and MCP clients.

```bash
# Start server (stdio mode - default)
nsip-mcp-server

# Or with explicit transport
MCP_TRANSPORT=stdio nsip-mcp-server
```

The server will:
1. Initialize FastMCP server with 9 NSIP tools
2. Load tiktoken tokenizer for context management
3. Start in-memory cache with 1-hour TTL
4. Listen for MCP protocol messages on stdin

### 2. Connect an MCP Client

Use any MCP-compatible client (Claude Desktop, custom client, etc.):

**Example MCP Client Configuration** (for Claude Desktop):

```json
{
  "mcpServers": {
    "nsip": {
      "command": "nsip-mcp-server",
      "env": {
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

### 3. Discover Available Tools

Once connected, the LLM client will automatically discover 9 NSIP tools:

| Tool Name | Purpose | Returns Large Responses? |
|-----------|---------|-------------------------|
| `nsip_get_last_update` | Get database last updated timestamp | No |
| `nsip_list_breeds` | List available breed groups | No |
| `nsip_get_statuses` | Get status options for breed | No |
| `nsip_get_trait_ranges` | Get trait value ranges for breed | No |
| `nsip_search_animals` | Search animals by breed and traits | **Yes** (may be summarized) |
| `nsip_get_animal` | Get detailed animal information | **Yes** (may be summarized) |
| `nsip_get_lineage` | Get animal lineage/pedigree | **Yes** (may be summarized) |
| `nsip_get_progeny` | Get animal progeny list | **Yes** (may be summarized) |
| `nsip_search_by_lpn` | Comprehensive animal lookup | **Always summarized** |

### 4. Query NSIP Data

**Example 1: List Available Breeds**

```json
{
  "tool": "nsip_list_breeds",
  "input": {}
}
```

**Response**:
```json
{
  "breeds": [
    {"id": "merino", "name": "Merino"},
    {"id": "poll_dorset", "name": "Poll Dorset"},
    {"id": "white_suffolk", "name": "White Suffolk"}
  ]
}
```

**Example 2: Get Animal Details**

```json
{
  "tool": "nsip_get_animal",
  "input": {
    "search_string": "6####92020###249"
  }
}
```

**Response (if ≤2000 tokens - pass-through)**:
```json
{
  "LpnId": "6####92020###249",
  "Sire": "6####92018###123",
  "Dam": "6####92017###456",
  "Breed": "Merino",
  "TotalProgeny": 15,
  "Contact": {
    "phone": "+61 2 1234 5678",
    "email": "breeder@example.com",
    "farmName": "Example Farm"
  },
  "Traits": [
    {"name": "PWWT", "value": 165.2, "accuracy": 87.5},
    {"name": "PEMD", "value": -0.5, "accuracy": 82.3},
    // ... all traits included
  ]
}
```

**Response (if >2000 tokens - summarized)**:
```json
{
  "LpnId": "6####92020###249",
  "Sire": "6####92018###123",
  "Dam": "6####92017###456",
  "Breed": "Merino",
  "TotalProgeny": 15,
  "Contact": {
    "phone": "+61 2 1234 5678",
    "email": "breeder@example.com",
    "farmName": "Example Farm"
  },
  "TopTraits": [
    {"name": "PWWT", "value": 165.2, "accuracy": 87.5},
    {"name": "PEMD", "value": -0.5, "accuracy": 82.3},
    {"name": "PFAT", "value": 0.1, "accuracy": 75.1}
  ],
  "_summarized": true,
  "_original_token_count": 3500,
  "_summary_token_count": 1050
}
```

**Example 3: Search Animals by Trait**

```json
{
  "tool": "nsip_search_animals",
  "input": {
    "breed_id": "merino",
    "page": 1,
    "page_size": 20,
    "search_criteria": {
      "PWWT": ">150",
      "PEMD": "<0"
    }
  }
}
```

**Response**:
```json
{
  "animals": [
    {
      "LpnId": "6####92020###249",
      "Breed": "Merino",
      "PWWT": 165.2,
      "PEMD": -0.5
    },
    // ... more results
  ],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "totalResults": 127
  },
  "_summarized": false
}
```

---

## Advanced Configuration

### HTTP SSE Transport (for Web Applications)

```bash
# Start server on HTTP SSE transport
MCP_TRANSPORT=http-sse MCP_PORT=8000 nsip-mcp-server
```

**Client Connection**:
```javascript
const eventSource = new EventSource('http://localhost:8000/mcp');
eventSource.onmessage = (event) => {
  const response = JSON.parse(event.data);
  console.log('MCP response:', response);
};
```

### WebSocket Transport (for Real-Time Bidirectional Communication)

```bash
# Start server on WebSocket transport
MCP_TRANSPORT=websocket MCP_PORT=9000 nsip-mcp-server
```

**Client Connection**:
```python
import websockets
import asyncio

async def connect_mcp():
    async with websockets.connect('ws://localhost:9000/mcp') as ws:
        await ws.send(json.dumps({
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 1
        }))
        response = await ws.recv()
        print(response)

asyncio.run(connect_mcp())
```

### Environment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `MCP_TRANSPORT` | Transport mechanism | `stdio` | `http-sse`, `websocket` |
| `MCP_PORT` | Port for HTTP SSE/WebSocket | None (required for non-stdio) | `8000`, `9000` |
| `TIKTOKEN_CACHE_DIR` | Token cache directory | OS default | `/tmp/tiktoken` |
| `LOG_LEVEL` | Logging verbosity | `INFO` | `DEBUG`, `WARNING` |

### Caching Behavior

The server caches NSIP API responses with a **1-hour TTL** to reduce redundant calls:

**Cache Key Format**: `method_name:sorted_json_params`

**Example**:
```python
# First call - fetches from NSIP API
nsip_get_animal(search_string="6####92020###249")  # Cache miss

# Second call within 1 hour - returns cached response
nsip_get_animal(search_string="6####92020###249")  # Cache hit (fast)

# After 1 hour - fetches fresh data
nsip_get_animal(search_string="6####92020###249")  # Cache expired, miss
```

**Cache Metrics**:
- Target hit rate: **40%+** in typical usage
- Max cache size: **1000 entries**
- Eviction policy: **FIFO** (oldest entries removed first)

---

## Context Management (Automatic Summarization)

### How It Works

1. **Token Counting**: Every API response is measured using **tiktoken (cl100k_base)** tokenizer
2. **Threshold Check**: Compare token count to **2000-token threshold**
3. **Response Handling**:
   - **≤2000 tokens**: Pass through unmodified (FR-015)
   - **>2000 tokens**: Summarize to ~70% reduction (FR-005)

### Summarization Rules

**What's Preserved** (FR-005a):
- ✅ Unique identifiers (LpnId, Sire, Dam)
- ✅ Breed information
- ✅ Total counts (TotalProgeny)
- ✅ Contact information (all fields - phone, email, farm name)
- ✅ Top 3 traits by accuracy (accuracy ≥50%)

**What's Omitted** (FR-005b):
- ❌ Traits with accuracy <50%
- ❌ Redundant nested structures
- ❌ Detailed metadata (unless specifically requested)

### Detecting Summarized Responses

Check the `_summarized` field in responses:

```python
if response.get("_summarized"):
    print(f"Response was summarized from {response['_original_token_count']} "
          f"to {response['_summary_token_count']} tokens")
    print(f"Reduction: {((response['_original_token_count'] - response['_summary_token_count']) / response['_original_token_count'] * 100):.1f}%")
```

---

## Error Handling

### Structured Error Responses

All errors follow **JSON-RPC 2.0** standard with additional context for LLM retry:

**Error Response Format**:
```json
{
  "error": {
    "code": -32602,
    "message": "Invalid parameter: lpn_id",
    "data": {
      "parameter": "lpn_id",
      "value": "123",
      "expected": "Non-empty string with at least 5 characters",
      "suggestion": "Provide a valid LPN ID like '6####92020###249'"
    }
  }
}
```

### Common Error Codes

| Code | Name | Meaning | Suggested Action |
|------|------|---------|------------------|
| `-32602` | INVALID_PARAMS | Invalid parameters | Check `error.data.suggestion` for correction |
| `-32000` | NSIP_API_ERROR | NSIP API call failed | Verify NSIP API availability |
| `-32001` | CACHE_ERROR | Cache operation failed | Retry without cache |
| `-32002` | SUMMARIZATION_ERROR | Summarization failed | Request smaller dataset or paginate |

**Example Error Handling** (Python MCP Client):
```python
try:
    result = await mcp_client.call_tool("nsip_get_animal", {"search_string": "123"})
except McpError as e:
    if e.code == -32602:  # INVALID_PARAMS
        print(f"Parameter error: {e.data['suggestion']}")
        # Retry with corrected parameters
        result = await mcp_client.call_tool("nsip_get_animal", {"search_string": "6####92020###249"})
```

---

## Testing the Server

### Health Check

```bash
# Check if server is running (HTTP SSE/WebSocket only)
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "uptime_seconds": 1234,
  "cache_hit_rate": 42.5,
  "active_connections": 3
}
```

### Tool Discovery Test

**Request** (JSON-RPC 2.0 via stdio):
```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "id": 1
}
```

**Expected Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "tools": [
      {
        "name": "nsip_get_last_update",
        "description": "Get the date when NSIP database was last updated..."
      },
      {
        "name": "nsip_list_breeds",
        "description": "List all available sheep breed groups..."
      },
      // ... 7 more tools
    ]
  },
  "id": 1
}
```

### Summarization Test

```bash
# Generate a large response (>2000 tokens) to test summarization
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"nsip_search_by_lpn","arguments":{"lpn_id":"6####92020###249"}},"id":2}' | nsip-mcp-server
```

**Expected**: Response includes `"_summarized": true` with token count metadata.

---

## Performance Targets

The server is designed to meet these success criteria:

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Tool Discovery** | <5 seconds | Time from connection to tool list returned |
| **Summarization** | 70% token reduction | Original tokens vs summary tokens |
| **Validation** | 95% caught before API | Invalid requests rejected at MCP layer |
| **Concurrent Connections** | 50+ without degradation | Load testing with multiple clients |
| **Cache Hit Rate** | 40%+ | Cache hits / (hits + misses) |
| **Startup Time** | <3 seconds | Process start to ready state |

---

## Troubleshooting

### Server Won't Start

**Problem**: `ModuleNotFoundError: No module named 'fastmcp'`

**Solution**:
```bash
uv sync  # Ensure dependencies installed
uv run nsip-mcp-server  # Run with uv
```

---

### Connection Refused (HTTP SSE/WebSocket)

**Problem**: `Connection refused to localhost:8000`

**Solution**:
```bash
# Check if server is running
ps aux | grep nsip-mcp-server

# Verify transport and port
MCP_TRANSPORT=http-sse MCP_PORT=8000 nsip-mcp-server
```

---

### Responses Not Summarized

**Problem**: Large responses (>2000 tokens) not being summarized

**Solution**:
```bash
# Check tiktoken is installed
uv pip list | grep tiktoken

# Enable debug logging
LOG_LEVEL=DEBUG nsip-mcp-server
```

**Expected Log**:
```
DEBUG: Response token count: 3500 (threshold: 2000)
DEBUG: Applying summarization (FR-005)
DEBUG: Summary token count: 1050 (70.0% reduction)
```

---

### Cache Not Working

**Problem**: Every request hits NSIP API (no cache hits)

**Solution**:
1. Check cache key generation:
   ```python
   # Cache keys are deterministic based on method + params
   # Same params = same cache key
   ```

2. Verify TTL hasn't expired (default: 1 hour)

3. Check cache metrics in logs:
   ```
   INFO: Cache hit rate: 42.5% (hits: 85, misses: 115)
   ```

---

## Next Steps

- **Integrate with LLM Application**: Add NSIP MCP server to your MCP client configuration
- **Explore Advanced Queries**: Use `nsip_search_animals` with complex trait filters
- **Monitor Performance**: Track cache hit rates and summarization effectiveness
- **Report Issues**: Submit bugs or feature requests to GitHub repository

---

## Additional Resources

- **MCP Specification**: https://modelcontextprotocol.io/specification
- **FastMCP Documentation**: https://gofastmcp.com
- **tiktoken Documentation**: https://github.com/openai/tiktoken
- **NSIP API Client Source**: See `src/nsip_client/` in repository

---

## License & Distribution

**Important**: This project is distributed exclusively via **GitHub Releases** (not PyPI). See README.md for licensing details.

**Installation from GitHub**:
```bash
# Install specific version
uvx --from git+https://github.com/USERNAME/nsip-api-client@v1.0.0 nsip-mcp-server

# Install latest
uvx --from git+https://github.com/USERNAME/nsip-api-client@main nsip-mcp-server
```
