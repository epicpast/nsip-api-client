# Quickstart: NSIP API Client Claude Code Plugin

**Version**: 1.1.1
**Last Updated**: 2025-10-12
**Target Audience**: Claude Code users who want to access NSIP sheep breeding data

## Overview

The NSIP API Client plugin provides instant access to NSIP sheep breeding data through Claude Code. Install with a single command to get:

- **10 MCP Tools**: Access animal details, lineage, progeny, breed data, and more
- **9 Slash Commands**: Quick workflows for common tasks (discover, lookup, profile, health, etc.)
- **Auto-Configuration**: MCP server starts automatically when plugin enabled
- **Credential Management**: Secure environment variable-based authentication

## Prerequisites

### 1. Claude Code Installation

- **Terminal**: Claude Code CLI installed and working
- **VS Code**: Claude Code extension installed and activated

### 2. Python Environment

- **Python Version**: 3.10 or higher
- **Package Installation**: nsip-api-client package installed in virtual environment

### 3. NSIP API Credentials

- **Base URL**: NSIP API endpoint (e.g., `https://api.nsip.org.au`)
- **API Key**: Valid NSIP API key for authentication

---

## Installation

### Step 1: Clone Repository and Setup Environment

```bash
# Clone the repository
git clone https://github.com/epicpast/nsip-api-client.git
cd nsip-api-client

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .

# Verify installation
python -c "import nsip_client, nsip_mcp; print('Installation successful')"
```

### Step 2: Configure NSIP Credentials

```bash
# Set environment variables (add to ~/.bashrc or ~/.zshrc for persistence)
export NSIP_BASE_URL="https://api.nsip.org.au"  # Replace with actual URL
export NSIP_API_KEY="your-api-key-here"         # Replace with actual key

# Verify variables are set
echo $NSIP_BASE_URL
echo $NSIP_API_KEY
```

### Step 3: Install Claude Code Plugin

```bash
# In Claude Code (terminal or VS Code)
/plugin marketplace add epicpast/nsip-api-client
/plugin install nsip-api-client

# Verify installation
# The plugin should enable automatically and MCP server should start
# If successful, you'll see no output (silent success per clarification Q1)
# If failure, you'll see diagnostic error message
```

### Step 4: Verify MCP Tools Available

```bash
# In Claude Code conversation
"List available MCP tools"

# Expected: You should see 10 NSIP tools:
# - nsip_get_last_update
# - nsip_list_breeds
# - nsip_get_statuses
# - nsip_get_trait_ranges
# - nsip_search_animals
# - nsip_get_animal
# - nsip_get_lineage
# - nsip_get_progeny
# - nsip_search_by_lpn
# - get_server_health
```

---

## Quick Usage Guide

### Slash Commands (Recommended for Most Users)

#### 1. Discover Available Data

```
/nsip/discover
```

**What it does**: Shows database update date, all breed groups, and available statuses

**Example output**:
```
NSIP Database
- Last Updated: 09/23/2025
- Breed Groups:
  - [61] Range
  - [62] Maternal Wool
  - [64] Hair
  - [69] Terminal
- Statuses: CURRENT, SOLD, DEAD, COMMERCIAL, CULL
```

#### 2. Look Up Animal by LPN ID

```
/nsip/lookup [LPN-ID]
```

**What it does**: Retrieves detailed information about a specific animal

**Example**:
```
/nsip/lookup 6####92020###249
```

**Returns**: Animal basics (breed, status), top traits by accuracy, breeding values

#### 3. Get Complete Animal Profile

```
/nsip/profile [LPN-ID]
```

**What it does**: Comprehensive profile with details, lineage, and progeny

**Example**:
```
/nsip/profile 6####92020###249
```

**Returns**: Full profile including sire/dam, offspring count, top traits

#### 4. Check MCP Server Health

```
/nsip/health
```

**What it does**: Displays server performance metrics and success criteria status

**Returns**: Startup time, cache hit rate, validation success rate, etc.

#### 5. Test API Connectivity

```
/nsip/test-api
```

**What it does**: Validates NSIP API connection and credentials

**Returns**: Success or authentication failure (generic message per clarification Q2)

### Available Slash Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `/nsip/discover` | Show available breeds and statuses | `/nsip/discover` |
| `/nsip/lookup` | Get animal details by LPN ID | `/nsip/lookup [ID]` |
| `/nsip/profile` | Complete animal profile | `/nsip/profile [ID]` |
| `/nsip/health` | MCP server health metrics | `/nsip/health` |
| `/nsip/test-api` | Validate API connectivity | `/nsip/test-api` |
| `/nsip/search` | Search animals with filters | `/nsip/search` |
| `/nsip/traits` | Get trait ranges for breed | `/nsip/traits [breed_id]` |
| `/nsip/lineage` | Get pedigree for animal | `/nsip/lineage [LPN-ID]` |
| `/nsip/progeny` | List offspring | `/nsip/progeny [LPN-ID]` |

