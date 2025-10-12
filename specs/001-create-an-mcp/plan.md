# Implementation Plan: Context-Efficient API-to-MCP Gateway

**Branch**: `001-create-an-mcp` | **Date**: 2025-10-11 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-create-an-mcp/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build an MCP (Model Context Protocol) server that wraps the existing NSIP client library to expose sheep breeding API capabilities to LLM applications in a context-efficient manner. The server will automatically transform large API responses (>2000 tokens) into summaries while preserving key information, support multiple transport mechanisms (stdio, HTTP SSE, WebSockets), and implement intelligent caching to reduce redundant API calls. The primary technical approach uses FastMCP 2.0 for MCP server implementation, tiktoken (cl100k_base) for token counting, and uv/uvx for modern Python package management.

## Technical Context

**Language/Version**: Python 3.8+ (specified in existing project pyproject.toml)
**Primary Dependencies**:
- FastMCP 2.0 (MCP server framework)
- tiktoken (OpenAI tokenizer for cl100k_base encoding)
- Existing nsip_client library (NSIPClient class)
- uv/uvx (Astral's package/project manager for builds and tool execution)

**Storage**: In-memory caching with 1-hour TTL (no persistent storage per constraints)
**Testing**: pytest, pytest-cov (>90% coverage required), black, isort, flake8, mypy (existing quality gates)
**Target Platform**: Cross-platform (Linux, macOS, Windows) as MCP server executable
**Project Type**: Single project - CLI/server application wrapping existing library
**Performance Goals**:
- MCP tool discovery <5 seconds after connection (SC-001)
- Server startup <3 seconds (SC-007)
- Summarization reduces responses by 70% tokens (SC-002)
- Support 50 concurrent connections (SC-005)
- Cache hits reduce API calls by 40% (SC-006)

**Constraints**:
- Responses ≤2000 tokens: pass-through unmodified (FR-015)
- Responses >2000 tokens: summarize to 70% reduction (FR-005)
- Token counting via tiktoken cl100k_base (GPT-4 tokenizer)
- No authentication (NSIP API is public per FR-004)
- Session-based caching only (no persistent storage per constraints)
- Must support multiple transports: stdio (default), HTTP SSE, WebSockets via MCP_TRANSPORT env var (FR-008a)

**Scale/Scope**:
- 9 MCP tools (wrapping NSIPClient methods per FR-010)
- 50 concurrent client connections
- Single API source (NSIP client library)
- Production use with 99.5% uptime target (SC-008)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Simplicity and Clarity
- ✅ **Single Purpose**: MCP server has one clear purpose - expose NSIPClient via MCP protocol with context efficiency
- ✅ **No Circular Dependencies**: New MCP server wraps existing nsip_client library without modifying it
- ✅ **Clear Organization**: Server code isolated in dedicated module/package
- ✅ **Documented Complexity**: Context efficiency logic (token counting, summarization) justified in spec

### Principle II: Testing and Quality
- ✅ **>90% Coverage**: SC-011 mandates >90% coverage measured by pytest-cov
- ✅ **Unit Tests**: All MCP tools, caching, summarization logic will have unit tests
- ✅ **Integration Tests**: Multi-method workflows, transport mechanisms tested
- ✅ **Quality Gates**: SC-012 requires black, isort, flake8, mypy to pass
- ✅ **Error Scenarios**: FR-007 requires structured error messages - must test failure cases
- ✅ **Edge Cases**: Boundary conditions (exactly 2000 tokens, cache expiration) identified in spec

### Principle III: GitHub-First Distribution
- ✅ **GitHub Releases Only**: MCP server will be distributed via GitHub Releases (consistent with existing project)
- ✅ **No PyPI**: Constitution explicitly prohibits PyPI publishing
- ✅ **Installation via GitHub**: Users install via GitHub URLs using uv/uvx

### Principle IV: Code Quality Standards
- ✅ **black**: 100-char line length (existing standard)
- ✅ **isort**: black profile (existing standard)
- ✅ **flake8**: max-line-length=100 (existing standard)
- ✅ **mypy**: Type hints required (existing standard)
- ✅ **Python 3.8+**: Matches existing project requirement
- ✅ **Docstrings**: Required for all public MCP tools and server classes

### Principle V: Documentation Excellence
- ✅ **README Updates**: Must document MCP server installation, configuration, usage
- ✅ **API Documentation**: Each MCP tool requires docstrings with parameter descriptions
- ✅ **CHANGELOG**: Breaking changes tracked
- ✅ **Design Documentation**: This plan + research.md + data-model.md provide comprehensive design docs
- ✅ **Examples**: quickstart.md will provide usage examples

**Gate Status**: ✅ **PASS** - All constitutional requirements satisfied. No violations to justify.

### Post-Phase 1 Re-Evaluation

After completing Phase 1 design (research.md, data-model.md, contracts/, quickstart.md), all constitutional principles remain satisfied:

**Phase 1 Artifacts Confirm**:
- ✅ **Simplicity**: research.md documents clear technical decisions, data-model.md defines focused entities
- ✅ **Testing**: data-model.md includes validation rules, contracts/ define testable tool schemas
- ✅ **Distribution**: quickstart.md documents GitHub-only installation via uv/uvx
- ✅ **Quality**: All models include type hints, validation, docstrings per Principle IV standards
- ✅ **Documentation**: quickstart.md provides comprehensive usage guide, contracts/ provide API reference

**No New Violations Introduced**: Phase 1 design maintains constitutional compliance established in initial gate check.

## Project Structure

### Documentation (this feature)

```
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```
src/
├── nsip_client/           # Existing NSIP client library (unchanged)
│   ├── __init__.py
│   ├── client.py          # NSIPClient class with 9 public methods
│   ├── models.py          # Data models for NSIP responses
│   ├── exceptions.py      # Exception classes
│   └── cli.py             # Existing CLI tool
│
└── nsip_mcp/              # NEW: MCP server implementation
    ├── __init__.py
    ├── server.py          # FastMCP server setup and tool definitions
    ├── tools.py           # MCP tool wrappers for NSIPClient methods
    ├── context.py         # Context management (token counting, summarization)
    ├── cache.py           # In-memory cache with 1-hour TTL
    ├── transport.py       # Transport mechanism handling (stdio/HTTP SSE/WebSocket)
    └── cli.py             # MCP server CLI entry point

tests/
├── unit/
│   ├── test_nsip_client.py      # Existing client tests (unchanged)
│   ├── test_mcp_tools.py         # NEW: MCP tool unit tests
│   ├── test_context_manager.py  # NEW: Token counting/summarization tests
│   ├── test_cache.py             # NEW: Cache logic tests
│   └── test_transport.py         # NEW: Transport mechanism tests
│
└── integration/
    ├── test_nsip_workflows.py    # Existing workflows (unchanged)
    └── test_mcp_workflows.py     # NEW: End-to-end MCP server tests

pyproject.toml             # Updated with fastmcp, tiktoken dependencies
README.md                  # Updated with MCP server documentation
```

**Structure Decision**: Single project structure (Option 1) selected. The MCP server is implemented as a new package `nsip_mcp` alongside the existing `nsip_client` package. This maintains separation of concerns while keeping everything in one repository. The existing client library remains unchanged, following the constitution's principle of no circular dependencies. All MCP-specific code is isolated in the new `nsip_mcp` module.

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

**No violations identified** - Constitution Check passed all gates. All complexity is justified by functional requirements in the specification.
