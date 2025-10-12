# Feature Specification: Context-Efficient API-to-MCP Gateway

**Feature Branch**: `001-create-an-mcp`
**Created**: 2025-10-11
**Status**: Draft
**Input**: User description: "create an MCP server that will expose api capabilities in a context efficient manner, using python3, astral uv/uvx, fastMCP and the current best practices. Reasearch all technical capabilities with context7 and other current information provideres."

## Clarifications

### Session 2025-10-11

- Q: What configuration format should be used for defining API sources? → A: The API source is defined in the client library in the project (NSIP client library)
- Q: What should be the default cache expiration time for NSIP API responses? → A: 1 hour
- Q: Should the MCP server filter out contact information (phone, email, farm names) from API responses? → A: No, include all data
- Q: Which transport mechanism should the MCP server use for client communication? → A: Support multiple
- Q: What should be the maximum response size (in tokens/characters) before triggering summarization? → A: 2000 tokens
- Q: How should FR-005 (summarization) and FR-015 (pass-through) be reconciled? → A: FR-015 for ≤2000 tokens (pass-through), FR-005 for >2000 tokens (summarize)
- Q: Which tokenization method should be used to count the 2000-token threshold? → A: tiktoken cl100k_base (GPT-4)
- Q: How should users select which transport to use? → A: Environment variable MCP_TRANSPORT
- Q: How should cache keys be generated from API requests? → A: method_name:sorted_json_params
- Q: How should the "70% smaller" reduction be measured? → A: Token count (tiktoken cl100k_base)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - API Function Discovery and Invocation (Priority: P1)

Developers need to connect their LLM applications to existing APIs without manually writing integration code for each endpoint. They want the MCP server to automatically discover available API operations and make them callable by AI assistants with minimal configuration.

**Why this priority**: This is the core value proposition - enabling AI to interact with APIs through a standardized protocol. Without this, the server has no purpose.

**Independent Test**: Can be fully tested by configuring an API endpoint, having an LLM client discover available operations, and successfully invoking one operation with parameters. Delivers immediate value as a working API bridge.

**Acceptance Scenarios**:

1. **Given** an API endpoint is configured with the MCP server, **When** an LLM client connects, **Then** the client receives a list of available API operations with descriptions
2. **Given** an LLM has discovered API operations, **When** the LLM invokes an operation with valid parameters, **Then** the server executes the API call and returns results in a format the LLM can process
3. **Given** an API requires authentication, **When** credentials are configured in the server, **Then** API calls are automatically authenticated without exposing credentials to the LLM

---

### User Story 2 - Efficient Context Management (Priority: P2)

LLM applications need to work with API data without overwhelming the context window. Users want the server to intelligently manage how much information is loaded into the AI's context, providing summaries or paginated results for large datasets.

**Why this priority**: Context efficiency is what differentiates this from a simple API proxy. It's essential for production use but can be implemented after basic functionality works.

**Independent Test**: Can be tested by querying an API that returns large payloads, verifying that the MCP server returns appropriately-sized chunks with options to retrieve more detail. Works independently of other features.

**Acceptance Scenarios**:

1. **Given** an API returns large response payloads, **When** the LLM requests data, **Then** the server provides a summary with metadata about total size and options to retrieve full details
2. **Given** a dataset too large for context, **When** accessed through the MCP server, **Then** results are paginated with clear navigation options
3. **Given** an LLM needs specific data from a large response, **When** the server processes the API result, **Then** only relevant fields are included based on configurable filtering rules

---

### User Story 3 - Error Handling and Validation (Priority: P3)

Developers need clear, actionable error messages when API calls fail or when the LLM provides invalid parameters. The system should validate inputs before making API calls and translate technical errors into descriptions the LLM can understand and act upon.

**Why this priority**: Essential for production reliability but can be implemented after core functionality exists. Initial versions can have basic error handling.

**Independent Test**: Can be tested by attempting invalid operations and verifying error messages are clear and actionable. Works without other features.

**Acceptance Scenarios**:

1. **Given** an LLM attempts an API call with invalid parameters, **When** the server validates the request, **Then** a structured error describes what's invalid and how to correct it
2. **Given** an API call fails due to network or service issues, **When** the error occurs, **Then** the server translates technical errors into natural language explanations with suggested recovery actions
3. **Given** an API has rate limits, **When** limits are approached or exceeded, **Then** the server proactively communicates remaining capacity and suggests timing for retries

---

### User Story 4 - Multi-API Orchestration (Priority: P4)

Advanced users need to compose workflows that span multiple API endpoints or services. The MCP server should enable the LLM to chain operations across different APIs while maintaining context efficiency throughout the workflow.

**Why this priority**: Nice-to-have for advanced use cases. Most users will start with single-API scenarios.

**Independent Test**: Can be tested by configuring multiple API sources and executing a workflow that uses data from one API as input to another.

**Acceptance Scenarios**:

