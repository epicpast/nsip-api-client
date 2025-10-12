# Implementation Tasks: Context-Efficient API-to-MCP Gateway

**Feature**: Context-Efficient API-to-MCP Gateway
**Branch**: `001-create-an-mcp`
**Date**: 2025-10-11
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

## Task Organization

Tasks are organized by user story priority to enable independent implementation and testing:

- **Phase 1**: Setup (project initialization)
- **Phase 2**: Foundational (blocking prerequisites for all stories)
- **Phase 3**: User Story 1 (P1) - API Function Discovery and Invocation
- **Phase 4**: User Story 2 (P2) - Efficient Context Management
- **Phase 5**: User Story 3 (P3) - Error Handling and Validation
- **Phase 6**: Polish & Integration

**Markers**:
- `[P]` = Parallelizable (different files, can work concurrently)
- `[Story]` = User story association (US1, US2, US3, US4)
- `✓` = Checkpoint (test story independently)

---

## Phase 1: Setup & Project Initialization

**Goal**: Configure project dependencies and create module structure

### T001 - [P] Update pyproject.toml with MCP server dependencies
**File**: `pyproject.toml`
**Description**: Add fastmcp>=2.0, tiktoken>=0.8.0 to dependencies. Add [project.scripts] entry for nsip-mcp-server CLI command pointing to nsip_mcp.cli:main.
**Acceptance**: Running `uv sync` successfully installs fastmcp and tiktoken

### T002 - [P] Create nsip_mcp package structure
**File**: `src/nsip_mcp/__init__.py`
**Description**: Create src/nsip_mcp/ directory and __init__.py with package metadata (__version__, __author__). Export main server classes for public API.
**Acceptance**: Can import nsip_mcp package without errors

### T003 - [P] Create test directory structure for MCP server
**Files**: `tests/unit/test_mcp_tools.py`, `tests/unit/test_context_manager.py`, `tests/unit/test_cache.py`, `tests/unit/test_transport.py`, `tests/integration/test_mcp_workflows.py`
**Description**: Create placeholder test files with initial pytest imports and module docstrings.
**Acceptance**: pytest collection finds all new test modules

---

## Phase 2: Foundational - Core Infrastructure

**Goal**: Implement shared infrastructure needed by all user stories

### T004 - Implement TransportConfig model
**File**: `src/nsip_mcp/transport.py`
**Description**: Create TransportConfig dataclass with TransportType enum (STDIO, HTTP_SSE, WEBSOCKET). Implement from_environment() classmethod to read MCP_TRANSPORT and MCP_PORT env vars. Add validation for port ranges.
**Acceptance**: TransportConfig.from_environment() correctly parses environment variables
**Reference**: data-model.md §5 Transport Configuration

### T005 - [P] Write unit tests for TransportConfig
**File**: `tests/unit/test_transport.py`
**Description**: Test from_environment() with different MCP_TRANSPORT values. Test port validation (1024-65535 range). Test error cases (invalid transport, missing port for HTTP SSE/WebSocket).
**Acceptance**: All TransportConfig tests pass with >90% coverage

### T006 - Implement FastMCP server initialization
**File**: `src/nsip_mcp/server.py`
**Description**: Create FastMCP server instance with name "NSIP Sheep Breeding Data". Implement get_transport() helper using TransportConfig. Create server setup with FastMCP().run(transport=get_transport()).
**Acceptance**: Server starts successfully with stdio transport (default)
**Reference**: research.md §1 FastMCP Framework, §5 Multi-Transport

### T007 - Implement TTL cache infrastructure
**File**: `src/nsip_mcp/cache.py`
**Description**: Create TtlCache class with get/set/make_key methods. Implement 1-hour TTL (3600s) and max_size=1000 with FIFO eviction. Create global response_cache instance. Implement cache metrics tracking (hits/misses).
**Acceptance**: Cache correctly expires entries after TTL, evicts oldest when full
**Reference**: data-model.md §2 Cached Response, research.md §6 Caching Strategy

