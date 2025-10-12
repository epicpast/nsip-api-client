# NSIP MCP Server Documentation

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Available Tools](#available-tools)
5. [Transport Configuration](#transport-configuration)
6. [Environment Variables](#environment-variables)
7. [Context Management](#context-management)
8. [Caching](#caching)
9. [Error Handling](#error-handling)
10. [Performance Metrics](#performance-metrics)
11. [Advanced Usage](#advanced-usage)
12. [Troubleshooting](#troubleshooting)
13. [API Reference](#api-reference)

---

## Overview

The NSIP MCP Server is a Model Context Protocol (MCP) implementation that provides LLM applications with structured access to the National Sheep Improvement Program (NSIP) breeding data. Built on FastMCP 2.0, it offers intelligent context management, caching, and multiple transport options for seamless integration with AI assistants.

### Key Features

- **9 MCP Tools**: Complete access to NSIP API operations
- **Context Management**: Automatic response summarization to prevent context overflow (70% token reduction)
- **Smart Caching**: 1-hour TTL cache with 40%+ hit rate target
- **Multiple Transports**: stdio (CLI), HTTP SSE (web), WebSocket (real-time)
- **Performance Optimized**: <3s startup, <5s tool discovery
- **Structured Errors**: JSON-RPC 2.0 compliant with LLM-friendly suggestions
- **Health Monitoring**: Built-in metrics and success criteria tracking

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      MCP Client (LLM)                       │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    NSIP MCP Server                          │
│  ┌────────────────────────────────────────────────────┐     │
│  │  FastMCP 2.0 Framework                             │     │
│  │  - Tool Registration                               │     │
│  │  - Transport Management (stdio/HTTP SSE/WebSocket) │     │
│  │  - JSON-RPC 2.0 Protocol                           │     │
│  └────────────────────────────────────────────────────┘     │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Context Management Layer                          │     │
│  │  - Token counting (tiktoken)                       │     │
│  │  - Automatic summarization (>2000 tokens)          │     │
│  │  - Metadata tracking                               │     │
│  └────────────────────────────────────────────────────┘     │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Caching Layer                                     │     │
│  │  - 1-hour TTL                                      │     │
│  │  - Key generation from method + params             │     │
│  │  - FIFO eviction (1000 max entries)                │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  NSIP API Client                            │
│  - HTTP client wrapper for NSIP Search API                  │
│  - Data model transformations                               │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              NSIP Search API (nsipsearch.nsip.org)          │
└─────────────────────────────────────────────────────────────┘
```

---

## Installation

### Prerequisites

- Python 3.10 or higher
- pip or uvx package manager

### Method 1: Install via pip from GitHub

**Install latest version:**
```bash
pip install git+https://github.com/epicpast/nsip-api-client.git
```

**Install specific version:**
```bash
pip install git+https://github.com/epicpast/nsip-api-client.git@v1.1.0
```

### Method 2: Install via uvx (no installation required)

**Run directly with uvx:**
```bash
uvx --from git+https://github.com/epicpast/nsip-api-client@v1.1.0 nsip-mcp-server
```

### Method 3: From source

```bash
git clone https://github.com/epicpast/nsip-api-client.git
cd nsip-api-client
pip install -e .
```

### Verify Installation

```bash
nsip-mcp-server --version
# Or check if command is available:
which nsip-mcp-server
```

---

## Quick Start

### 1. Basic stdio Usage

The default transport is stdio (standard input/output), perfect for integration with MCP clients like Claude Desktop.

```bash
nsip-mcp-server
# Server starts and waits for JSON-RPC 2.0 messages on stdin
```

### 2. Claude Desktop Configuration

Add the following to your Claude Desktop configuration file:

**Location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Configuration:**
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

**Using uvx (no installation):**
```json
{
  "mcpServers": {
    "nsip": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/epicpast/nsip-api-client@v1.1.0",
        "nsip-mcp-server"
      ],
      "env": {
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

### 3. First Tool Call Examples

Once configured in Claude Desktop, you can use the NSIP tools naturally:

**Example 1: Get breed list**
```
"What breeds are available in NSIP?"
```

**Example 2: Search for animals**
```
"Find Katahdin sheep with good weaning weight traits"
```

**Example 3: Get animal details**
```
"Give me details about sheep 6####92020###249"
```

---

## Available Tools

The NSIP MCP Server provides 10 tools (9 NSIP API operations + 1 health check):

### Tool Summary Table

| Tool Name | Description | Parameters | May Be Summarized |
|-----------|-------------|------------|-------------------|
| `nsip_get_last_update` | Get database last update timestamp | None | No |
| `nsip_list_breeds` | List available breed groups | None | No |
| `nsip_get_statuses` | Get animal status options | None | No |
| `nsip_get_trait_ranges` | Get trait ranges for a breed | `breed_id` (int) | No |
| `nsip_search_animals` | Search animals by criteria | `page`, `page_size`, `breed_id`, `sorted_trait`, `reverse`, `search_criteria` | Yes (if >2000 tokens) |
| `nsip_get_animal` | Get detailed animal information | `search_string` (str) | Yes (if >2000 tokens) |
| `nsip_get_lineage` | Get animal lineage/pedigree | `lpn_id` (str) | Yes (if >2000 tokens) |
| `nsip_get_progeny` | Get animal progeny (offspring) | `lpn_id` (str), `page`, `page_size` | Yes (if >2000 tokens) |
| `nsip_search_by_lpn` | Complete animal profile | `lpn_id` (str) | Always |
| `get_server_health` | Get server health metrics | None | No |

---

### Detailed Tool Reference

#### 1. nsip_get_last_update

Get the timestamp of the last database update.

**Parameters:** None

**Returns:**
```json
{
  "date": "09/23/2025"
}
```

**Example Usage:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "nsip_get_last_update",
    "arguments": {}
  },
  "id": 1
}
```

---

#### 2. nsip_list_breeds

Get list of available breed groups in the NSIP database.

**Parameters:** None

**Returns:**
```json
[
  {"id": 61, "name": "Range"},
  {"id": 62, "name": "Maternal Wool"},
  {"id": 64, "name": "Hair"},
  {"id": 69, "name": "Terminal"}
]
```

**Example Usage:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "nsip_list_breeds",
    "arguments": {}
  },
  "id": 2
}
```

---

#### 3. nsip_get_statuses

Get available animal status values.

**Parameters:** None

**Returns:**
```json
["CURRENT", "SOLD", "DEAD", "COMMERCIAL", "CULL", "EXPORTED"]
```

**Example Usage:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "nsip_get_statuses",
    "arguments": {}
  },
  "id": 3
}
```

---

#### 4. nsip_get_trait_ranges

Get trait value ranges (min/max) for a specific breed.

**Parameters:**
- `breed_id` (int, required): The breed ID (use `nsip_list_breeds` to find IDs)

**Returns:**
```json
{
  "BWT": {"min": -0.713, "max": 0.956},
  "WWT": {"min": -1.234, "max": 2.456},
  "YWT": {"min": -2.1, "max": 5.8},
  "NLB": {"min": -0.15, "max": 0.35}
}
```

**Example Usage:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "nsip_get_trait_ranges",
    "arguments": {
      "breed_id": 486
    }
  },
  "id": 4
}
```

**Error Example:**
```json
{
  "error": {
    "code": -32602,
    "message": "Invalid parameter: breed_id",
    "data": {
      "parameter": "breed_id",
      "value": -5,
      "expected": "Positive integer",
      "suggestion": "Provide a valid breed_id (e.g., 486 for Katahdin)"
    }
  }
}
```

---

#### 5. nsip_search_animals

Search for animals based on breed, traits, and other criteria with pagination.

**Parameters:**
- `page` (int, optional): Page number (0-indexed, default: 0)
- `page_size` (int, optional): Results per page (1-100, default: 15)
- `breed_id` (int, optional): Filter by breed ID
- `sorted_trait` (str, optional): Trait code to sort by (e.g., "BWT", "WWT")
- `reverse` (bool, optional): Sort in reverse order
- `search_criteria` (dict, optional): Additional filters

**Returns:**
```json
{
  "results": [
    {
      "LpnId": "6####92020###249",
      "Breed": "Katahdin",
      "Gender": "Female",
      "DateOfBirth": "2/5/2020",
      "Status": "CURRENT"
    }
  ],
  "total_count": 1523,
  "page": 0,
  "page_size": 15,
  "_summarized": false,
  "_original_token_count": 892
}
```

**Example Usage:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "nsip_search_animals",
    "arguments": {
      "breed_id": 486,
      "page": 0,
      "page_size": 15,
      "sorted_trait": "WWT",
      "reverse": true
    }
  },
  "id": 5
}
```

---

#### 6. nsip_get_animal

Get detailed information about a specific animal including traits, EBVs, and contact information.

**Parameters:**
- `search_string` (str, required): LPN ID or registration number (minimum 5 characters)

**Returns:**

**Small response (≤2000 tokens):**
```json
{
  "lpn_id": "6####92020###249",
  "breed": "Katahdin",
  "gender": "Female",
  "date_of_birth": "2/5/2020",
  "sire": "6####92019###124",
  "dam": "6####92018###035",
  "traits": {
    "BWT": {"value": 0.246, "accuracy": 0.74},
    "WWT": {"value": 3.051, "accuracy": 0.71}
  },
  "_summarized": false,
  "_original_token_count": 1200
}
```

**Large response (>2000 tokens, automatically summarized):**
```json
{
  "lpn_id": "6####92020###249",
  "breed": "Katahdin",
  "sire": "6####92019###124",
  "dam": "6####92018###035",
  "total_progeny": 6,
  "contact": {
    "farm_name": "<redacted>",
    "contact_name": "<redacted>",
    "phone": "<redacted>",
    "email": "<redacted>"
  },
  "top_traits": [
    {"trait": "WWT", "value": 3.051, "accuracy": 0.71},
    {"trait": "BWT", "value": 0.246, "accuracy": 0.74},
    {"trait": "YWT", "value": 5.123, "accuracy": 0.68}
  ],
  "_summarized": true,
  "_original_token_count": 3500,
  "_summary_token_count": 1050,
  "_reduction_percent": 70.0
}
```

**Example Usage:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "nsip_get_animal",
    "arguments": {
      "search_string": "6####92020###249"
    }
  },
  "id": 6
}
```

---

#### 7. nsip_get_lineage

Get the lineage/pedigree tree for an animal.

**Parameters:**
- `lpn_id` (str, required): The LPN ID of the animal (minimum 5 characters)

**Returns:**
```json
{
  "sire": {
    "lpn_id": "6####92019###124",
    "breed": "Katahdin"
  },
  "dam": {
    "lpn_id": "6####92018###035",
    "breed": "Katahdin"
  },
  "_summarized": true,
  "_original_token_count": 2500,
  "_summary_token_count": 720,
  "_reduction_percent": 71.20
}
```

**Example Usage:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "nsip_get_lineage",
    "arguments": {
      "lpn_id": "6####92020###249"
    }
  },
  "id": 7
}
```

---

#### 8. nsip_get_progeny

Get progeny (offspring) records for a parent animal with pagination.

**Parameters:**
- `lpn_id` (str, required): The LPN ID of the parent animal
- `page` (int, optional): Page number (0-indexed, default: 0)
- `page_size` (int, optional): Results per page (1-100, default: 10)

**Returns:**
```json
{
  "animals": [
    {
      "lpn_id": "6####92021###301",
      "breed": "Katahdin",
      "gender": "Male",
      "date_of_birth": "3/12/2021"
    }
  ],
  "total_count": 6,
  "page": 0,
  "page_size": 10,
  "_summarized": false,
  "_original_token_count": 1800
}
```

**Example Usage:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "nsip_get_progeny",
    "arguments": {
      "lpn_id": "6####92020###249",
      "page": 0,
      "page_size": 10
    }
  },
  "id": 8
}
```

---

#### 9. nsip_search_by_lpn

Get complete animal profile (details + lineage + progeny) in a single call.

**Important:** This tool ALWAYS returns a summarized response due to the combined data size.

**Parameters:**
- `lpn_id` (str, required): The LPN ID to search for

**Returns:**
```json
{
  "lpn_id": "6####92020###249",
  "breed": "Katahdin",
  "sire": "6####92019###124",
  "dam": "6####92018###035",
  "total_progeny": 6,
  "top_traits": [
    {"trait": "WWT", "value": 3.051, "accuracy": 0.71},
    {"trait": "BWT", "value": 0.246, "accuracy": 0.74},
    {"trait": "YWT", "value": 5.123, "accuracy": 0.68}
  ],
  "_summarized": true,
  "_original_token_count": 5200,
  "_summary_token_count": 1100,
  "_reduction_percent": 78.85
}
```

**Example Usage:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "nsip_search_by_lpn",
    "arguments": {
      "lpn_id": "6####92020###249"
    }
  },
  "id": 9
}
```

---

#### 10. get_server_health

Get server health status and performance metrics.

**Parameters:** None

**Returns:**
```json
{
  "startup_time_seconds": 0.245,
  "discovery_times": {
    "avg_seconds": 2.3,
    "target_seconds": 5.0
  },
  "summarization": {
    "avg_reduction_percent": 72.5,
    "target_percent": 70.0
  },
  "validation": {
    "success_rate_percent": 96.8,
    "target_percent": 95.0,
    "total_validations": 1250,
    "successful": 1210,
    "failed": 40
  },
  "cache": {
    "hit_rate_percent": 43.2,
    "target_percent": 40.0,
    "total_requests": 5000,
    "hits": 2160,
    "misses": 2840
  },
  "connections": {
    "current": 5,
    "peak": 52,
    "target": 50
  },
  "success_criteria": {
    "SC-001 Discovery <5s": true,
    "SC-002 Summarization >=70%": true,
    "SC-003 Validation >=95%": true,
    "SC-006 Cache Hit >=40%": true,
    "SC-007 Startup <3s": true
  }
}
```

**Example Usage:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "get_server_health",
    "arguments": {}
  },
  "id": 10
}
```

---

## Transport Configuration

The NSIP MCP Server supports three transport mechanisms for different integration scenarios:

### 1. stdio (Standard Input/Output) - Default

**Use Case:** MCP clients like Claude Desktop, terminal applications

**Configuration:**
```bash
# Explicit stdio mode
MCP_TRANSPORT=stdio nsip-mcp-server

# Or simply (stdio is default):
nsip-mcp-server
```

**Protocol:**
- JSON-RPC 2.0 messages over stdin/stdout
- One message per line
- Binary-safe (newline-delimited JSON)

**Example Message Flow:**
```
→ {"jsonrpc":"2.0","method":"tools/list","id":1}
← {"jsonrpc":"2.0","result":{"tools":[...]},"id":1}
```

---

### 2. HTTP SSE (Server-Sent Events)

**Use Case:** Web applications, browser-based clients, HTTP-only environments

**Configuration:**
```bash
MCP_TRANSPORT=http-sse MCP_PORT=8000 nsip-mcp-server
```

**Endpoints:**
- `POST /messages` - Send JSON-RPC requests
- `GET /sse` - Subscribe to server-sent events
- `GET /health` - Health check endpoint

**Example Usage:**
```bash
# Start server
MCP_TRANSPORT=http-sse MCP_PORT=8000 nsip-mcp-server

# In another terminal:
curl -X POST http://localhost:8000/messages \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'

# Health check
curl http://localhost:8000/health
```

**CORS Configuration:**
HTTP SSE transport includes CORS headers for browser access:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

---

### 3. WebSocket

**Use Case:** Real-time bidirectional communication, persistent connections, low-latency applications

**Configuration:**
```bash
MCP_TRANSPORT=websocket MCP_PORT=9000 nsip-mcp-server
```

**WebSocket URL:**
```
ws://localhost:9000/ws
```

**Example Usage:**
```bash
# Start server
MCP_TRANSPORT=websocket MCP_PORT=9000 nsip-mcp-server

# Connect with wscat (install: npm install -g wscat)
wscat -c ws://localhost:9000/ws

# Send JSON-RPC message:
> {"jsonrpc":"2.0","method":"tools/list","id":1}
< {"jsonrpc":"2.0","result":{"tools":[...]},"id":1}
```

**Python Client Example:**
```python
import asyncio
import websockets
import json

async def call_tool():
    uri = "ws://localhost:9000/ws"
    async with websockets.connect(uri) as websocket:
        # Send request
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "nsip_get_animal",
                "arguments": {"search_string": "6####92020###249"}
            },
            "id": 1
        }
        await websocket.send(json.dumps(request))

        # Receive response
        response = await websocket.recv()
        print(json.loads(response))

asyncio.run(call_tool())
```

---

## Environment Variables

Configure the NSIP MCP Server using these environment variables:

| Variable | Description | Default | Valid Values | Required |
|----------|-------------|---------|--------------|----------|
| `MCP_TRANSPORT` | Transport mechanism | `stdio` | `stdio`, `http-sse`, `websocket` | No |
| `MCP_PORT` | Port for HTTP SSE/WebSocket | None | 1024-65535 | Yes (for non-stdio) |
| `MCP_HOST` | Host address to bind to | `0.0.0.0` | Valid IP/hostname | No |
| `TIKTOKEN_CACHE_DIR` | Token cache directory | OS default | Valid path | No |
| `LOG_LEVEL` | Logging verbosity | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` | No |

### Configuration Examples

**Example 1: Default stdio mode**
```bash
nsip-mcp-server
```

**Example 2: HTTP SSE on port 8000**
```bash
export MCP_TRANSPORT=http-sse
export MCP_PORT=8000
nsip-mcp-server
```

**Example 3: WebSocket with debug logging**
```bash
MCP_TRANSPORT=websocket \
MCP_PORT=9000 \
LOG_LEVEL=DEBUG \
nsip-mcp-server
```

**Example 4: Docker with environment file**
```bash
# .env file
MCP_TRANSPORT=http-sse
MCP_PORT=8000
MCP_HOST=0.0.0.0
LOG_LEVEL=INFO

# Run with environment file
docker run --env-file .env nsip-mcp-server
```

---

## Context Management

The NSIP MCP Server implements intelligent context management to prevent LLM context window overflow using automatic response summarization.

### How It Works

1. **Token Counting**: Every response is measured using the GPT-4 tokenizer (cl100k_base)
2. **Threshold Check**: Responses >2000 tokens are flagged for summarization
3. **Smart Summarization**: Large responses are condensed while preserving critical information
4. **Metadata Tracking**: All responses include summarization metadata

### Token Threshold

```
Response Size         Action
──────────────────────────────────
≤2000 tokens     →   Pass-through (unmodified)
>2000 tokens     →   Automatic summarization
```

### What's Preserved in Summaries

The summarizer keeps the most important information:

- **Identity**: LPN ID, breed, registration info
- **Pedigree**: Sire and dam LPN IDs
- **Progeny**: Total count (not full list)
- **Contact**: Complete breeder contact information
- **Top Traits**: Best 3 traits by accuracy (≥50% accuracy only)

### What's Omitted

To achieve 70% token reduction:

- Low-accuracy traits (accuracy <50%)
- Verbose metadata and registration details
- Full progeny lists (count preserved)
- Duplicate or redundant information

### Summarization Example

**Original Response (3500 tokens):**
```json
{
  "lpn_id": "6####92020###249",
  "breed": "Katahdin",
  "gender": "Female",
  "date_of_birth": "2/5/2020",
  "status": "CURRENT",
  "sire": "6####92019###124",
  "dam": "6####92018###035",
  "traits": {
    "BWT": {"value": 0.246, "accuracy": 0.74},
    "WWT": {"value": 3.051, "accuracy": 0.71},
    "YWT": {"value": 5.123, "accuracy": 0.68},
    "PFAT": {"value": 0.12, "accuracy": 0.35},
    "PEMD": {"value": 0.45, "accuracy": 0.42},
    "... 20+ more traits ..."
  },
  "progeny": {
    "animals": ["... full list of 6 offspring ..."],
    "total_count": 6
  },
  "contact": {
    "farm_name": "[FARM_NAME]",
    "contact_name": "[OWNER_NAME]",
    "phone": "[PHONE_NUMBER]",
    "email": "[EMAIL_ADDRESS]"
  },
  "... extensive metadata ..."
}
```

**Summarized Response (1050 tokens, 70% reduction):**
```json
{
  "lpn_id": "6####92020###249",
  "breed": "Katahdin",
  "sire": "6####92019###124",
  "dam": "6####92018###035",
  "total_progeny": 6,
  "contact": {
    "farm_name": "[FARM_NAME]",
    "contact_name": "[OWNER_NAME]",
    "phone": "[PHONE_NUMBER]",
    "email": "[EMAIL_ADDRESS]"
  },
  "top_traits": [
    {"trait": "BWT", "value": 0.246, "accuracy": 0.74},
    {"trait": "WWT", "value": 3.051, "accuracy": 0.71},
    {"trait": "YWT", "value": 5.123, "accuracy": 0.68}
  ],
  "_summarized": true,
  "_original_token_count": 3500,
  "_summary_token_count": 1050,
  "_reduction_percent": 70.0
}
```

### Metadata Fields

All responses include these metadata fields:

| Field | Description | Example |
|-------|-------------|---------|
| `_summarized` | Whether response was summarized | `true` or `false` |
| `_original_token_count` | Tokens in original response | `3500` |
| `_summary_token_count` | Tokens after summarization | `1050` |
| `_reduction_percent` | Percentage reduction achieved | `70.0` |

### Force Summarization

Some tools ALWAYS summarize regardless of size:

- `nsip_search_by_lpn`: Combines details + lineage + progeny (always large)

### Summarization Failure Handling

If summarization fails, the server falls back to pass-through mode with additional metadata:

```json
{
  "... original response data ...",
  "_summarization_failed": true,
  "_summarization_error": "Error message here"
}
```

---

## Caching

The NSIP MCP Server includes a smart caching layer to reduce API calls and improve response times.

### Cache Configuration

- **TTL (Time To Live)**: 1 hour (3600 seconds)
- **Max Entries**: 1000
- **Eviction Policy**: FIFO (First In, First Out)
- **Target Hit Rate**: 40%+ in typical usage

### How Caching Works

1. **Cache Key Generation**: `method_name:sorted_json_params`
2. **Cache Lookup**: Check cache before API call
3. **Cache Hit**: Return cached result immediately
4. **Cache Miss**: Call API, store result, return to client
5. **Cache Expiration**: Entries older than 1 hour are invalidated

### Cache Key Examples

```python
# Example 1: Get animal details
method = "get_animal_details"
params = {"search_string": "6####92020###249"}
cache_key = "get_animal_details:{'search_string':'6####92020###249'}"

# Example 2: Search animals
method = "search_animals"
params = {"breed_id": 486, "page": 0, "page_size": 15}
cache_key = "search_animals:{'breed_id':486,'page':0,'page_size':15}"
```

### Cache Performance

**First call (cache miss):**
```
Request: nsip_get_animal("6####92020###249")
Cache: MISS
API Call: 250ms
Total: 250ms
```

**Second call within 1 hour (cache hit):**
```
Request: nsip_get_animal("6####92020###249")
Cache: HIT
API Call: 0ms (skipped)
Total: <1ms
```

**After 1 hour (cache expired):**
```
Request: nsip_get_animal("6####92020###249")
Cache: MISS (expired)
API Call: 250ms
Total: 250ms
```

### What Gets Cached

All MCP tool responses are cached:

- ✅ Breed lists (rarely changes)
- ✅ Animal details (1-hour freshness acceptable)
- ✅ Lineage data (immutable after birth)
- ✅ Progeny lists (updates infrequently)
- ✅ Trait ranges (changes rarely)
- ✅ Search results (pagination cached per page)

### Cache Metrics

Check cache performance with `get_server_health`:

```json
{
  "cache": {
    "hit_rate_percent": 43.2,
    "target_percent": 40.0,
    "total_requests": 5000,
    "hits": 2160,
    "misses": 2840,
    "size": 234,
    "max_size": 1000
  }
}
```

### Cache Invalidation

The cache automatically invalidates entries:

- After 1 hour (TTL expiration)
- When max size reached (oldest removed first)
- On server restart (in-memory cache)

There is no manual cache invalidation API. If you need fresh data immediately, restart the server or wait for TTL expiration.

---

## Error Handling

The NSIP MCP Server provides structured, LLM-friendly error responses following JSON-RPC 2.0 specification.

### Error Response Format

All errors follow this structure:

```json
{
  "error": {
    "code": -32602,
    "message": "Human-readable error description",
    "data": {
      "parameter": "affected_parameter",
      "value": "invalid_value",
      "expected": "what_was_expected",
      "suggestion": "helpful suggestion for LLM"
    }
  }
}
```

### Error Codes

| Code | Name | Description | Example |
|------|------|-------------|---------|
| `-32700` | Parse error | Invalid JSON | Malformed JSON request |
| `-32600` | Invalid Request | Invalid JSON-RPC 2.0 | Missing required fields |
| `-32601` | Method not found | Unknown tool name | Calling non-existent tool |
| `-32602` | Invalid params | Parameter validation failed | Invalid LPN ID format |
| `-32603` | Internal error | Server-side error | Unhandled exception |
| `-32000` | NSIP API error | Error from NSIP API | API timeout or failure |
| `-32001` | Cache error | Cache operation failed | Cache corruption |
| `-32002` | Summarization error | Summarization failed | Unable to summarize response |

### Common Error Examples

#### 1. Invalid LPN ID

```json
{
  "error": {
    "code": -32602,
    "message": "Invalid parameter: search_string",
    "data": {
      "parameter": "search_string",
      "value": "123",
      "expected": "Non-empty string with at least 5 characters",
      "suggestion": "Provide a valid LPN ID like '6####92020###249'"
    }
  }
}
```

#### 2. Invalid Breed ID

```json
{
  "error": {
    "code": -32602,
    "message": "Invalid parameter: breed_id",
    "data": {
      "parameter": "breed_id",
      "value": -5,
      "expected": "Positive integer",
      "suggestion": "Provide a valid breed_id (e.g., 486 for Katahdin)"
    }
  }
}
```

#### 3. Invalid Pagination

```json
{
  "error": {
    "code": -32602,
    "message": "Invalid parameter: page_size",
    "data": {
      "parameter": "page_size",
      "value": 150,
      "expected": "Integer between 1 and 100",
      "suggestion": "Use page_size between 1-100 (e.g., 15), not 150"
    }
  }
}
```

#### 4. Animal Not Found

```json
{
  "error": {
    "code": -32000,
    "message": "Animal not found: getting animal details for 'INVALID123'",
    "data": {
      "original_error": "NSIPNotFoundError: Animal not found",
      "suggestion": "Verify the LPN ID is correct and animal exists in NSIP database"
    }
  }
}
```

#### 5. NSIP API Timeout

```json
{
  "error": {
    "code": -32000,
    "message": "NSIP API timeout: searching animals",
    "data": {
      "original_error": "NSIPTimeoutError: Request timed out after 30s",
      "suggestion": "Try again or check NSIP API status at http://nsipsearch.nsip.org"
    }
  }
}
```

### Parameter Validation

The server performs parameter validation BEFORE making API calls:

**Validation Success Rate Target:** ≥95%

**What Gets Validated:**
- ✅ LPN ID format (minimum 5 characters)
- ✅ Breed ID positive integer
- ✅ Page numbers non-negative
- ✅ Page size between 1-100
- ✅ Required parameters present

**Validation Example:**
```python
# Valid call
nsip_get_animal(search_string="6####92020###249")  # ✅

# Invalid call (caught before API)
nsip_get_animal(search_string="123")  # ❌ Too short
```

### Error Recovery Strategies

**For LLMs:**
1. Parse the `suggestion` field for guidance
2. Correct the parameter based on `expected` value
3. Retry with corrected parameters

**For Developers:**
1. Check `error.data` for detailed information
2. Implement retry logic for transient errors (timeout)
3. Use health endpoint to diagnose persistent issues

---

## Performance Metrics

The NSIP MCP Server tracks comprehensive performance metrics to ensure it meets design targets.

### Success Criteria

The server is designed to meet these performance targets:

| ID | Criterion | Target | Description |
|----|-----------|--------|-------------|
| SC-001 | Tool Discovery | <5 seconds | Time from connection to tools/list response |
| SC-002 | Summarization | ≥70% reduction | Token reduction percentage for summaries |
| SC-003 | Validation | ≥95% success | Validation catch rate before API calls |
| SC-004 | Reliability | ≥99.9% uptime | (Not tracked in health endpoint) |
| SC-005 | Concurrency | 50+ connections | Concurrent connections without degradation |
| SC-006 | Cache Hit Rate | ≥40% | Cache hit rate in typical usage |
| SC-007 | Startup Time | <3 seconds | Time from launch to ready state |
| SC-008-012 | (See health endpoint) | Various | Additional metrics |

### Health Endpoint

Use `get_server_health` tool or HTTP endpoint to check metrics:

**Tool Call:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "get_server_health",
    "arguments": {}
  },
  "id": 1
}
```

**HTTP Endpoint (HTTP SSE/WebSocket only):**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "startup_time_seconds": 0.245,
  "discovery_times": {
    "avg_seconds": 2.3,
    "target_seconds": 5.0,
    "samples": 150
  },
  "summarization": {
    "avg_reduction_percent": 72.5,
    "target_percent": 70.0,
    "total_summarizations": 425,
    "successful": 423,
    "failed": 2
  },
  "validation": {
    "success_rate_percent": 96.8,
    "target_percent": 95.0,
    "total_validations": 1250,
    "successful": 1210,
    "failed": 40
  },
  "cache": {
    "hit_rate_percent": 43.2,
    "target_percent": 40.0,
    "total_requests": 5000,
    "hits": 2160,
    "misses": 2840,
    "size": 234,
    "max_size": 1000
  },
  "connections": {
    "current": 5,
    "peak": 52,
    "target": 50
  },
  "success_criteria": {
    "SC-001 Discovery <5s": true,
    "SC-002 Summarization >=70%": true,
    "SC-003 Validation >=95%": true,
    "SC-006 Cache Hit >=40%": true,
    "SC-007 Startup <3s": true,
    "SC-005 Concurrent 50+": true
  }
}
```

### Interpreting Metrics

**Startup Time:**
- ✅ Good: <2 seconds
- ⚠️ Acceptable: 2-3 seconds
- ❌ Slow: >3 seconds (check dependencies)

**Discovery Time:**
- ✅ Good: <3 seconds
- ⚠️ Acceptable: 3-5 seconds
- ❌ Slow: >5 seconds (check tool registration)

**Summarization Reduction:**
- ✅ Good: ≥70%
- ⚠️ Acceptable: 60-70%
- ❌ Poor: <60% (review summarization logic)

**Validation Success Rate:**
- ✅ Good: ≥95%
- ⚠️ Acceptable: 90-95%
- ❌ Poor: <90% (improve validation)

**Cache Hit Rate:**
- ✅ Good: ≥40%
- ⚠️ Acceptable: 30-40%
- ❌ Poor: <30% (review TTL or usage patterns)

### Performance Monitoring

**Monitor these metrics regularly:**

1. **Startup time**: Ensures fast server initialization
2. **Cache hit rate**: Indicates effective caching
3. **Validation success**: Catches errors early
4. **Summarization reduction**: Manages context efficiently
5. **Connection count**: Tracks load

**Red flags:**
- Startup time increasing over time
- Cache hit rate dropping suddenly
- High validation failure rate
- Summarization reduction below 70%
- Connection count approaching 50

---

## Advanced Usage

### Multiple Concurrent Connections

The server supports 50+ concurrent connections without performance degradation.

**Load Testing Example:**
```python
import asyncio
import aiohttp

async def call_tool(session, animal_id):
    async with session.post('http://localhost:8000/messages', json={
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "nsip_get_animal",
            "arguments": {"search_string": animal_id}
        },
        "id": 1
    }) as response:
        return await response.json()

