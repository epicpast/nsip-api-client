# Research: Claude Code Plugin System

**Feature**: Claude Code Plugin Distribution
**Date**: 2025-10-12
**Purpose**: Resolve technical unknowns about Claude Code plugin packaging and MCP server integration

## Research Findings

### 1. Claude Code Plugin Marketplace Structure

**Decision**: Use `marketplace.json` in `.claude-plugin/` directory with standard schema

**Rationale**:
- Claude Code plugin system requires `.claude-plugin/marketplace.json` file
- Marketplace file contains plugin metadata, version, description, and author
- Users add marketplace via `/plugin marketplace add <github-org>/<repo-name>`
- Multiple plugins can be defined in single marketplace.json

**Alternatives Considered**:
- ❌ Individual plugin.json per plugin: More complex, not standard pattern
- ❌ Root-level configuration: Violates Claude Code plugin conventions

**Schema** (based on Claude Code documentation and examples):
```json
{
  "$schema": "https://claude.ai/schemas/plugin-marketplace.json",
  "name": "nsip-api-client",
  "version": "1.1.1",
  "description": "NSIP sheep breeding data access via MCP server for Claude Code",
  "owner": "epicpast",
  "plugins": [
    {
      "name": "nsip-api-client",
      "description": "Access NSIP sheep breeding data with MCP tools and slash commands",
      "version": "1.1.1",
      "author": "epicpast",
      "source": "."
    }
  ]
}
```

**References**:
- Claude Code plugin announcement: https://www.anthropic.com/news/claude-code-plugins
- Example marketplace: https://github.com/anthropics/claude-code/.claude-plugin/marketplace.json

---

### 2. MCP Server Configuration in Plugin

**Decision**: Use **inline MCP server definition in plugin.json** with `mcpServers` key

**Rationale**:
- Claude Code plugins support MCP server definitions either:
  1. Inline in `plugin.json` via `mcpServers` object
  2. Separate `.mcp.json` file at plugin root
- Inline configuration is simpler and keeps all plugin metadata in one place
- Reduces file fragmentation (fewer files to maintain)
- MCP server auto-starts when plugin enabled, auto-stops when disabled

**Alternatives Considered**:
- ❌ Separate `.mcp.json`: More files, additional maintenance burden
- ❌ No MCP config (manual setup): Defeats purpose of plugin (easy installation)

**Configuration Pattern**:
```json
{
  "name": "nsip-api-client",
  "mcpServers": {
    "nsip-api-client": {
      "command": "${CLAUDE_PLUGIN_ROOT}/../../venv/bin/python",
      "args": ["-m", "nsip_mcp.server"],
      "env": {
        "NSIP_BASE_URL": "${NSIP_BASE_URL}",
        "NSIP_API_KEY": "${NSIP_API_KEY}"
      }
    }
  }
}
```

**Key Features**:
- `${CLAUDE_PLUGIN_ROOT}`: Plugin-relative path resolution
- `${VAR_NAME}`: Environment variable expansion
- Transport type defaults to stdio (suitable for MCP servers)

**References**:
- Claude Code MCP docs: https://docs.claude.com/en/docs/claude-code/mcp

---

### 3. Python Path Resolution for MCP Server

**Decision**: Use **relative path from plugin root to Python interpreter** via `${CLAUDE_PLUGIN_ROOT}`

**Rationale**:
- MCP server runs as subprocess spawned by Claude Code
- Must locate Python interpreter with nsip_mcp module installed
- Options evaluated:
  1. ✅ **Virtual environment in repo**: `${CLAUDE_PLUGIN_ROOT}/../../venv/bin/python`
  2. System Python: May not have nsip-api-client installed
  3. Hardcoded path: Not portable across systems

**Assumptions**:
- User has created virtual environment at repo root: `/path/to/nsip-api-client/venv/`
- nsip-api-client package installed in venv: `pip install -e .`
- Plugin installed in repo at: `/path/to/nsip-api-client/.claude-plugin/`
- Path navigation: `.claude-plugin/` → `../../` → repo root → `venv/bin/python`

**Alternatives Considered**:
- ❌ `python3`: May use wrong Python or lack nsip-api-client
- ❌ `/usr/bin/python3`: Hardcoded, not portable
- ❌ `which python`: Shell-dependent, not reliable

**Installation Documentation Must Include**:
```bash
# Prerequisites (to be documented in .claude-plugin/README.md)
cd /path/to/nsip-api-client
python3 -m venv venv
source venv/bin/activate
pip install -e .

# Then install plugin
/plugin marketplace add epicpast/nsip-api-client
/plugin install nsip-api-client
```

---

### 4. Slash Command Definition Format

**Decision**: Use **Markdown files in `.claude-plugin/commands/` directory** with structured prompts