1. **Given** multiple APIs are configured, **When** an LLM executes a multi-step workflow, **Then** intermediate results are efficiently cached and reused across operations
2. **Given** APIs have dependencies (output of A feeds into B), **When** the LLM plans a workflow, **Then** the server provides information about which operations can be chained together

---

### Edge Cases

- What happens when an API endpoint becomes unavailable during operation? System should cache the last known state and provide graceful degradation
- How does the system handle APIs with inconsistent response formats (JSON vs XML vs plain text)? Should normalize to a consistent format for LLM consumption
- What happens when API rate limits are reached? Should queue requests with exponential backoff or return clear rate limit status
- How does system handle authentication token expiration? Should automatically refresh tokens when possible or prompt for re-authentication
- What happens when API responses contain binary data (images, files)? Should provide metadata about the resource with options to access it indirectly
- How does system handle long-running API operations? Should provide async operation status and polling capabilities
- What happens when API schemas change? Should detect breaking changes and alert users while maintaining backward compatibility where possible

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose API endpoints as callable tools in the Model Context Protocol format
- **FR-002**: System MUST automatically generate tool descriptions from API documentation or schema definitions
- **FR-003**: System MUST validate all inputs before forwarding requests to target APIs
- **FR-004**: NSIP API requires no authentication (public API per NSIPClient line 8). MCP server MUST NOT implement authentication handling. Reserved for future multi-API support (User Story 4)
- **FR-005**: System MUST transform API responses exceeding 2000 tokens into context-efficient formats suitable for LLM consumption through summarization (responses ≤2000 tokens pass through per FR-015)
- **FR-005a**: Summarization MUST preserve: unique identifiers (LpnId, Sire, Dam), breed information, total counts (TotalProgeny), contact information, top 3 traits by accuracy
- **FR-005b**: Summarization MUST omit: traits with accuracy <50, redundant nested structures, detailed metadata unless specifically requested
- **FR-006**: System MUST support pagination for large result sets with clear navigation options
- **FR-007**: System MUST provide structured error messages that LLMs can interpret and act upon
- **FR-008**: System MUST support multiple concurrent LLM client connections
- **FR-008a**: System MUST support multiple transport mechanisms for client communication (stdio, HTTP SSE, WebSockets) selectable via MCP_TRANSPORT environment variable (values: "stdio" [default], "http-sse", "websocket")
- **FR-009**: System MUST cache frequently accessed API responses to reduce redundant calls
- **FR-010**: System MUST expose the existing NSIP client library methods as MCP tools:
  - `get_date_last_updated()` → Tool: `nsip_get_last_update`
  - `get_available_breed_groups()` → Tool: `nsip_list_breeds`
  - `get_statuses_by_breed_group()` → Tool: `nsip_get_statuses`
  - `get_trait_ranges_by_breed(breed_id)` → Tool: `nsip_get_trait_ranges`
  - `search_animals(breed_id, page, page_size, search_criteria)` → Tool: `nsip_search_animals`
  - `get_animal_details(search_string)` → Tool: `nsip_get_animal`
  - `get_lineage(lpn_id)` → Tool: `nsip_get_lineage`
  - `get_progeny(lpn_id, page, page_size)` → Tool: `nsip_get_progeny`
  - `search_by_lpn(lpn_id)` → Tool: `nsip_search_by_lpn` (convenience method combining details+lineage+progeny)
- **FR-011**: System MUST log all API interactions for debugging and auditing purposes
- **FR-012**: System MUST respect API rate limits and provide feedback about available capacity
- **FR-013**: System MUST support both synchronous and asynchronous API operations
- **FR-014**: System MUST provide health check endpoints for monitoring server and API availability
- **FR-015**: System MUST pass through complete API responses unmodified when ≤2000 tokens (no filtering of contact information or other fields; responses >2000 tokens are summarized per FR-005)

### Acceptance Criteria Examples

The following examples illustrate testable acceptance criteria for key functional requirements:

- **FR-001 Acceptance**: When an LLM client connects to the MCP server, the client MUST receive a list of tools including all 9 NSIP tools (nsip_get_last_update, nsip_list_breeds, nsip_get_statuses, nsip_get_trait_ranges, nsip_search_animals, nsip_get_animal, nsip_get_lineage, nsip_get_progeny, nsip_search_by_lpn) with JSON schema definitions conforming to MCP specification

- **FR-005 Acceptance**: Given an API response containing 3500 tokens (measured by tiktoken cl100k_base), when the MCP server processes it, then the response MUST be summarized to ≤1050 tokens (70% reduction) while preserving all fields specified in FR-005a (identifiers, breed info, total counts, contact info, top 3 traits by accuracy)

- **FR-010 Acceptance**: When invoking the `nsip_get_animal` tool with parameter `{"search_string": "6####92020###249"}`, the MCP server MUST call NSIPClient.get_animal_details("6####92020###249") and return the result without modification if response ≤2000 tokens

- **FR-015 Acceptance**: Given an API response of 1850 tokens containing contact information (phone, email, farm names), when processed by the MCP server, then all contact information fields MUST be present in the returned response without filtering or omission

### Key Entities