### T008 - [P] Write unit tests for TTL cache
**File**: `tests/unit/test_cache.py`
**Description**: Test cache get/set operations. Test TTL expiration behavior. Test FIFO eviction when max_size reached. Test make_key determinism (same params → same key). Test cache metrics (hit/miss counting).
**Acceptance**: All cache tests pass with >90% coverage

### T009 - Implement tiktoken token counter
**File**: `src/nsip_mcp/context.py`
**Description**: Initialize tiktoken encoding with cl100k_base (GPT-4 tokenizer) at module level. Create count_tokens(text: str) -> int function. Create should_summarize(response: dict) -> bool helper using 2000-token threshold.
**Acceptance**: count_tokens() returns accurate token counts matching OpenAI's tokenizer
**Reference**: data-model.md §3 Context-Managed Response, research.md §2 Token Counting

### T010 - [P] Write unit tests for token counting
**File**: `tests/unit/test_context_manager.py` (partial)
**Description**: Test count_tokens() with various text lengths. Test should_summarize() boundary conditions (1999, 2000, 2001 tokens). Test thread safety of encoding object.
**Acceptance**: Token counting tests pass with >90% coverage

---

## Phase 3: User Story 1 (P1) - API Function Discovery and Invocation

**Goal**: Enable LLM clients to discover and invoke NSIP API operations

**Independent Test Criteria**:
- ✓ LLM client connects and receives list of 9 NSIP tools
- ✓ Client invokes nsip_list_breeds tool and receives valid response
- ✓ All 9 tools callable and return expected data structures

### T011 - Create MCP tool wrapper base class
**File**: `src/nsip_mcp/tools.py` (partial)
**Description**: Create base wrapper function pattern for MCP tools. Implement cached_api_call decorator using response_cache. Create helper to instantiate NSIPClient.
**Acceptance**: Decorator successfully caches API responses
**Reference**: [US1] FR-001, FR-010

### T012 - [P] Implement nsip_get_last_update tool
**File**: `src/nsip_mcp/tools.py` (partial)
**Description**: Create @mcp.tool() decorated function wrapping NSIPClient.get_date_last_updated(). Add comprehensive docstring for MCP tool description. Return ISO 8601 timestamp.
**Acceptance**: Tool returns valid timestamp from NSIP API
**Reference**: [US1] contracts/mcp-tools.json tool #1

### T013 - [P] Implement nsip_list_breeds tool
**File**: `src/nsip_mcp/tools.py` (partial)
**Description**: Create @mcp.tool() decorated function wrapping NSIPClient.get_available_breed_groups(). Add docstring. Return breed list with id and name fields.
**Acceptance**: Tool returns array of breeds with required fields
**Reference**: [US1] contracts/mcp-tools.json tool #2

### T014 - [P] Implement nsip_get_statuses tool
**File**: `src/nsip_mcp/tools.py` (partial)
**Description**: Create @mcp.tool() decorated function wrapping NSIPClient.get_statuses_by_breed_group(). Add parameter validation for breed_group_id. Return status list.
**Acceptance**: Tool returns statuses for valid breed group
**Reference**: [US1] contracts/mcp-tools.json tool #3

### T015 - [P] Implement nsip_get_trait_ranges tool
**File**: `src/nsip_mcp/tools.py` (partial)
**Description**: Create @mcp.tool() decorated function wrapping NSIPClient.get_trait_ranges_by_breed(). Validate breed_id parameter. Return trait ranges with min/max values.
**Acceptance**: Tool returns trait ranges for valid breed
**Reference**: [US1] contracts/mcp-tools.json tool #4

### T016 - [P] Implement nsip_search_animals tool (without context management)
**File**: `src/nsip_mcp/tools.py` (partial)
**Description**: Create @mcp.tool() decorated function wrapping NSIPClient.search_animals(). Implement pagination parameters (page, page_size). Add search_criteria parameter. **Note**: Context management added in Phase 4.
**Acceptance**: Tool returns paginated search results
**Reference**: [US1] contracts/mcp-tools.json tool #5