async def load_test():
    async with aiohttp.ClientSession() as session:
        tasks = [call_tool(session, f"640149202{i}FLE249")
                 for i in range(100)]
        results = await asyncio.gather(*tasks)
        print(f"Completed {len(results)} requests")

asyncio.run(load_test())
```

### Custom Timeout Configuration

The NSIP client uses a 30-second timeout by default. For slow connections:

```python
# Modify nsip_mcp/tools.py
def get_nsip_client() -> NSIPClient:
    global _client_instance
    if _client_instance is None:
        _client_instance = NSIPClient(timeout=60)  # 60 seconds
    return _client_instance
```

### Integration Patterns

#### Pattern 1: Conversational AI

```
User: "Show me Katahdin sheep with good weaning weight"
AI: → nsip_list_breeds() to get breed IDs
    → nsip_search_animals(breed_id=64, sorted_trait="WWT", reverse=true)
    → Returns top animals sorted by WWT
```

#### Pattern 2: Pedigree Analysis

```
User: "Analyze the lineage of sheep 6####92020###249"
AI: → nsip_search_by_lpn("6####92020###249")
    → Returns complete profile with lineage and progeny
    → Summarizes family tree and genetic traits
```

#### Pattern 3: Trait Comparison

```
User: "Compare BWT ranges across different breeds"
AI: → nsip_list_breeds() to get all breeds
    → For each breed: nsip_get_trait_ranges(breed_id)
    → Compares BWT min/max across breeds
