# NSIP API Client - Claude Code Plugin

Access NSIP sheep breeding data through Claude Code with one-command installation.

## Features

- **10 MCP Tools**: Animal details, lineage, progeny, breed data, trait ranges, search, health metrics
- **9 Slash Commands**: Quick workflows for common tasks
- **Auto-Configuration**: MCP server starts automatically when plugin enabled
- **Secure**: Environment variable-based credential management

## Prerequisites

- Claude Code CLI or VS Code extension
- Python 3.10 or higher
- nsip-api-client package installed in virtual environment
- Optional: Custom NSIP_BASE_URL (defaults to http://nsipsearch.nsip.org/api)

## Installation

### Step 1: Setup Environment

```bash
# Clone repository (if not already done)
git clone https://github.com/epicpast/nsip-api-client.git
cd nsip-api-client

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install package
pip install -e .
```

### Step 2: Install Plugin (No Configuration Needed!)

```bash
# In Claude Code (terminal or VS Code)
/plugin marketplace add epicpast/nsip-api-client
/plugin install nsip-api-client

# Verify MCP tools available
"List available MCP tools"
# Expected: 10 NSIP tools listed
```

## Slash Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `/nsip/discover` | Show database info, breeds, statuses | `/nsip/discover` |
| `/nsip/lookup` | Get animal details by LPN ID | `/nsip/lookup [LPN-ID]` |
| `/nsip/profile` | Complete animal profile (details + lineage + progeny) | `/nsip/profile [LPN-ID]` |
| `/nsip/health` | Server performance metrics | `/nsip/health` |
| `/nsip/test-api` | Validate API connectivity | `/nsip/test-api` |
| `/nsip/search` | Search animals with filters | `/nsip/search` |
| `/nsip/traits` | Get trait ranges for breed | `/nsip/traits [breed_id]` |
| `/nsip/lineage` | Get pedigree tree | `/nsip/lineage [LPN-ID]` |
| `/nsip/progeny` | List offspring | `/nsip/progeny [LPN-ID]` |

## MCP Tools

- `nsip_get_last_update`: Database update date
- `nsip_list_breeds`: Available breed groups
- `nsip_get_statuses`: Animal statuses
- `nsip_get_trait_ranges`: Trait min/max values by breed
- `nsip_search_animals`: Search with pagination and filters
- `nsip_get_animal`: Detailed animal information
- `nsip_get_lineage`: Pedigree tree
- `nsip_get_progeny`: Offspring list
- `nsip_search_by_lpn`: Complete profile (combines above)
- `get_server_health`: Server metrics and success criteria

## Troubleshooting

### Plugin Enable Fails

**Error**: Plugin enable fails with diagnostic error

**Solutions**:
- Check Python version: `python --version` (must be 3.10+)
- Verify package installed: `pip list | grep nsip`
- Ensure venv active: `which python` (should point to venv)
- Reinstall: `pip install -e .`

### API Connection Errors

**Note**: The NSIP API is public and requires no authentication.

**If you experience connection issues**:
- Check internet connectivity
- Verify NSIP API is accessible: `curl http://nsipsearch.nsip.org/api/GetLastUpdate`
- Optional: Set custom base URL: `export NSIP_BASE_URL="http://your-custom-url"`
- Test connectivity: `/nsip/test-api`

### MCP Tools Not Available

**Solutions**:
- Verify plugin enabled: `/plugin list`
- Check server status: `/nsip/health`
- Re-enable plugin: `/plugin disable nsip-api-client && /plugin enable nsip-api-client`

## Platform Support

Works identically on Claude Code CLI (terminal) and VS Code extension (100% feature parity per SC-005).

## Support

- **Repository**: https://github.com/epicpast/nsip-api-client
- **Issues**: https://github.com/epicpast/nsip-api-client/issues
- **Changelog**: https://github.com/epicpast/nsip-api-client/blob/main/docs/CHANGELOG.md