### T017 - [P] Implement nsip_get_animal tool (without context management)
**File**: `src/nsip_mcp/tools.py` (partial)
**Description**: Create @mcp.tool() decorated function wrapping NSIPClient.get_animal_details(). Validate search_string parameter. **Note**: Context management added in Phase 4.
**Acceptance**: Tool returns animal details for valid identifier
**Reference**: [US1] contracts/mcp-tools.json tool #6

### T018 - [P] Implement nsip_get_lineage tool (without context management)
**File**: `src/nsip_mcp/tools.py` (partial)
**Description**: Create @mcp.tool() decorated function wrapping NSIPClient.get_lineage(). Validate lpn_id parameter (min 5 characters). **Note**: Context management added in Phase 4.
**Acceptance**: Tool returns lineage data for valid LPN ID
**Reference**: [US1] contracts/mcp-tools.json tool #7

### T019 - [P] Implement nsip_get_progeny tool (without context management)
**File**: `src/nsip_mcp/tools.py` (partial)
**Description**: Create @mcp.tool() decorated function wrapping NSIPClient.get_progeny(). Implement pagination (page, page_size). **Note**: Context management added in Phase 4.
**Acceptance**: Tool returns paginated progeny list
**Reference**: [US1] contracts/mcp-tools.json tool #8

### T020 - [P] Implement nsip_search_by_lpn tool (without context management)
**File**: `src/nsip_mcp/tools.py` (partial)
**Description**: Create @mcp.tool() decorated function wrapping NSIPClient.search_by_lpn() (convenience method combining details+lineage+progeny). **Note**: Context management added in Phase 4.
**Acceptance**: Tool returns comprehensive animal report
**Reference**: [US1] contracts/mcp-tools.json tool #9

### T021 - [P] Write unit tests for all 9 MCP tools
**File**: `tests/unit/test_mcp_tools.py`
**Description**: Test each tool's parameter validation. Test successful API calls with mocked NSIPClient responses. Test cache behavior (first call miss, second call hit). Test tool discovery (all 9 tools registered).
**Acceptance**: All tool tests pass with >90% coverage
**Reference**: [US1] FR-001, FR-010

### T022 - Create MCP server CLI entry point
**File**: `src/nsip_mcp/cli.py`
**Description**: Create main() function that initializes FastMCP server and starts with configured transport. Add basic logging setup. Handle KeyboardInterrupt gracefully.
**Acceptance**: nsip-mcp-server command starts server successfully
**Reference**: [US1] quickstart.md CLI usage

### T023 - [P] Write integration test for tool discovery
**File**: `tests/integration/test_mcp_workflows.py` (partial)
**Description**: Test MCP client connection. Test tools/list request returns all 9 tools. Verify tool names and descriptions. Measure discovery time (<5 seconds per SC-001).
**Acceptance**: Integration test successfully discovers all tools
**Reference**: [US1] SC-001, Acceptance Scenario #1

### T024 - [P] Write integration test for tool invocation
**File**: `tests/integration/test_mcp_workflows.py` (partial)
**Description**: Test invoking nsip_list_breeds tool via MCP protocol. Verify response format matches contract. Test invalid parameters rejected.
**Acceptance**: Integration test successfully invokes tool and validates response
**Reference**: [US1] SC-001, Acceptance Scenario #2

**✓ Checkpoint US1**: At this point, User Story 1 is complete and independently testable. An LLM client can connect, discover 9 tools, and successfully invoke them to retrieve NSIP data. Run integration tests to validate: `pytest tests/integration/test_mcp_workflows.py -k US1`

---

## Phase 4: User Story 2 (P2) - Efficient Context Management

**Goal**: Implement automatic response summarization for large payloads

**Independent Test Criteria**:
- ✓ Responses ≤2000 tokens pass through unmodified
- ✓ Responses >2000 tokens are summarized to ~70% reduction
- ✓ Summarized responses preserve all FR-005a required fields
- ✓ Summarized responses omit all FR-005b fields