```

### Batch Processing

For bulk operations, use pagination effectively:

```python
# Get all animals for a breed (paginated)
breed_id = 486
page_size = 100
page = 0

while True:
    result = nsip_search_animals(
        breed_id=breed_id,
        page=page,
        page_size=page_size
    )

    # Process results
    animals = result['results']
    if not animals:
        break

    # Next page
    page += 1
```

### Custom Summarization

To extend summarization for specific use cases, modify `nsip_mcp/context.py`:

```python
def summarize_response(response: Dict[str, Any], token_budget: int = TOKEN_THRESHOLD) -> Dict[str, Any]:
    # Add custom summarization logic here
    # Example: Preserve specific traits for your analysis

    custom_traits = ["BWT", "WWT", "YWT"]  # Your focus traits

    # Filter traits to custom set
    traits = response.get("traits", {})
    filtered = {k: v for k, v in traits.items() if k in custom_traits}

    # Return custom summary
    return {
        "lpn_id": response.get("lpn_id"),
        "breed": response.get("breed"),
        "custom_traits": filtered,
        "_summarized": True
    }
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Server Won't Start

**Symptoms:**
```
Configuration error: MCP_PORT environment variable required for http-sse transport
```

**Solution:**
```bash
# Set required environment variable
export MCP_PORT=8000
MCP_TRANSPORT=http-sse nsip-mcp-server
```

