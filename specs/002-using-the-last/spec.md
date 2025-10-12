# Feature Specification: Claude Code Plugin Distribution

**Feature Branch**: `002-using-the-last`
**Created**: 2025-10-12
**Status**: Draft
**Input**: User description: "using the last response listed for slash command specificy the implementation of this project being listed as a claude code plugin"

## Clarifications

### Session 2025-10-12

- Q: What level of operational visibility should users have when plugin operations execute? → A: Silent success, errors only - Plugin operations succeed silently; only errors are displayed to users
- Q: How should the plugin handle credential errors to prevent accidental exposure of API keys in error messages or logs? → A: Never log credentials - Any credential errors display generic message ("Authentication failed") without indicating which credential is problematic
- Q: What should happen if the MCP server fails to start when the plugin is enabled? → A: Fail plugin enable with error - Plugin enable operation fails with diagnostic error; plugin remains disabled; user must fix issue before enabling

## User Scenarios & Testing *(mandatory)*

### User Story 1 - One-Command Plugin Installation (Priority: P1)

Claude Code users want to install the NSIP MCP server with a single command instead of manually editing configuration files. They should be able to discover the plugin, install it, and start using NSIP tools immediately.

**Why this priority**: This is the core value proposition of the plugin system - ease of installation. Without this, users must manually configure `.mcp.json` files, which is error-prone and time-consuming.

**Independent Test**: Can be fully tested by running the plugin install command and verifying that the MCP server starts automatically and exposes NSIP tools. Delivers immediate value by eliminating manual configuration.

**Acceptance Scenarios**:

1. **Given** Claude Code is installed and running, **When** user runs `/plugin marketplace add epicpast/nsip-api-client`, **Then** the marketplace is added successfully with confirmation message
2. **Given** the marketplace is added and Python 3.10+ is installed, **When** user runs `/plugin install nsip-api-client`, **Then** the plugin installs and the MCP server starts automatically
3. **Given** the marketplace is added but Python is not available, **When** user runs `/plugin install nsip-api-client`, **Then** plugin enable fails with diagnostic error indicating Python requirement; plugin remains disabled
4. **Given** the plugin is installed, **When** user lists available tools, **Then** all 10 NSIP MCP tools are available (nsip_get_last_update, nsip_list_breeds, nsip_get_statuses, nsip_get_trait_ranges, nsip_search_animals, nsip_get_animal, nsip_get_lineage, nsip_get_progeny, nsip_search_by_lpn, get_server_health)
5. **Given** the plugin is installed, **When** user calls any NSIP tool, **Then** the tool executes successfully and returns data

---

### User Story 2 - Quick NSIP Data Discovery (Priority: P2)

Users want convenient slash commands that combine multiple NSIP MCP tools into common workflows, making it faster to discover and explore NSIP sheep breeding data.

**Why this priority**: Once the MCP server is working (P1), users need an efficient way to interact with NSIP data. Slash commands provide a guided, user-friendly interface that reduces the learning curve.

**Independent Test**: Can be tested by executing each slash command and verifying it calls the correct MCP tools and formats output appropriately. Delivers value by making common tasks (like "show me available breeds" or "lookup this animal") much faster.

**Acceptance Scenarios**:

1. **Given** the plugin is enabled, **When** user runs `/nsip/discover`, **Then** system displays database update date, all breed groups with IDs, and available statuses in formatted output
2. **Given** the plugin is enabled, **When** user runs `/nsip/lookup` with an LPN ID, **Then** system retrieves and displays formatted animal details including breed, top traits, and status
3. **Given** the plugin is enabled, **When** user runs `/nsip/profile` with an LPN ID, **Then** system displays comprehensive profile with details, lineage, and progeny in a single command
4. **Given** the plugin is enabled, **When** user runs `/nsip/health`, **Then** system displays server performance metrics and success criteria status

---

### User Story 3 - Environment Configuration (Priority: P2)

Users need to configure NSIP API credentials (base URL and API key) for the MCP server without editing complex configuration files. The plugin should support environment variable configuration and provide clear guidance on setup.

**Why this priority**: While MCP server functionality is critical (P1), users must configure credentials to connect to their NSIP instance. This is tied with slash commands (P2) because both enhance the user experience after installation.

**Independent Test**: Can be tested by providing different credential configurations (environment variables, config files) and verifying the MCP server connects successfully. Delivers value by making credential management straightforward.