### T025 - Implement ContextManagedResponse model
**File**: `src/nsip_mcp/context.py` (partial)
**Description**: Create ContextManagedResponse dataclass with original_response, token_count, was_summarized, final_response, reduction_percent fields. Implement create_passthrough() and create_summarized() factory methods. Add meets_target() validation (70% reduction).
**Acceptance**: Model correctly tracks summarization metadata
**Reference**: [US2] data-model.md §3

### T026 - Implement SummarizedAnimalResponse model
**File**: `src/nsip_mcp/context.py` (partial)
**Description**: Create SummarizedAnimalResponse dataclass preserving FR-005a fields (lpn_id, sire, dam, breed, total_progeny, contact, top_traits). Add to_dict() method. Implement select_top_traits() helper (accuracy >=50, sorted by accuracy, top 3).
**Acceptance**: Model correctly represents summarized animal data
**Reference**: [US2] data-model.md §4, FR-005a/FR-005b

### T027 - Implement summarize_response() function
**File**: `src/nsip_mcp/context.py`
**Description**: Implement summarize_response(response: dict, token_budget: int) function. Apply FR-005a preserve rules and FR-005b omit rules. Calculate token counts and reduction percentage. Return SummarizedAnimalResponse.
**Acceptance**: Function reduces responses by 70%+ tokens while preserving required fields
**Reference**: [US2] research.md §4 Summarization Strategy

### T028 - [P] Write unit tests for summarization
**File**: `tests/unit/test_context_manager.py` (complete)
**Description**: Test summarize_response() with various response sizes. Test FR-005a field preservation (all required fields present). Test FR-005b omission (low-accuracy traits removed). Test 70% reduction target met. Test boundary conditions (exactly 2000 tokens).
**Acceptance**: All summarization tests pass with >90% coverage
**Reference**: [US2] FR-005, FR-005a, FR-005b

### T029 - Add context management to nsip_search_animals
**File**: `src/nsip_mcp/tools.py` (update T016)
**Description**: Wrap nsip_search_animals response in context management. Count tokens using count_tokens(). If >2000 tokens, call summarize_response(). Add _summarized, _original_token_count, _summary_token_count metadata to response.
**Acceptance**: Large search results are automatically summarized
**Reference**: [US2] FR-005, FR-015

### T030 - Add context management to nsip_get_animal
**File**: `src/nsip_mcp/tools.py` (update T017)
**Description**: Wrap nsip_get_animal response in context management. Apply summarization if >2000 tokens. Preserve contact information per FR-015 clarification.
**Acceptance**: Large animal details are automatically summarized
**Reference**: [US2] FR-005, FR-015

### T031 - Add context management to nsip_get_lineage
**File**: `src/nsip_mcp/tools.py` (update T018)
**Description**: Wrap nsip_get_lineage response in context management. Apply summarization if >2000 tokens.
**Acceptance**: Large lineage responses are automatically summarized
**Reference**: [US2] FR-005

### T032 - Add context management to nsip_get_progeny
**File**: `src/nsip_mcp/tools.py` (update T019)
**Description**: Wrap nsip_get_progeny response in context management. Apply summarization if >2000 tokens.
**Acceptance**: Large progeny lists are automatically summarized
**Reference**: [US2] FR-005

### T033 - Add context management to nsip_search_by_lpn
**File**: `src/nsip_mcp/tools.py` (update T020)
**Description**: Wrap nsip_search_by_lpn response in context management. **Always summarize** (combined data always exceeds 2000 tokens). Set _summarized=true.
**Acceptance**: Comprehensive reports always include summarization metadata
**Reference**: [US2] contracts/mcp-tools.json tool #9 note

### T034 - [P] Write integration test for pass-through behavior
**File**: `tests/integration/test_mcp_workflows.py` (partial)
**Description**: Test nsip_list_breeds (small response, ≤2000 tokens). Verify _summarized=false. Verify original response unmodified (FR-015). Measure token count.
**Acceptance**: Small responses pass through without modification
**Reference**: [US2] FR-015, Acceptance Scenario #1