**Root Cause:** HTTP SSE and WebSocket transports require a port number.

---

#### Issue 2: Slow Tool Discovery

**Symptoms:**
- Health check shows discovery time >5s
- Initial tool calls take a long time

**Solution:**
```bash
# Enable debug logging to identify bottleneck
LOG_LEVEL=DEBUG nsip-mcp-server
```

**Possible Causes:**
- Network latency to NSIP API
- Slow tiktoken initialization
- Insufficient system resources

---

#### Issue 3: Low Cache Hit Rate

**Symptoms:**
- Health check shows hit rate <30%
- Repeated queries feel slow

**Solution:**
1. Check if queries have varying parameters
2. Ensure parameters are consistent (sort order matters)
3. Consider longer TTL for stable data

**Example:**
```python
# These create DIFFERENT cache keys:
nsip_search_animals(breed_id=486, page=0)
nsip_search_animals(page=0, breed_id=486)  # Different order!

# Use consistent parameter ordering
```

---

#### Issue 4: Context Overflow Despite Summarization

**Symptoms:**
- LLM still receives too much data
- Summarization reduction <70%

**Solution:**
1. Check health metrics: `get_server_health`
2. Review `_reduction_percent` in responses
3. Adjust summarization strategy in `context.py`

**Debug Example:**
```bash
# Enable debug logging to see token counts
LOG_LEVEL=DEBUG nsip-mcp-server

# Check specific response
{
  "_summarized": true,
  "_original_token_count": 3500,
  "_summary_token_count": 1200,
  "_reduction_percent": 65.7  # Below 70% target
}
```

