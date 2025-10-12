# Implementation Plan: Claude Code Plugin Distribution

**Branch**: `002-using-the-last` | **Date**: 2025-10-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-using-the-last/spec.md`

## Summary

Package the nsip-api-client project as a Claude Code plugin to enable one-command installation and usage of the NSIP MCP server. Users will be able to install the plugin via `/plugin marketplace add epicpast/nsip-api-client` and `/plugin install nsip-api-client`, which automatically configures and starts the MCP server, exposes all 10 NSIP tools, and provides convenient slash commands for common workflows (discover, lookup, profile, health, test-api). The plugin supports environment variable configuration for NSIP credentials and works across both terminal and VS Code versions of Claude Code.

## Technical Context

**Language/Version**: Python 3.10+ (existing project requirement), JSON/Markdown for plugin configuration
**Primary Dependencies**:
- Existing: nsip_client (client library), nsip_mcp (FastMCP 2.12.4+ server)
- New: Claude Code plugin system (JSON schema for marketplace.json and plugin.json)
**Storage**: N/A (plugin configuration stored in `.claude-plugin/` directory)
**Testing**: pytest for validation of plugin structure and configuration files
**Target Platform**: Claude Code CLI (terminal) and VS Code extension
**Project Type**: Plugin packaging (adds `.claude-plugin/` directory to existing single-project structure)
**Performance Goals**:
- Plugin install and MCP server startup: <2 minutes total (SC-001)
- Slash command execution: <30 seconds for common tasks (SC-004)
**Constraints**:
- Silent success operations; errors only mode (clarification Q1)
- Generic authentication errors without credential exposure (clarification Q2)
- Plugin enable must fail with diagnostic error if MCP server fails to start (clarification Q3)
- Claude Code marketplace JSON schema compliance required
- MCP server transport types: stdio, streamable-http, or websocket only
**Scale/Scope**:
- 1 plugin with 1 MCP server configuration
- 9+ slash commands for NSIP workflows
- 10 MCP tools exposed (existing nsip_mcp implementation)
- Support for 2 platforms (terminal + VS Code)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Simplicity and Clarity

✅ **PASS** - Plugin adds focused `.claude-plugin/` directory with clear purpose: package distribution
- New components serve single purpose: marketplace metadata, MCP config, slash commands
- No new dependencies on nsip_client or nsip_mcp (uses existing MCP server as-is per FR out-of-scope)
- Configuration files are simple JSON/Markdown with well-defined schemas

### Principle II: Testing and Quality

✅ **PASS** - Plugin configuration testing planned
- JSON schema validation tests for marketplace.json and plugin.json
- Slash command prompt validation
- Integration tests for plugin install/enable/disable flows
- All existing quality gates (black, isort, flake8, mypy, pytest >80% coverage) apply to any Python test code
- Plugin-specific artifacts (JSON, Markdown) validated via schema checks

### Principle III: GitHub-First Distribution

✅ **PASS** - Plugin distributed via GitHub repository
- Claude Code plugins are GitHub-first by design (marketplace points to GitHub repo)
- Users add marketplace via `/plugin marketplace add epicpast/nsip-api-client` (GitHub URL)
- No PyPI involvement for plugin packaging
- Aligns with existing constitution for main package distribution

### Principle IV: Code Quality Standards

✅ **PASS** - No new Python code; configuration files only
- JSON files: validated via schema
- Markdown files: standard formatting for slash command prompts
- Existing code quality tools (black, isort, flake8, mypy) not applicable to plugin artifacts
- Any test code added follows existing quality standards

### Principle V: Documentation Excellence

✅ **PASS** - Documentation requirements defined in spec
- FR-009: Plugin MUST include README.md with installation, prerequisites, usage examples
- FR-010: Plugin MUST include slash command documentation
- Plugin metadata includes clear description for marketplace discovery
- Usage examples for all slash commands required

### Quality Gates Compliance

✅ **PASS** - All mandatory quality gates remain applicable
- Plugin artifacts (JSON/Markdown) don't require Python quality gates
- Any new Python test code must pass all 6 mandatory gates
- No changes to existing nsip_client or nsip_mcp code (out of scope)
- CI/CD workflows unchanged

**Constitution Check Status**: ✅ **ALL PRINCIPLES SATISFIED**

No violations. Plugin packaging is additive and aligns with all constitutional principles.

## Project Structure

### Documentation (this feature)

```
specs/002-using-the-last/
├── plan.md              # This file (/speckit.plan command output)
├── spec.md              # Feature specification
├── checklists/
│   └── requirements.md  # Spec quality validation
├── research.md          # Phase 0 output (Claude Code plugin system research)
├── data-model.md        # Phase 1 output (plugin metadata model)
├── quickstart.md        # Phase 1 output (plugin installation and usage guide)
└── contracts/           # Phase 1 output (JSON schemas for plugin config)
    ├── marketplace-schema.json
    ├── plugin-schema.json
    └── slash-command-schema.json
```

### Source Code (repository root)

```
# Existing structure (unchanged)
src/
├── nsip_client/         # NSIP API client library (existing, no changes)
├── nsip_mcp/            # MCP server implementation (existing, no changes)
tests/
├── unit/                # Unit tests (existing)
├── integration/         # Integration tests (existing)
└── plugin/              # NEW: Plugin validation tests
    ├── test_marketplace_json.py
    ├── test_plugin_json.py
    └── test_slash_commands.py

# NEW: Plugin packaging structure
.claude-plugin/
├── marketplace.json     # Plugin marketplace metadata
├── plugin.json          # Plugin definition with MCP server config (OR .mcp.json below)
├── .mcp.json            # Alternative: separate MCP server config
├── README.md            # Plugin installation and usage documentation
└── commands/            # Slash command definitions
    ├── discover.md
    ├── lookup.md
    ├── profile.md
    ├── health.md
    ├── test-api.md
    ├── search.md
    ├── traits.md
    ├── lineage.md
    └── progeny.md
```

**Structure Decision**:

The plugin uses the **additive packaging structure** where `.claude-plugin/` directory is added to the existing single-project layout. This maintains separation between:

1. **Core Library** (`src/nsip_client/`, `src/nsip_mcp/`) - Existing implementation, unchanged
2. **Plugin Packaging** (`.claude-plugin/`) - New distribution mechanism
3. **Tests** (`tests/plugin/`) - New validation for plugin configuration

**MCP Server Configuration Choice**: Use **inline configuration in plugin.json** (not separate `.mcp.json`) for simplicity. This keeps all plugin metadata in one file and reduces configuration fragmentation.

**Slash Command Storage**: Create `commands/` subdirectory under `.claude-plugin/` with one Markdown file per command. This provides clear organization and follows Claude Code plugin conventions.

## Complexity Tracking

*No constitutional violations requiring justification.*

All design decisions align with constitution principles:
- Simplicity: Minimal new files, clear separation of concerns
- Testing: Plugin config validated via schema tests
- GitHub-First: Plugin distributed via GitHub marketplace mechanism
- Quality: Standard validation for configuration artifacts
- Documentation: Comprehensive plugin docs required (FR-009, FR-010)