**Acceptance Scenarios**:

1. **Given** user has NSIP credentials, **When** user sets `NSIP_BASE_URL` and `NSIP_API_KEY` environment variables before enabling plugin, **Then** MCP server starts and NSIP API tools use those credentials successfully
2. **Given** the plugin is enabled without credentials, **When** user attempts to call an NSIP tool, **Then** MCP server is running but tool calls display generic authentication error without exposing credential values
3. **Given** the plugin is enabled, **When** user runs `/nsip/test-api`, **Then** system validates connectivity and reports success or authentication failure (generic message only, no credential exposure)
4. **Given** user updates environment variables, **When** user restarts or re-enables the plugin, **Then** MCP server uses the updated credentials

---

### User Story 4 - Plugin Discovery and Documentation (Priority: P3)

Potential users want to discover the nsip-api-client plugin through the Claude Code marketplace and understand what it does before installing. They should be able to read clear documentation about features, requirements, and usage.

**Why this priority**: Discovery and documentation enhance adoption but are not critical for core functionality. Users can still install and use the plugin if they know about it through other channels.

**Independent Test**: Can be tested by browsing the marketplace, reading plugin metadata, and verifying all information is accurate and helpful. Delivers value by improving discoverability and reducing installation friction.

**Acceptance Scenarios**:

1. **Given** user is browsing Claude Code marketplaces, **When** user searches for "NSIP" or "sheep breeding", **Then** nsip-api-client plugin appears in results with accurate description
2. **Given** user views the plugin details, **When** user reads the plugin description, **Then** they understand it provides NSIP API access via MCP server and see available tools
3. **Given** user installs the plugin, **When** user looks for usage documentation, **Then** they find README with installation instructions, slash command reference, and examples
4. **Given** user needs help, **When** user runs `/nsip/help` or reads documentation, **Then** they see comprehensive guide to all slash commands and MCP tools

---

### Edge Cases

- What happens when user installs plugin without setting NSIP credentials? (MCP server starts successfully; NSIP API tool calls display generic "Authentication failed" message without exposing which credentials are missing)
- How does system handle invalid NSIP credentials? (MCP server starts successfully; NSIP API tool calls return generic authentication error; no credential values or names exposed in error messages)
- What happens if Python is not installed or wrong version when enabling plugin? (Plugin enable fails with diagnostic error; plugin remains disabled until Python 3.10+ available)
- What happens if nsip-api-client package is not installed when enabling plugin? (Plugin enable fails with diagnostic error indicating package requirement; plugin remains disabled)
- What happens if MCP server fails to start due to port conflict or other runtime error? (Plugin enable fails with diagnostic error; plugin remains disabled; user must resolve issue)
- What happens when multiple plugins try to use the same MCP server name? (Plugin installation should detect conflict and warn user)
- How does system handle plugin updates? (Users should be able to update plugin without losing configuration)
- What happens when NSIP API is unavailable or times out? (Tools should return helpful error messages and suggest checking `/nsip/health`)
- How does plugin behave when disabled and re-enabled? (MCP server should stop cleanly and restart without issues; startup failures fail the enable operation)
- What happens when user has both manual `.mcp.json` configuration and plugin installed? (Plugin-scoped config should take precedence; document this behavior)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Plugin MUST provide metadata in `.claude-plugin/marketplace.json` including name, description, version, and author
- **FR-002**: Plugin MUST define MCP server configuration inline in `plugin.json` (chosen approach for simplicity) or in separate `.mcp.json` file (alternative deferred post-MVP)
- **FR-003**: Plugin MUST support environment variable expansion for `NSIP_BASE_URL` and `NSIP_API_KEY` credentials; these variables are OPTIONAL for MCP server startup and only required when calling NSIP API tools
- **FR-004**: Plugin MUST automatically start the NSIP MCP server when enabled; if startup fails (e.g., Python not found, nsip-api-client package not installed), plugin enable operation MUST fail with diagnostic error and plugin MUST remain disabled; MCP server CAN start without credentials (credentials only needed when calling NSIP API tools)
- **FR-005**: Plugin MUST automatically stop the NSIP MCP server when disabled
- **FR-006**: Plugin MUST expose all 10 NSIP MCP tools when active
- **FR-007**: Plugin MUST provide at least 5 slash commands for common NSIP workflows (discover, lookup, profile, health, test-api)
- **FR-008**: Plugin MUST use `${CLAUDE_PLUGIN_ROOT}` for plugin-relative file paths in MCP server configuration
- **FR-009**: Plugin MUST include README.md with installation instructions, prerequisites, and usage examples
- **FR-010**: Plugin MUST include slash command documentation for each command with description and examples
- **FR-011**: Slash commands MUST call appropriate MCP tools and format output for readability
- **FR-012**: Slash commands MUST handle MCP tool errors gracefully and provide actionable error messages; successful operations remain silent
- **FR-013**: Plugin MUST be installable via standard Claude Code plugin commands (`/plugin marketplace add`, `/plugin install`)
- **FR-014**: Plugin MUST support toggling on/off without losing configuration (`/plugin disable`, `/plugin enable`)
- **FR-015**: Plugin MUST work across both terminal and VS Code versions of Claude Code
- **FR-016**: Plugin operations (install, enable, disable) MUST operate silently on success; errors MUST display diagnostic messages to users
- **FR-017**: Plugin MUST NOT expose credential values or names in error messages; authentication failures MUST display generic "Authentication failed" message only