---

#### Issue 5: Invalid Parameter Errors

**Symptoms:**
```json
{
  "error": {
    "code": -32602,
    "message": "Invalid parameter: search_string"
  }
}
```

**Solution:**
Read the `suggestion` field in error response:
```json
{
  "error": {
    "data": {
      "suggestion": "Provide a valid LPN ID like '6####92020###249'"
    }
  }
}
```

**Common Mistakes:**
- LPN ID too short (<5 characters)
- Negative page numbers
- Page size >100
- Empty search strings

---

#### Issue 6: NSIP API Timeouts

**Symptoms:**
```json
{
  "error": {
    "code": -32000,
    "message": "NSIP API timeout"
  }
}
```

**Solution:**
1. Check NSIP website status: http://nsipsearch.nsip.org
2. Increase timeout (see Advanced Usage)
3. Implement retry logic

**Retry Example:**
```python
import time

def call_with_retry(tool_name, params, max_retries=3):
    for attempt in range(max_retries):
        try:
            return call_tool(tool_name, params)
        except TimeoutError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
```

---

#### Issue 7: WebSocket Connection Drops

**Symptoms:**
- WebSocket disconnects randomly
- Connection closed unexpectedly

**Solution:**
1. Implement ping/pong keep-alive
2. Handle reconnection in client
3. Check network stability