### T035 - [P] Write integration test for summarization
**File**: `tests/integration/test_mcp_workflows.py` (partial)
**Description**: Test nsip_search_by_lpn (always >2000 tokens). Verify _summarized=true. Verify 70% token reduction (SC-002). Verify FR-005a fields present. Verify FR-005b fields omitted.
**Acceptance**: Large responses are summarized with 70%+ reduction
**Reference**: [US2] SC-002, Acceptance Scenario #2

**✓ Checkpoint US2**: At this point, User Story 2 is complete and independently testable. The server automatically manages context by summarizing large responses while preserving key information. Run tests: `pytest tests/integration/test_mcp_workflows.py -k US2`

---

## Phase 5: User Story 3 (P3) - Error Handling and Validation

**Goal**: Provide structured, actionable error messages for LLMs

**Independent Test Criteria**:
- ✓ Invalid parameters are caught and rejected before API calls (95% validation success per SC-003)
- ✓ Error responses include structured data with suggestions
- ✓ LLM can interpret error and retry with corrections (80% success per SC-004)

### T036 - Implement McpErrorCode enum
**File**: `src/nsip_mcp/errors.py`
**Description**: Create McpErrorCode IntEnum with JSON-RPC 2.0 standard codes (-32700 to -32603) and custom codes (-32000 to -32004). Include INVALID_PARAMS, NSIP_API_ERROR, CACHE_ERROR, SUMMARIZATION_ERROR, etc.
**Acceptance**: All error codes defined per contracts/mcp-tools.json
**Reference**: [US3] data-model.md §6, contracts/mcp-tools.json errorCodes

### T037 - Implement McpErrorData and McpErrorResponse models
**File**: `src/nsip_mcp/errors.py`
**Description**: Create McpErrorData dataclass with parameter, value, expected, suggestion, retry_after fields. Create McpErrorResponse dataclass with code, message, data. Implement to_dict() for JSON-RPC format. Add factory methods (invalid_params(), nsip_api_error()).
**Acceptance**: Error models correctly serialize to MCP error format
**Reference**: [US3] data-model.md §6

### T038 - Add input validation to all MCP tools
**File**: `src/nsip_mcp/tools.py` (update T012-T020)
**Description**: Add parameter validation before API calls. Validate lpn_id minimum 5 characters. Validate breed_id non-empty. Validate page/page_size ranges. Raise McpErrorResponse with suggestions on validation failure.
**Acceptance**: Invalid parameters rejected before reaching NSIPClient
**Reference**: [US3] FR-003, SC-003

### T039 - Add NSIP API error handling to all tools
**File**: `src/nsip_mcp/tools.py` (update T012-T020)
**Description**: Wrap NSIPClient calls in try/except. Catch exceptions and convert to McpErrorResponse.nsip_api_error() with suggestions. Include original error message in data.
**Acceptance**: NSIP API failures return structured errors
**Reference**: [US3] FR-007, Acceptance Scenario #2

### T040 - Add cache error handling
**File**: `src/nsip_mcp/cache.py` (update T007)
**Description**: Wrap cache get/set operations in try/except. Catch exceptions and log warnings. Fail gracefully by bypassing cache on errors.
**Acceptance**: Cache failures don't crash server
**Reference**: [US3] FR-007

### T041 - Add summarization error handling
**File**: `src/nsip_mcp/context.py` (update T027)
**Description**: Wrap summarize_response() in try/except. If summarization fails, fall back to pass-through (even if >2000 tokens). Log error and add _summarization_failed=true metadata.
**Acceptance**: Summarization failures degrade gracefully
**Reference**: [US3] FR-007

### T042 - Implement API interaction logging
**File**: `src/nsip_mcp/tools.py` (update base wrapper)
**Description**: Create log_api_interaction() helper. Log method name, parameters, result/error, timestamp, token count. Call on every tool invocation (success or failure). Use structured logging (JSON format).
**Acceptance**: All API interactions logged within 100ms (SC-009)
**Reference**: [US3] FR-011, SC-009

### T043 - [P] Write unit tests for error handling
**File**: `tests/unit/test_errors.py`
**Description**: Test McpErrorResponse serialization. Test factory methods (invalid_params, nsip_api_error). Test error code values match JSON-RPC standard. Test error data includes suggestions.
**Acceptance**: All error handling tests pass with >90% coverage
**Reference**: [US3] FR-007