### Key Entities

- **Plugin Metadata**: Defines plugin identity (name, version, description, author) and is stored in `.claude-plugin/marketplace.json`
- **MCP Server Configuration**: Specifies how to start the NSIP MCP server (command, args, environment variables) and integrates with Claude Code's MCP system
- **Slash Command**: User-facing shortcut that executes predefined prompts to accomplish common tasks using NSIP MCP tools
- **Environment Credentials**: User-provided NSIP API credentials (base URL, API key) that authenticate MCP server connections

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can install the plugin and start using NSIP tools in under 2 minutes (from `/plugin install` to first successful tool call)
- **SC-002**: Plugin installation reduces MCP server setup time by at least 80% compared to manual `.mcp.json` configuration
- **SC-003**: All 10 NSIP MCP tools are available and functional immediately after plugin installation without additional configuration
- **SC-004**: Users can complete common NSIP tasks (like "discover available breeds" or "lookup animal by ID") using slash commands in under 30 seconds
- **SC-005**: Plugin works consistently across terminal and VS Code installations with 100% feature parity
- **SC-006**: Plugin README provides credential configuration instructions with step-by-step examples, environment variable templates, and troubleshooting guidance; validation confirms all required elements present
- **SC-007**: Plugin enables/disables cleanly in 100% of test cases; successful operations complete without errors or orphaned processes; startup failures properly fail the enable operation with diagnostic errors
- **SC-008**: Common NSIP tasks (discover breeds, lookup animal by ID, view complete profile) complete in 5 or fewer user actions via slash commands

## Scope & Boundaries *(mandatory)*

### In Scope

- Plugin packaging and marketplace configuration for nsip-api-client
- MCP server auto-start/stop when plugin is enabled/disabled
- Environment variable support for NSIP credentials
- Slash commands for common NSIP workflows (discover, lookup, profile, health, test-api, search, traits, lineage, progeny)
- Documentation for installation and usage
- Support for both terminal and VS Code Claude Code installations

### Out of Scope

- Changes to existing nsip_mcp MCP server implementation (server works as-is)
- Changes to nsip_client Python library
- Custom credential management UI (users manage credentials via environment variables)
- Plugin auto-updates (users manually update via `/plugin update`)
- Multi-instance MCP server support (one MCP server per plugin)
- Slash command customization by users (commands are predefined)
- Integration with other Claude Code plugins or marketplaces beyond the standard system

### Assumptions & Dependencies

**Assumptions**:
- Claude Code plugin system supports MCP server definitions in `plugin.json` or `.mcp.json`
- Users have Python 3.10+ installed to run the MCP server
- Users have valid NSIP API credentials (base URL and API key)
- nsip-api-client package is already installed or installable via pip
- Plugin-relative paths using `${CLAUDE_PLUGIN_ROOT}` work as documented

**Dependencies**:
- Claude Code CLI/VS Code extension (plugin host environment)
- Python 3.10+ runtime
- nsip-api-client package (nsip_client and nsip_mcp modules)
- NSIP API availability (external dependency)
- GitHub repository hosting for marketplace distribution

**Constraints**:
- Plugin must follow Claude Code marketplace JSON schema
- MCP server configuration must use supported transport types (stdio, streamable-http, websocket)
- Slash commands are limited by Claude Code's slash command syntax and capabilities
- Plugin cannot modify Claude Code core behavior or other plugins