**Keep-Alive Example:**
```javascript
const ws = new WebSocket('ws://localhost:9000/ws');

// Send ping every 30 seconds
setInterval(() => {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      jsonrpc: "2.0",
      method: "ping",
      id: Date.now()
    }));
  }
}, 30000);

// Reconnect on close
ws.onclose = () => {
  console.log('Reconnecting...');
  setTimeout(connect, 1000);
};
```

---

### Debug Logging

Enable detailed logging for troubleshooting:

```bash
# Debug level (most verbose)
LOG_LEVEL=DEBUG nsip-mcp-server

# Info level (default)
LOG_LEVEL=INFO nsip-mcp-server

# Warning level (errors only)
LOG_LEVEL=WARNING nsip-mcp-server
```

**Debug Output Example:**
```
DEBUG:nsip_mcp.cache:Cache MISS for get_animal_details:{'search_string':'6####92020###249'}
DEBUG:nsip_client:GET http://nsipsearch.nsip.org/api/details/getAnimalDetails?searchString=6####92020###249
DEBUG:nsip_mcp.context:Response size: 3500 tokens, threshold: 2000, summarizing: True
DEBUG:nsip_mcp.context:Summarization reduced tokens from 3500 to 1050 (70.0% reduction)
DEBUG:nsip_mcp.cache:Cache SET for get_animal_details:{'search_string':'6####92020###249'}
```