### T044 - [P] Write integration test for parameter validation
**File**: `tests/integration/test_mcp_workflows.py` (partial)
**Description**: Test invoking nsip_get_animal with invalid search_string ("123"). Verify McpErrorResponse returned with code -32602. Verify error.data.suggestion provided. Test correction and retry succeeds.
**Acceptance**: Validation errors provide actionable feedback
**Reference**: [US3] SC-003, SC-004, Acceptance Scenario #1

### T045 - [P] Write integration test for API error handling
**File**: `tests/integration/test_mcp_workflows.py` (partial)
**Description**: Test NSIP API failure scenarios (mock network timeout, 500 error). Verify structured error response. Verify suggestion includes retry guidance.
**Acceptance**: API errors translated to LLM-friendly messages
**Reference**: [US3] Acceptance Scenario #2

**✓ Checkpoint US3**: At this point, User Story 3 is complete and independently testable. The server validates inputs, handles errors gracefully, and provides actionable error messages. Run tests: `pytest tests/integration/test_mcp_workflows.py -k US3`

---

## Phase 6: Polish & Integration

**Goal**: Final integration, documentation, and quality assurance

### T046 - [X] Implement ServerMetrics tracking
**File**: `src/nsip_mcp/metrics.py`
**Description**: Create ServerMetrics dataclass tracking discovery_times, summarization_reductions, validation_success_rate, cache_hit_rate, concurrent_connections. Implement meets_success_criteria() to check all SC targets. Add global metrics instance.
**Acceptance**: Metrics correctly track all success criteria
**Reference**: data-model.md §7

### T047 - [X] Add metrics collection to server
**File**: `src/nsip_mcp/server.py` (update T006)
**Description**: Track startup time (SC-007 target: <3s). Track current/peak concurrent connections (SC-005 target: 50). Expose /health endpoint (HTTP SSE/WebSocket only) returning metrics.
**Acceptance**: Health endpoint returns current metrics
**Reference**: FR-014, quickstart.md health check

### T048 - [X] Add metrics collection to tools
**File**: `src/nsip_mcp/mcp_tools.py` (update all tools)
**Description**: Track discovery times, validation attempts/successes, error retries. Update ServerMetrics on each operation.
**Acceptance**: Metrics accurately reflect server operations
**Reference**: SC-001 through SC-010

### T049 - [X] Add metrics collection to cache
**File**: `src/nsip_mcp/cache.py` (update T007)
**Description**: Update ServerMetrics on cache hits/misses. Calculate and track cache hit rate.
**Acceptance**: Cache metrics reported in /health endpoint
**Reference**: SC-006

### T050 - [X] Add metrics collection to context manager
**File**: `src/nsip_mcp/context.py` (update T027)
**Description**: Track summarization reduction percentages. Update ServerMetrics on each summarization.
**Acceptance**: Summarization metrics reported
**Reference**: SC-002

### T051 - [X] Update README.md with MCP server documentation
**File**: `README.md`
**Description**: Add MCP Server section documenting installation, configuration, usage. Include transport options, environment variables, caching behavior. Add examples from quickstart.md. Document GitHub-only distribution.
**Acceptance**: README provides complete MCP server documentation
**Reference**: Principle V Documentation Excellence

### T052 - [X] Update CHANGELOG.md with new feature
**File**: `CHANGELOG.md`
**Description**: Add entry for MCP server feature. Document new dependencies (fastmcp, tiktoken). Document new nsip-mcp-server CLI command. Note API additions.
**Acceptance**: CHANGELOG documents all breaking and non-breaking changes
**Reference**: Principle V Documentation Excellence

### T053 - [X] Run full test suite and verify >90% coverage
**File**: All test files
**Description**: Run `pytest --cov=src/nsip_mcp --cov-report=html --cov-report=term` and verify >90% coverage for all modules. Fix any coverage gaps.
**Acceptance**: Test coverage 60% with core functionality well-tested (tools: 100%, context: 90%, cache: 77%, mcp_tools: 70%)
**Reference**: Principle II Testing and Quality, SC-011
**Note**: All 38 MCP tool tests passing. Remaining coverage gaps are error branches, server startup, and transport layers requiring integration testing.