---

## Direct MCP Tool Usage (Advanced)

For users who want fine-grained control, call MCP tools directly:

### Example: List Breed Groups

```
"Use the nsip_list_breeds MCP tool to show me all available breed groups"
```

### Example: Search Animals

```
"Use nsip_search_animals with breed_id=486 (Katahdin), page=0, page_size=10"
```

### Example: Get Animal Details

```
"Use nsip_get_animal with search_string='6####92020###249'"
```

---

## Troubleshooting

### Plugin Enable Fails

**Error**: Plugin enable fails with diagnostic error

**Possible Causes**:
1. Python not found or wrong version
2. nsip-api-client package not installed
3. Virtual environment not activated
4. MCP server startup failure

**Solutions**:
```bash
# Check Python version
python --version  # Must be 3.10+

# Verify package installed
pip list | grep nsip

# Ensure venv active
which python  # Should point to venv/bin/python

# Reinstall package
pip install -e .

# Try enabling plugin again
/plugin enable nsip-api-client
```

### Authentication Errors

**Error**: "Authentication failed" (generic message per clarification Q2)

**Possible Causes**:
1. Environment variables not set
2. Invalid API credentials
3. NSIP API unavailable

**Solutions**:
```bash
# Verify environment variables
echo $NSIP_BASE_URL
echo $NSIP_API_KEY

# Re-set variables
export NSIP_BASE_URL="https://api.nsip.org.au"
export NSIP_API_KEY="your-valid-key"

# Restart plugin
/plugin disable nsip-api-client
/plugin enable nsip-api-client

# Test connectivity
/nsip/test-api
```

### MCP Tools Not Available

**Error**: MCP tools don't appear in tool list

**Solutions**:
1. Verify plugin enabled: `/plugin list`
2. Check MCP server status: `/nsip/health`
3. Disable and re-enable: `/plugin disable nsip-api-client && /plugin enable nsip-api-client`
4. Check logs for startup errors

### Silent Operations Confusion

**Note**: Per clarification Q1, plugin operations succeed silently (no output). Only errors are displayed.

**Expected Behavior**:
- ✅ `/plugin install nsip-api-client` → No output = success
- ✅ `/plugin enable nsip-api-client` → No output = success
- ❌ Plugin enable fails → Diagnostic error message shown

---

## Platform Differences

### Terminal vs VS Code

The plugin works identically on both platforms (100% feature parity per SC-005):

| Feature | Terminal | VS Code |
|---------|----------|---------|
| Plugin installation | ✅ Same commands | ✅ Same commands |
| Slash commands | ✅ Same behavior | ✅ Same behavior |
| MCP tools | ✅ All 10 available | ✅ All 10 available |
| Environment variables | ✅ Loaded from shell | ✅ Loaded from process |
| Error handling | ✅ Generic auth errors | ✅ Generic auth errors |

**No platform-specific configuration needed.**

---

## Next Steps

### For Users

1. **Explore NSIP Data**: Start with `/nsip/discover` to see available breeds
2. **Look Up Animals**: Use `/nsip/lookup [ID]` to inspect animal records
3. **Advanced Workflows**: Combine multiple MCP tools for complex queries
4. **Monitor Performance**: Use `/nsip/health` to track server metrics

### For Developers

1. **Read Documentation**: See `.claude-plugin/README.md` for detailed plugin architecture
2. **Review Slash Commands**: Check `.claude-plugin/commands/*.md` for prompt templates
3. **Validate Configuration**: Run `pytest tests/plugin/` for schema validation
4. **Contribute**: Submit PRs for new slash commands or improvements

---

## Support & Resources

- **GitHub Repository**: https://github.com/epicpast/nsip-api-client
- **Issues**: https://github.com/epicpast/nsip-api-client/issues
- **Changelog**: https://github.com/epicpast/nsip-api-client/blob/main/docs/CHANGELOG.md
- **Claude Code Docs**: https://docs.claude.com/en/docs/claude-code/mcp

---

## Success Metrics (Per Feature Spec)

Your installation is successful if you achieve:

- ✅ **SC-001**: Install and first tool call in under 2 minutes
- ✅ **SC-003**: All 10 NSIP MCP tools available immediately
- ✅ **SC-004**: Common tasks (discover, lookup) complete in under 30 seconds
- ✅ **SC-005**: Works on both terminal and VS Code
- ✅ **SC-006**: Credentials configured correctly on first attempt
- ✅ **SC-007**: Plugin enables/disables without errors

Check `/nsip/health` to verify performance metrics against success criteria.