---

### Performance Tuning

**Optimize Startup Time:**
1. Use a faster Python interpreter (PyPy)
2. Pre-initialize tiktoken cache
3. Reduce dependency loading

**Optimize Cache:**
1. Increase TTL for stable data (modify cache.py)
2. Implement cache warming on startup
3. Use external cache (Redis) for persistence

**Optimize Summarization:**
1. Cache summarization results
2. Pre-compute summaries for common queries
3. Adjust token threshold based on use case

---

### Getting Help

**Resources:**
- GitHub Issues: https://github.com/epicpast/nsip-api-client/issues
- Repository: https://github.com/epicpast/nsip-api-client
- NSIP Website: http://nsipsearch.nsip.org

**Reporting Bugs:**
Include:
1. Server version (`pip show nsip-client`)
2. Python version (`python --version`)
3. Transport configuration
4. Health metrics output
5. Debug logs (with `LOG_LEVEL=DEBUG`)
6. Minimal reproduction steps

---

## API Reference

### Type Definitions

#### BreedGroup

```typescript
interface BreedGroup {
  id: number;        // Breed group ID (e.g., 64)
  name: string;      // Breed group name (e.g., "Hair")
}
```

#### TraitData

```typescript
interface TraitData {
  value: number;      // EBV value
  accuracy: number;   // Accuracy percentage (0-100)
}
```