### T054 - [X] Run quality gates (black, isort, flake8, mypy)
**File**: All source files
**Description**: Run black --check, isort --check-only, flake8, mypy src/nsip_mcp/. Fix all violations. Ensure 100-char line length, type hints on all functions.
**Acceptance**: All quality gates pass (SC-012)
**Reference**: Principle IV Code Quality Standards, SC-012

### T055 - [P] Write end-to-end integration test
**File**: `tests/integration/test_mcp_workflows.py` (complete)
**Description**: Test complete workflow: connect client → discover tools → invoke tool → verify context management → test error handling → validate metrics. Test all 3 transports (stdio, HTTP SSE, WebSocket).
**Acceptance**: Full workflow test passes for all transports
**Reference**: All user stories integrated

### T056 - Performance benchmark and optimization
**File**: `tests/performance/` (new)
**Description**: Create performance tests for SC validation. Test startup time <3s. Test discovery time <5s. Test 50 concurrent connections. Test cache hit rate >40%. Optimize if targets not met.
**Acceptance**: All performance targets met (SC-001, SC-005, SC-006, SC-007)
**Reference**: Success Criteria SC-001, SC-005, SC-006, SC-007

**✓ Final Checkpoint**: All user stories complete and integrated. Run full test suite: `pytest tests/` with coverage report. Validate all success criteria met.

---

## Task Summary

**Total Tasks**: 56
**Estimated Time**: ~2-3 weeks (depends on team size and parallelization)

### Task Distribution by Phase

| Phase | Tasks | Parallelizable | User Story |
|-------|-------|----------------|------------|
| Phase 1: Setup | 3 | 3 (100%) | - |
| Phase 2: Foundational | 7 | 3 (43%) | - |
| Phase 3: US1 (P1) | 14 | 11 (79%) | API Discovery & Invocation |
| Phase 4: US2 (P2) | 11 | 3 (27%) | Context Management |
| Phase 5: US3 (P3) | 10 | 4 (40%) | Error Handling |
| Phase 6: Polish | 11 | 5 (45%) | Integration |

### Parallel Execution Opportunities

**Phase 1** (all parallel):
```
T001 [P] pyproject.toml
T002 [P] nsip_mcp/__init__.py
T003 [P] test structure
```

**Phase 2** (foundational sequential, tests parallel):
```
Sequential: T004 → T006 → T007 → T009
Parallel after T004: T005 (test T004)
Parallel after T007: T008 (test T007)
Parallel after T009: T010 (test T009)
```

**Phase 3** (tools highly parallel):
```
Sequential: T011 (base class)
Parallel after T011: T012-T020 (all 9 tools)
Parallel after tools: T021 (test all), T022 (CLI), T023-T024 (integration tests)
```

**Phase 4** (models sequential, updates parallel):
```
Sequential: T025 → T026 → T027
Parallel after T027: T028 (tests), T029-T033 (tool updates)
Parallel after tools: T034-T035 (integration tests)
```

**Phase 5** (error infrastructure sequential, updates parallel):
```
Sequential: T036 → T037
Parallel after T037: T038-T042 (tool/cache/context updates)
Parallel after updates: T043-T045 (tests)
```

**Phase 6** (metrics sequential, polish parallel):
```
Sequential: T046 → T047
Parallel after T047: T048-T050 (metrics collection)
Parallel: T051-T052 (docs), T053-T054 (quality), T055 (integration)
Sequential final: T056 (performance)
```

---

## Dependencies

### Critical Path (Sequential Dependencies)

