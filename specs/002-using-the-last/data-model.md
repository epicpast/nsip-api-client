# Data Model: Claude Code Plugin Metadata

**Feature**: Claude Code Plugin Distribution
**Date**: 2025-10-12
**Purpose**: Define entities and relationships for plugin configuration

## Overview

The plugin metadata model defines the structure of configuration files in `.claude-plugin/` directory. These are declarative JSON/Markdown files, not runtime data structures.

## Entities

### 1. Marketplace Metadata

**Purpose**: Top-level container for plugin marketplace information

**Location**: `.claude-plugin/marketplace.json`

**Schema**:
```json
{
  "name": "string",              // Marketplace identifier (e.g., "nsip-api-client")
  "version": "string",           // Marketplace version (semver, e.g., "1.1.1")
  "description": "string",       // Brief marketplace description
  "owner": "string",             // GitHub org/user (e.g., "epicpast")
  "plugins": [Plugin]            // Array of Plugin entities (see below)
}
```

**Validation Rules**:
- `name`: Required, non-empty, matches GitHub repo name
- `version`: Required, semver format (X.Y.Z)
- `description`: Required, 1-200 characters
- `owner`: Required, valid GitHub username/org
- `plugins`: Required, non-empty array

**Relationships**:
- Has many Plugins (1:N)
- Referenced by Claude Code via GitHub URL: `epicpast/nsip-api-client`

---

### 2. Plugin

**Purpose**: Individual plugin definition within marketplace

**Location**: Embedded in `marketplace.json` → `plugins` array

**Schema**:
```json
{
  "name": "string",              // Plugin identifier (e.g., "nsip-api-client")
  "description": "string",       // Plugin description for marketplace
  "version": "string",           // Plugin version (semver)
  "author": "string",            // Plugin author/maintainer
  "source": "string",            // Path to plugin directory (usually ".")
  "category": "string"           // Optional: plugin category (e.g., "data-access")
}
```

**Validation Rules**:
- `name`: Required, unique within marketplace, alphanumeric + hyphens
- `description`: Required, 10-500 characters
- `version`: Required, semver format
- `author`: Required
- `source`: Required, relative path or "." for root
- `category`: Optional, standard categories TBD

**Relationships**:
- Belongs to Marketplace (N:1)
- Has one Plugin Configuration (1:1, via `source` path)

---

### 3. Plugin Configuration

**Purpose**: Detailed plugin settings including MCP server configuration

**Location**: `.claude-plugin/plugin.json` (at path specified by Plugin.source)

**Schema**:
```json
{
  "name": "string",              // Must match Plugin.name
  "mcpServers": {                // MCP server configurations (key = server name)
    "server-name": {
      "command": "string",       // Path to executable (supports ${CLAUDE_PLUGIN_ROOT})
      "args": ["string"],        // Command arguments
      "env": {                   // Environment variables
        "KEY": "value"           // Supports ${VAR} expansion
      }
    }
  }
}
```

**Validation Rules**:
- `name`: Required, must match parent Plugin.name
- `mcpServers`: Optional but recommended for MCP integration
- `mcpServers[name].command`: Required, absolute or ${CLAUDE_PLUGIN_ROOT}-relative path
- `mcpServers[name].args`: Optional array of strings
- `mcpServers[name].env`: Optional object with string key-value pairs

**Variable Expansion**:
- `${CLAUDE_PLUGIN_ROOT}`: Resolves to absolute path of `.claude-plugin/` directory
- `${VAR_NAME}`: Resolves to environment variable `VAR_NAME` value

**Relationships**:
- Belongs to Plugin (1:1)
- Defines 0 or more MCP Server Configurations (1:N)

---

### 4. MCP Server Configuration

**Purpose**: Specifies how to start and connect to MCP server

**Location**: Embedded in `plugin.json` → `mcpServers` object

**Schema**:
```json
{
  "command": "string",           // Executable path
  "args": ["string"],            // Command arguments
  "env": {                       // Environment variables
    "KEY": "value"
  }
}
```

**For nsip-api-client**:
```json
{
  "command": "${CLAUDE_PLUGIN_ROOT}/../../venv/bin/python",
  "args": ["-m", "nsip_mcp.server"],
  "env": {
    "NSIP_BASE_URL": "${NSIP_BASE_URL}",
    "NSIP_API_KEY": "${NSIP_API_KEY}"
  }
}
```

**Validation Rules**:
- `command`: Required, must resolve to executable file
- `args`: Optional, array of strings
- `env`: Optional, string-to-string mapping
- Environment variable references (`${VAR}`) must be defined or plugin enable fails

**Lifecycle**:
- **Plugin Enable**: MCP server started as subprocess
  - Failure → plugin enable fails with diagnostic error (clarification Q3)
- **Plugin Disable**: MCP server terminated gracefully
- **Credentials**: Loaded from environment variables at startup

**Relationships**:
- Belongs to Plugin Configuration (N:1)
- Exposes MCP Tools (1:N, defined in nsip_mcp.server, not plugin config)

---

### 5. Slash Command

**Purpose**: User-facing command shortcuts that execute predefined prompts

**Location**: `.claude-plugin/commands/*.md` (one file per command)

**File Naming**:
- File name determines command: `discover.md` → `/nsip/discover`
- Prefix `/nsip/` inferred from plugin namespace