#### AnimalSummary

```typescript
interface AnimalSummary {
  LpnId: string;           // Animal identifier
  Breed: string;           // Breed name
  Gender: string;          // "Male" or "Female"
  DateOfBirth: string;     // Date string
  Status: string;          // e.g., "CURRENT", "SOLD"
  Sire?: string;           // Sire LPN ID
  Dam?: string;            // Dam LPN ID
}
```

#### AnimalDetails

```typescript
interface AnimalDetails {
  lpn_id: string;
  breed: string;
  gender: string;
  date_of_birth: string;
  status: string;
  sire?: string;
  dam?: string;
  total_progeny: number;
  genotyped: boolean;
  traits: Record<string, TraitData>;
  contact?: ContactInfo;
  _summarized: boolean;
  _original_token_count?: number;
  _summary_token_count?: number;
  _reduction_percent?: number;
}
```

#### ContactInfo

```typescript
interface ContactInfo {
  farm_name: string;
  contact_name: string;
  phone: string;
  email: string;
}
```

#### SearchResults

```typescript
interface SearchResults {
  results: AnimalSummary[];
  total_count: number;
  page: number;
  page_size: number;
  _summarized: boolean;
  _original_token_count: number;
}
```

#### ProgenyResults

```typescript
interface ProgenyResults {
  animals: AnimalSummary[];
  total_count: number;
  page: number;
  page_size: number;
  _summarized: boolean;
  _original_token_count: number;
}
```

---

### Common Trait Codes

#### Growth Traits

| Code | Name | Description |
|------|------|-------------|
| BWT | Birth Weight | Weight at birth |
| WWT | Weaning Weight | Weight at weaning (~120 days) |
| MWWT | Maternal Weaning Weight | Maternal effect on lamb weight |
| PWWT | Post Weaning Weight | Weight after weaning |
| YWT | Yearling Weight | Weight at 1 year |

#### Carcass Traits

| Code | Name | Description |
|------|------|-------------|
| YEMD | Yearling Eye Muscle Depth | Loin muscle depth at 1 year |
| YFAT | Yearling Fat | Fat depth at 1 year |
| PEMD | Post Weaning Eye Muscle Depth | Loin muscle depth post-weaning |
| PFAT | Post Weaning Fat | Fat depth post-weaning |

#### Wool Traits

| Code | Name | Description |
|------|------|-------------|
| YGFW | Yearling Greasy Fleece Weight | Fleece weight at 1 year |
| YFD | Yearling Fibre Diameter | Wool fineness at 1 year |
| YSL | Yearling Staple Length | Wool length at 1 year |

#### Reproduction

| Code | Name | Description |
|------|------|-------------|
| NLB | Number of Lambs Born | Litter size |
| NLW | Number of Lambs Weaned | Successful weanings |

#### Parasite Resistance

| Code | Name | Description |
|------|------|-------------|
| WFEC | Weaning Fecal Egg Count | Parasite resistance at weaning |
| PFEC | Post Weaning Fecal Egg Count | Parasite resistance post-weaning |

#### Indexes

| Code | Name | Description |
|------|------|-------------|
| USRangeIndex | US Range Index | Combined index for range production |
| USHairIndex | US Hair Index | Combined index for hair sheep |
| SRC$ | SRC Dollar Index | Economic index |

---

### Breed Group IDs

| ID | Name | Common Breeds |
|----|------|---------------|
| 61 | Range | Rambouillet, Targhee |
| 62 | Maternal Wool | Columbia, Polypay |
| 64 | Hair | Katahdin, Dorper, St. Croix |
| 69 | Terminal | Suffolk, Hampshire, Texel |

---

## Version History

- **v1.1.0** (2025-10-11): Added MCP server support
- **v1.0.0** (2025-10-06): Initial NSIP API client release

---

## License

MIT License - See LICENSE file for details.

---

## Credits

**NSIP MCP Server** is built on:
- FastMCP 2.0 - Model Context Protocol framework
- tiktoken - Token counting library
- NSIP Search API - National Sheep Improvement Program data

**Reverse Engineering Credits:**
The NSIP API client was created through network traffic analysis of the NSIP Search web application at http://nsipsearch.nsip.org

---

*Last Updated: October 11, 2025*
