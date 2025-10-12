# NSIP Search API Client

A Python client for the NSIP (National Sheep Improvement Program) Search API, reverse-engineered from http://nsipsearch.nsip.org

## Overview

This client provides programmatic access to sheep breeding data including:
- Animal details and genetic traits (EBVs)
- Pedigree/lineage information
- Progeny records
- Breed groups and trait ranges
- Search and filtering capabilities

## Installation

> **⚠️ Important:** This package is **NOT** published to PyPI. It is only available through GitHub Releases.
> See [DISTRIBUTION.md](DISTRIBUTION.md) for our distribution policy.

### From GitHub Release (Recommended)

Download the latest release from the [releases page](https://github.com/epicpast/nsip-api-client/releases):

```bash
# Install from wheel (recommended)
pip install https://github.com/epicpast/nsip-api-client/releases/latest/download/nsip_client-1.0.0-py3-none-any.whl

# Or install from source distribution
pip install https://github.com/epicpast/nsip-api-client/releases/download/v1.0.0/nsip-client-1.0.0.tar.gz
```

### From Git

```bash
# Install latest from main branch
pip install git+https://github.com/epicpast/nsip-api-client.git

# Install specific version tag
pip install git+https://github.com/epicpast/nsip-api-client.git@v1.0.0
```

### From Source

```bash
git clone https://github.com/epicpast/nsip-api-client.git
cd nsip-api-client
pip install -e .
```

## API Endpoints Discovered

### Base URL
```
http://nsipsearch.nsip.org/api
```

### Authentication
No authentication required - this is a public API.

### Endpoints

#### Search & Metadata
- `GET /search/getDateLastUpdated` - Get database last update date
- `GET /search/getAvailableBreedGroups` - List all breed groups
- `GET /search/getStatusesByBreedGroup` - List animal statuses
- `GET /search/getTraitRangesByBreed?breedId={id}` - Get trait ranges for a breed
- `POST /search/getPageOfSearchResults?page={p}&pageSize={size}&breedId={id}` - Search animals

#### Animal Details
- `GET /details/getAnimalDetails?searchString={lpnId}` - Get animal details
- `GET /details/getLineage?lpnId={lpnId}` - Get pedigree/lineage
- `GET /details/getPageOfProgeny?lpnId={lpnId}&page={p}&pageSize={size}` - Get offspring

## Usage

### Basic Example

```python
from nsip_client import NSIPClient

# Initialize client
client = NSIPClient()

# Get animal details
animal = client.get_animal_details("6401492020FLE249")
print(f"Breed: {animal['Breed']}")
print(f"DOB: {animal['DateOfBirth']}")

# Get progeny
progeny = client.get_progeny("6401492020FLE249")
print(f"Total offspring: {progeny['TotalCount']}")

# Get lineage
lineage = client.get_lineage("6401492020FLE249")
```

### Search Animals

```python
# Search by breed
results = client.search_animals(
    breed_id=486,  # South African Meat Merino
    page=0,
    page_size=15
)

for animal in results['Results']:
    print(animal['LpnId'])
```

### Get Breed Information

```python
# Get all breed groups
breed_groups = client.get_available_breed_groups()
for group in breed_groups:
    print(f"{group['Id']}: {group['Name']}")

# Get trait ranges for a breed
trait_ranges = client.get_trait_ranges_by_breed(486)
```

### Complete Animal Profile

```python
# Get all information at once
profile = client.search_by_lpn("6401492020FLE249")
print(profile['details'])
print(profile['lineage'])
print(profile['progeny'])
```

## MCP Server

The NSIP API Client includes an MCP (Model Context Protocol) server that exposes NSIP sheep breeding data to LLM applications. The server provides intelligent context management with automatic response summarization to prevent LLM context window overflow.

### Features

- **9 MCP Tools**: Complete access to NSIP API through MCP protocol
- **Context Management**: Automatic summarization of large responses (>2000 tokens)
- **Smart Caching**: 1-hour TTL cache with 40%+ hit rate target
- **Multiple Transports**: stdio (CLI), HTTP SSE (web), WebSocket (real-time)
- **Performance Optimized**: <3s startup, <5s tool discovery, 70% token reduction

### Installation

The MCP server is included with the package and accessible via the `nsip-mcp-server` command:

```bash
# Install from GitHub release
pip install git+https://github.com/epicpast/nsip-api-client@v1.0.0

# Or using uvx (no installation required)
uvx --from git+https://github.com/epicpast/nsip-api-client@v1.0.0 nsip-mcp-server
```

### Quick Start

**Start the server (stdio mode - default)**:
```bash
nsip-mcp-server
```

**Configure with Claude Desktop** (`claude_desktop_config.json`):
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

### Available MCP Tools

| Tool Name | Description | May Be Summarized |
|-----------|-------------|-------------------|
| `nsip_get_last_update` | Get database last updated timestamp | No |
| `nsip_list_breeds` | List available breed groups | No |
| `nsip_get_statuses` | Get status options for breed group | No |
| `nsip_get_trait_ranges` | Get trait value ranges for breed | No |
| `nsip_search_animals` | Search animals by breed and traits | Yes |
| `nsip_get_animal` | Get detailed animal information | Yes |
| `nsip_get_lineage` | Get animal lineage/pedigree | Yes |
| `nsip_get_progeny` | Get animal progeny list | Yes |
| `nsip_search_by_lpn` | Comprehensive animal lookup | Always |

### Transport Options

**stdio (Default - for MCP clients)**:
```bash
nsip-mcp-server
# Or explicitly:
MCP_TRANSPORT=stdio nsip-mcp-server
```

**HTTP SSE (for web applications)**:
```bash
MCP_TRANSPORT=http-sse MCP_PORT=8000 nsip-mcp-server
```

**WebSocket (for real-time bidirectional communication)**:
```bash
MCP_TRANSPORT=websocket MCP_PORT=9000 nsip-mcp-server
```

### Environment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `MCP_TRANSPORT` | Transport mechanism | `stdio` | `http-sse`, `websocket` |
| `MCP_PORT` | Port for HTTP SSE/WebSocket | None (required for non-stdio) | `8000`, `9000` |
| `TIKTOKEN_CACHE_DIR` | Token cache directory | OS default | `/tmp/tiktoken` |
| `LOG_LEVEL` | Logging verbosity | `INFO` | `DEBUG`, `WARNING` |

### Context Management

The server automatically manages response sizes to prevent LLM context overflow:

**Responses ≤2000 tokens**: Pass through unmodified
**Responses >2000 tokens**: Automatically summarized to ~70% reduction

**What's preserved in summaries**:
- ✅ Identity: LPN ID, breed, sire, dam
- ✅ Progeny: Total count (not full list)
- ✅ Contact: All breeder information
- ✅ Top 3 traits by accuracy (≥50% accuracy only)

**What's omitted**:
- ❌ Low-accuracy traits (<50%)
- ❌ Verbose metadata
- ❌ Full progeny lists (count only)

**Example summarized response**:
```json
{
  "lpn_id": "6401492020FLE249",
  "breed": "Katahdin",
  "sire": "6401492019FLE124",
  "dam": "6401492018FLE035",
  "total_progeny": 6,
  "contact": {
    "farm_name": "Beyond Blessed Farm",
    "phone": "(276)-759-4718"
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

### Caching

The server caches NSIP API responses with a **1-hour TTL** to reduce API load:

- **Cache Key**: `method_name:sorted_json_params`
- **Target Hit Rate**: 40%+ in typical usage
- **Max Size**: 1000 entries
- **Eviction**: FIFO (oldest removed first)

Example:
```python
# First call - API fetch
nsip_get_animal(search_string="6401492020FLE249")  # Cache miss

# Within 1 hour - cached response
nsip_get_animal(search_string="6401492020FLE249")  # Cache hit (fast)

# After 1 hour - fresh data
nsip_get_animal(search_string="6401492020FLE249")  # Cache expired
```

### Error Handling

All MCP tools return structured errors following JSON-RPC 2.0 with LLM-friendly suggestions:

```json
{
  "error": {
    "code": -32602,
    "message": "Invalid parameter: lpn_id",
    "data": {
      "parameter": "lpn_id",
      "value": "123",
      "expected": "Non-empty string with at least 5 characters",
      "suggestion": "Provide a valid LPN ID like '6401492020FLE249'"
    }
  }
}
```

**Common error codes**:
- `-32602`: Invalid parameters (check suggestion for fix)
- `-32000`: NSIP API error (verify API availability)
- `-32001`: Cache error (retry without cache)
- `-32002`: Summarization error (request smaller dataset)

### Health Monitoring

Get server health and performance metrics (HTTP SSE/WebSocket only):

```bash
curl http://localhost:8000/health
```

Response includes:
- Discovery times (target: <5s)
- Summarization reduction (target: ≥70%)
- Validation success rate (target: ≥95%)
- Cache hit rate (target: ≥40%)
- Concurrent connections (support: 50+)
- Startup time (target: <3s)

### Performance

The MCP server is designed to meet these targets:

| Metric | Target |
|--------|--------|
| Tool Discovery | <5 seconds |
| Summarization Reduction | ≥70% token reduction |
| Validation Success | ≥95% caught before API |
| Cache Hit Rate | ≥40% |
| Concurrent Connections | 50+ without degradation |
| Startup Time | <3 seconds |

### Advanced Usage

**Example MCP tool call**:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "nsip_get_animal",
    "arguments": {
      "search_string": "6401492020FLE249"
    }
  },
  "id": 1
}
```

**Example search with traits**:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "nsip_search_animals",
    "arguments": {
      "breed_id": 486,
      "page": 0,
      "page_size": 15
    }
  },
  "id": 2
}
```

For complete MCP server documentation, examples, and troubleshooting, see `specs/001-create-an-mcp/quickstart.md`.

## API Response Structure

### Animal Details Response
```json
{
  "LpnId": "6401492020FLE249",
  "Breed": "Katahdin",
  "BreedGroup": "Hair",
  "DateOfBirth": "2/5/2020",
  "Gender": "Female",
  "Status": "CURRENT",
  "Sire": "6401492019FLE124",
  "Dam": "6401492018FLE035",
  "TotalProgeny": 6,
  "Genotyped": "No",
  "Traits": {
    "BWT": {"Value": 0.246, "Accuracy": 74},
    "WWT": {"Value": 3.051, "Accuracy": 71},
    ...
  },
  "ContactInfo": {
    "FarmName": "Beyond Blessed Farm",
    "ContactName": "Chris and Mandy Fletcher",
    "Phone": "(276)-759-4718",
    "Email": "mbfletcher08@gmail.com"
  }
}
```

## Breed Groups

- **61** - Range
- **62** - Maternal Wool
- **64** - Hair
- **69** - Terminal

## Common Traits (EBVs)

### Growth Traits
- **BWT** - Birth Weight
- **WWT** - Weaning Weight
- **MWWT** - Maternal Weaning Weight
- **PWWT** - Post Weaning Weight
- **YWT** - Yearling Weight

### Carcass Traits
- **YEMD** - Yearling Eye Muscle Depth
- **YFAT** - Yearling Fat
- **PEMD** - Post Weaning Eye Muscle Depth
- **PFAT** - Post Weaning Fat

### Wool Traits (for wool breeds)
- **YGFW** - Yearling Greasy Fleece Weight
- **YFD** - Yearling Fibre Diameter
- **YSL** - Yearling Staple Length

### Reproduction
- **NLB** - Number of Lambs Born
- **NLW** - Number of Lambs Weaned

### Parasite Resistance
- **WFEC** - Weaning Fecal Egg Count
- **PFEC** - Post Weaning Fecal Egg Count

### Indexes
- **US Range Index**
- **US Hair Index**
- **SRC$ Index**

## Network Traffic Analysis

The API was reverse-engineered using Chrome DevTools by:
1. Loading http://nsipsearch.nsip.org/#!/search
2. Performing searches and viewing animal details
3. Capturing network requests to identify API endpoints
4. Analyzing request/response headers and payloads

### Headers Used
```
Accept: application/json, text/plain, */*
User-Agent: Mozilla/5.0...
```

No authentication headers, cookies, or API keys required.

## Limitations

- This is a reverse-engineered client based on public web traffic
- The API is not officially documented
- Endpoints may change without notice
- Rate limiting behavior is unknown
- Some endpoints (like breed list by group) may need additional discovery

## Example: Your Sheep

```python
client = NSIPClient()

# Get details for your sheep
my_sheep = client.search_by_lpn("6401492020FLE249")

print(f"Name/ID: {my_sheep['details']['LpnId']}")
print(f"Breed: {my_sheep['details']['Breed']}")
print(f"Farm: {my_sheep['details']['ContactInfo']['FarmName']}")
print(f"Total Progeny: {my_sheep['details']['TotalProgeny']}")
print(f"US Hair Index: {my_sheep['details']['Traits']['USHairIndex']['Value']}")
```

## License

This client is provided as-is for educational and research purposes. The NSIP data remains property of the National Sheep Improvement Program.