- **API Source**: The existing NSIP client library (NSIPClient class) that the MCP server wraps; includes methods for animal search, details retrieval, lineage queries, and breed group operations
- **Tool Definition**: MCP-formatted description of an API operation; includes operation name, description, required parameters, optional parameters, expected response format, and error conditions
- **Context Window**: Represents the amount of information being tracked for efficient context management; includes size limits (maximum 2000 tokens per response before summarization, counted using tiktoken cl100k_base GPT-4 tokenizer), priority rules for what to include, and strategies for summarization
- **Authentication Credential**: Secure storage of API access tokens or keys; includes credential type, expiration info, refresh capabilities, and scope of access
- **Response Cache**: Temporary storage of API responses with 1-hour expiration; includes cache key (format: "method_name:sorted_json_params", e.g., "get_animal_details:{'lpn_id':'123'}"), expiration time (default 3600 seconds), size, and access frequency for optimization
- **Request Validation Rule**: Schema that defines valid inputs for each API operation; includes parameter types, constraints, required vs optional fields, and validation error messages

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: LLM clients can discover and call any configured API operation within 5 seconds of connection
- **SC-002**: API response summaries are 70% smaller (measured by token count using tiktoken cl100k_base) than full payloads while retaining key information needed for LLM decision-making
- **SC-003**: 95% of invalid requests are caught by validation before reaching the target API
- **SC-004**: Error messages from API failures are successfully interpreted by LLMs to retry with corrected parameters in 80% of cases
- **SC-005**: System supports at least 50 concurrent LLM client connections without degradation
- **SC-006**: Cached responses reduce redundant API calls by at least 40% in typical usage patterns
- **SC-007**: Server startup time is under 3 seconds for configurations with up to 10 API sources
- **SC-008**: System maintains 99.5% uptime over 30-day periods (excluding downstream API availability)
- **SC-009**: All API interactions are logged with sufficient detail for troubleshooting within 100ms of completion
- **SC-010**: LLM clients receive status updates for long-running operations (>5 seconds) at least every 2 seconds
- **SC-011**: Test coverage MUST exceed 90% for all MCP server modules (measured by pytest-cov)
- **SC-012**: All quality gates (black, isort, flake8, mypy) MUST pass before merge

## Assumptions *(mandatory)*

- APIs being integrated provide either OpenAPI/Swagger specifications or comprehensive documentation for schema generation
- Target APIs support standard HTTP methods (GET, POST, PUT, DELETE) and return structured data (JSON preferred)
- Authentication methods used by target APIs are industry-standard (API keys, OAuth 2.0, Bearer tokens)
- LLM clients connecting to the MCP server support the official Model Context Protocol specification
- The server will run in an environment with stable network connectivity to target APIs
- Users have appropriate authorization to access the APIs they configure with the MCP server
- API rate limits are reasonable for typical LLM interaction patterns (at least 60 requests per minute)
- Server will be deployed in an environment with adequate resources (minimum 1 CPU core, 512MB RAM)
- Configuration changes require server restart (hot-reloading is not required for initial version)
- Developers using the server have basic understanding of API concepts (endpoints, methods, authentication)

## Dependencies *(mandatory)*

- Availability and stability of target APIs being integrated
- Target APIs must provide accessible documentation or machine-readable schemas
- Network connectivity between MCP server and target APIs
- Authentication credentials with appropriate permissions for target APIs
- LLM client applications that implement Model Context Protocol
- Adequate server resources for concurrent operations and caching
- Error reporting requires APIs to return structured error responses (not just HTTP status codes)
- Context efficiency features depend on APIs returning predictable, well-structured data formats

## Constraints *(mandatory)*

- System must not store sensitive user data beyond the active session (cache only)
- Must comply with rate limits and terms of service of all integrated APIs
- Cannot modify or intercept API responses in ways that violate API provider policies
- Server must handle API timeouts without blocking other concurrent operations
- Configuration file size is limited to reasonable limits for parsing (under 10MB)
- Server must operate in environments where direct internet access may be restricted by firewalls
- Memory usage for caching must be bounded to prevent resource exhaustion
- Log file growth must be manageable (rotation or size limits required)
- Cannot guarantee transaction atomicity across multiple API calls to different services
- Must respect API authentication token lifetimes and cannot extend them

## Out of Scope *(mandatory)*

- Building a graphical user interface for configuration management
- Providing a hosted/cloud version of the MCP server (deployment is user responsibility)
- Creating AI models or LLM clients (server only exposes APIs to existing LLM applications)
- Implementing API mocking or simulation capabilities for testing
- Data transformation beyond context efficiency (complex ETL pipelines)
- Long-term persistent storage of API responses (only session-based caching)
- API versioning management or migration tools
- Generating API documentation from the MCP server's perspective
- Monitoring and alerting infrastructure (external tools should be used)
- Load balancing across multiple API endpoints
- Custom authentication protocol development (only standard methods supported)
- Integration with specific LLM platforms beyond MCP standard compliance
- Billing or usage tracking for API consumption
- Automated API discovery without manual configuration