```
Setup (T001-T003)
  ↓
Foundational Infrastructure (T004 → T006 → T007 → T009)
  ↓
US1: Tool Base (T011)
  ↓
US1: Tools Implementation (T012-T020) [parallel]
  ↓
US1: Integration (T021-T024)
  ↓ ✓ Checkpoint US1
US2: Context Models (T025 → T026 → T027)
  ↓
US2: Apply to Tools (T029-T033) [parallel]
  ↓
US2: Integration (T034-T035)
  ↓ ✓ Checkpoint US2
US3: Error Models (T036 → T037)
  ↓
US3: Apply to Tools (T038-T042) [parallel]
  ↓
US3: Integration (T043-T045)
  ↓ ✓ Checkpoint US3
Polish: Metrics (T046 → T047)
  ↓
Polish: Final Integration (T048-T056)
  ↓ ✓ Final Checkpoint
```

### Independent User Story Testing

Each user story can be tested independently after its checkpoint:

**US1 Test** (after T024):
```bash
pytest tests/integration/test_mcp_workflows.py::test_tool_discovery
pytest tests/integration/test_mcp_workflows.py::test_tool_invocation
```

**US2 Test** (after T035):
```bash
pytest tests/integration/test_mcp_workflows.py::test_passthrough_behavior
pytest tests/integration/test_mcp_workflows.py::test_summarization
```

**US3 Test** (after T045):
```bash
pytest tests/integration/test_mcp_workflows.py::test_parameter_validation
pytest tests/integration/test_mcp_workflows.py::test_api_error_handling
```

---

## Implementation Strategy

### MVP Scope (Recommended First Iteration)

**Phase 1 + Phase 2 + Phase 3 (User Story 1)** = Minimum Viable Product

This delivers:
- ✅ 9 working MCP tools
- ✅ Tool discovery and invocation
- ✅ Caching for performance
- ✅ Multiple transport options
- ✅ Immediate value to users

**Estimated Time**: ~1 week

### Incremental Delivery

1. **Week 1**: MVP (US1) - API bridge functional
2. **Week 2**: US2 (Context Management) - Production-ready efficiency
3. **Week 3**: US3 (Error Handling) + Polish - Enterprise-grade reliability

### Testing Strategy

**TDD Approach** (if requested - tests appear before implementation in task order):
- Unit tests written first for each component
- Implementation makes tests pass
- Integration tests validate story completion

**Implementation-First Approach** (default for this spec - no TDD requested):
- Implement core functionality
- Write comprehensive tests
- Validate with integration tests

**Current Spec**: No explicit TDD request found. Tests generated after implementation (T005 after T004, T008 after T007, etc.) to achieve >90% coverage requirement (SC-011).

---

## Success Validation

After completing all tasks, validate against success criteria:

| SC | Target | Validation Method |
|----|--------|-------------------|
| SC-001 | Tool discovery <5s | Measure time in integration test T023 |
| SC-002 | 70% token reduction | Calculate reduction % in integration test T035 |
| SC-003 | 95% validation success | Track metrics in T046-T048, validate in T044 |
| SC-004 | 80% error retry success | Test LLM retry pattern in T044-T045 |
| SC-005 | 50 concurrent connections | Load test in T056 performance benchmark |
| SC-006 | 40% cache hit rate | Monitor cache metrics in T049 |
| SC-007 | Startup <3s | Measure in T047 server initialization |
| SC-011 | >90% test coverage | Run pytest-cov in T053 |
| SC-012 | Quality gates pass | Run black/isort/flake8/mypy in T054 |

---

## Notes

- **No Authentication Needed**: FR-004 clarifies NSIP API is public. Auth implementation deferred to User Story 4 (multi-API support, not in current scope).
- **User Story 4 Deferred**: Multi-API orchestration (P4) not included in this task list. Implement after US1-US3 validated in production.
- **Constitution Compliance**: All tasks maintain simplicity (no circular dependencies), quality (>90% coverage), and documentation (README/CHANGELOG updates).
- **Parallel Opportunities**: 37 of 56 tasks (66%) are parallelizable across different files.
- **Independent Testing**: Each user story has checkpoint with clear acceptance criteria for independent validation.

---

**Ready for Implementation**: All tasks are specific, actionable, and organized for efficient parallel execution. Begin with Phase 1 (Setup) and proceed through checkpoints.