**Content Structure** (Markdown):
```markdown
# /nsip/[command] - [Brief Description]

[Detailed instructions for Claude to execute]

## Instructions

1. [Step 1]
2. [Step 2]
...

## Error Handling

- [Error scenario 1]: [How to handle]
- [Error scenario 2]: [How to handle]
```

**For nsip-api-client** (9 commands required):
1. `discover.md` - Display database info, breeds, statuses
2. `lookup.md` - Get animal details by LPN ID
3. `profile.md` - Get complete animal profile (details + lineage + progeny)
4. `health.md` - Show MCP server health and metrics
5. `test-api.md` - Validate NSIP API connectivity
6. `search.md` - Search animals with filters
7. `traits.md` - Get trait ranges for a breed
8. `lineage.md` - Get pedigree for an animal
9. `progeny.md` - List offspring for an animal

**Validation Rules**:
- File must exist at `.claude-plugin/commands/[name].md`
- Must contain instructions for calling MCP tools
- Must include error handling guidance
- Must follow silent success / errors-only policy (clarification Q1)

**Relationships**:
- Belongs to Plugin (N:1)
- References MCP Tools (N:M, via prompt instructions)

---

## Entity Relationships Diagram

```
Marketplace (marketplace.json)
  └─1:N─> Plugin (embedded in marketplace.json)
             ├─1:1─> Plugin Configuration (plugin.json)
             │          └─1:N─> MCP Server Configuration (embedded in plugin.json)
             │                      └─1:N─> MCP Tools (defined in nsip_mcp.server code)
             │
             └─1:N─> Slash Command (commands/*.md files)
                        └─N:M─> MCP Tools (referenced in prompts)
```

## Data Flow

### Installation Flow

1. **User Action**: `/plugin marketplace add epicpast/nsip-api-client`
   - Claude Code fetches `marketplace.json` from GitHub
   - Validates Marketplace Metadata schema
   - Registers marketplace

2. **User Action**: `/plugin install nsip-api-client`
   - Claude Code reads Plugin entry from marketplace
   - Loads Plugin Configuration from `source` path
   - Validates configuration schemas
   - Attempts to start MCP Server (if `mcpServers` defined)
   - Success: Plugin enabled, tools available
   - Failure: Plugin enable fails with diagnostic error (clarification Q3)

### Usage Flow

1. **User Action**: `/nsip/discover`
   - Claude Code loads `commands/discover.md`
   - Executes prompt instructions
   - Calls MCP tools: `nsip_get_last_update`, `nsip_list_breeds`, `nsip_get_statuses`
   - Formats and displays results

2. **Error Scenario**: Authentication failure
   - MCP tool returns generic "Authentication failed" (clarification Q2)
   - No credential names or values exposed
   - User sees error, must check environment variables

### Credential Flow

1. **User Setup**: Sets environment variables before enabling plugin
   ```bash
   export NSIP_BASE_URL="https://api.nsip.example.com"
   export NSIP_API_KEY="secret-key-value"
   ```

2. **Plugin Enable**: Environment variables passed to MCP server via `env` configuration
   - `${NSIP_BASE_URL}` → actual URL value
   - `${NSIP_API_KEY}` → actual key value

3. **MCP Server Startup**: nsip_mcp.server reads environment variables
   - Validates presence (if missing, startup may fail)
   - Creates NSIPClient with credentials
   - If invalid, API calls fail with generic auth error

## State Transitions

### Plugin State

```
NOT_INSTALLED ──install──> ENABLED
                            │
                            ├─disable──> DISABLED
                            │
                            └─uninstall──> NOT_INSTALLED

DISABLED ──enable──> ENABLED (may fail if MCP server won't start)
```

### MCP Server State

```
STOPPED ──plugin enable──> STARTING ──success──> RUNNING
                             │
                             └─failure──> STOPPED (plugin enable fails)

RUNNING ──plugin disable──> STOPPED
```

## Validation Constraints

### Cross-Entity Validation

1. **Name Consistency**:
   - `marketplace.json → plugins[].name` MUST match `plugin.json → name`

2. **Version Synchronization**:
   - Plugin version SHOULD match nsip-api-client package version (1.1.1)
   - Marketplace version SHOULD track plugin version

3. **Python Path Validity**:
   - MCP server `command` path MUST resolve to executable Python interpreter
   - Python environment MUST have nsip-api-client installed
   - Path `${CLAUDE_PLUGIN_ROOT}/../../venv/bin/python` assumes specific repo structure

4. **Environment Variables**:
   - `NSIP_BASE_URL` and `NSIP_API_KEY` MUST be set for MCP server to connect
   - Missing variables → MCP server may fail to start or API calls fail with auth errors

5. **Slash Command Coverage**:
   - Minimum 5 slash commands required (FR-007)
   - Recommended: 9 commands for comprehensive NSIP workflow coverage

## Summary

The plugin metadata model is **declarative and file-based**, not a runtime database. Entities are JSON/Markdown configuration files that Claude Code reads to:

1. Register marketplace (marketplace.json)
2. Install plugin (plugin.json, commands/*.md)
3. Start MCP server (mcpServers configuration)
4. Execute slash commands (Markdown prompts)

All entities are validated via JSON schemas (Phase 1 contracts/) before plugin installation succeeds.