**Rationale**:
- Claude Code slash commands are defined as Markdown files
- Each file contains prompt executed when command is invoked
- File name determines command name (e.g., `discover.md` → `/nsip/discover`)
- Prompts can include instructions for calling MCP tools and formatting output

**Pattern**:
```markdown
# /nsip/discover - Discover Available NSIP Data

You are tasked with discovering and displaying available NSIP sheep breeding data.

## Instructions

1. Call the `nsip_get_last_update` MCP tool to get database update date
2. Call the `nsip_list_breeds` MCP tool to get all breed groups
3. Call the `nsip_get_statuses` MCP tool to get available statuses
4. Format and display the results in a user-friendly overview:

**NSIP Database**
- Last Updated: [date from step 1]
- Breed Groups:
  - [ID] [Name] (for each breed from step 2)
- Statuses: [comma-separated list from step 3]

## Error Handling

- If any tool call fails, display generic error without exposing credentials
- Suggest checking `/nsip/health` for diagnostic information
```

**Alternatives Considered**:
- ❌ JSON-based commands: Less readable, harder to author
- ❌ Inline in plugin.json: Clutters config, poor separation of concerns

**References**:
- Based on Claude Code plugin examples and slash command conventions

---

### 5. Error Handling and Logging Policy

**Decision**: Implement **silent success, errors-only logging** per clarification Q1

**Rationale**:
- User selected Option A: "Silent success, errors only"
- Plugin operations (install, enable, disable) succeed without output
- Only failures display diagnostic messages
- MCP tool errors handled by existing nsip_mcp error responses

**Implementation Notes**:
- MCP server startup errors handled by Claude Code plugin system
- If MCP server fails to start, plugin enable fails (per clarification Q3)
- Slash command errors display via MCP tool error responses
- No additional logging infrastructure needed

**Credential Security** (clarification Q2):
- Authentication errors display generic "Authentication failed" message
- No credential names or values exposed in errors
- Applies to both MCP server startup and MCP tool execution

---

### 6. Testing Strategy for Plugin Configuration

**Decision**: Create **JSON schema validation tests** in `tests/plugin/`

**Rationale**:
- Plugin artifacts (JSON files) need validation but aren't Python code
- Schema validation ensures marketplace.json and plugin.json correctness
- Slash command Markdown files validated for required sections

**Test Coverage**:
1. `test_marketplace_json.py`:
   - Validate marketplace.json against schema
   - Check required fields: name, version, description, plugins
   - Verify plugin metadata completeness

2. `test_plugin_json.py`:
   - Validate plugin.json against schema
   - Check mcpServers configuration
   - Verify environment variable syntax

3. `test_slash_commands.py`:
   - Verify all required slash commands exist (discover, lookup, profile, health, test-api)
   - Validate Markdown structure
   - Check for MCP tool call instructions

**Test Execution**:
- Integrated into existing pytest suite
- Runs with standard `pytest` or `./run_tests_and_coverage.sh`
- Must pass all quality gates before merge

---

### 7. Cross-Platform Compatibility (Terminal vs VS Code)

**Decision**: Use **platform-agnostic configuration** (no platform-specific code)

**Rationale**:
- Claude Code plugin system handles platform differences
- MCP server (stdio transport) works identically in terminal and VS Code
- Slash commands execute the same across platforms
- Environment variables work consistently

**Testing Approach**:
- Manual testing on both terminal and VS Code
- Automated tests validate configuration correctness
- SC-005 success criterion: 100% feature parity across platforms

**No Special Implementation Needed**:
- Plugin configuration is declarative (JSON/Markdown)
- No platform detection or conditional logic required

---

## Summary of Technical Decisions

| Decision Area | Choice | Impact |
|---------------|--------|--------|
| Marketplace Structure | marketplace.json in .claude-plugin/ | Standard pattern, GitHub-first distribution |
| MCP Config Location | Inline in plugin.json via mcpServers | Simpler, fewer files, single source of metadata |
| Python Path | Relative venv path via ${CLAUDE_PLUGIN_ROOT} | Portable, uses project venv |
| Slash Commands | Markdown files in commands/ directory | Readable, maintainable, standard pattern |
| Logging Policy | Silent success, errors only | Per user clarification Q1 |
| Credential Security | Generic auth errors, no exposure | Per user clarification Q2 |
| Startup Failures | Fail plugin enable with diagnostic | Per user clarification Q3 |
| Testing | JSON schema validation + pytest | Validates config correctness |
| Platform Support | Platform-agnostic declarative config | Works on terminal + VS Code |

## Open Questions

None remaining. All technical unknowns have been resolved through research and user clarifications.

## Next Steps

Proceed to **Phase 1: Design & Contracts**:
1. Create data-model.md defining plugin metadata entities
2. Generate JSON schemas in contracts/ directory
3. Create quickstart.md with installation and usage guide
4. Update agent context with new plugin technology
