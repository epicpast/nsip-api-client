"""MCP tool implementations for NSIP API.

This module defines all MCP tools that wrap NSIPClient methods, providing
LLM-friendly interfaces with automatic caching, context management, and error handling.
"""

import logging
from typing import TYPE_CHECKING, Any, Awaitable, Optional, cast

from nsip_client.exceptions import (
    NSIPAPIError,
    NSIPNotFoundError,
    NSIPTimeoutError,
    NSIPValidationError,
)
from nsip_mcp.context import (
    ContextManagedResponse,
    summarize_response,
)
from nsip_mcp.errors import McpErrorResponse
from nsip_mcp.server import mcp
from nsip_mcp.tools import cached_api_call, get_nsip_client

# Import metrics for tracking (avoid circular import)
if TYPE_CHECKING:
    from nsip_mcp.metrics import ServerMetrics

server_metrics: Optional["ServerMetrics"] = None  # type: ignore[assignment]
try:
    from nsip_mcp.metrics import server_metrics as _server_metrics

    server_metrics = _server_metrics
except ImportError:
    pass

# Configure logging
logger = logging.getLogger(__name__)


def apply_context_management(response: dict[str, Any], summarize: bool = False) -> dict[str, Any]:
    """Apply context management (pass-through or summarization) to API response.

    IMPORTANT: Summarization is OPT-IN only. By default, all data is preserved.

    Args:
        response: Original API response
        summarize: If True, summarize the response. If False (default), pass through all data.

    Returns:
        Context-managed response with metadata

    Example:
        >>> response = {"lpn_id": "ABC123", "breed": "Katahdin"}
        >>> # Default: pass-through (no data loss)
        >>> managed = apply_context_management(response)
        >>> managed['_summarized']
        False
        >>> # Explicit summarization
        >>> managed = apply_context_management(response, summarize=True)
        >>> managed['_summarized']
        True
    """
    try:
        if summarize:
            # User explicitly requested summarization
            summarized = summarize_response(response)
            managed = ContextManagedResponse.create_summarized(response, summarized)
        else:
            # Default: pass through unmodified (no data loss)
            managed = ContextManagedResponse.create_passthrough(response)

        return managed.final_response

    except Exception as e:
        # Summarization failed - fall back to pass-through (T041)
        logger.warning(f"Summarization failed: {e}. Falling back to pass-through.")
        response["_summarization_failed"] = True
        response["_summarization_error"] = str(e)
        return response


def validate_lpn_id(lpn_id: str, parameter_name: str = "lpn_id") -> dict[str, Any] | None:
    """Validate LPN ID parameter.

    Args:
        lpn_id: LPN ID to validate
        parameter_name: Name of the parameter (for error messages)

    Returns:
        None if validation succeeds, error dict if validation fails

    Note:
        LPN IDs must be at least 5 characters long
    """
    if not lpn_id or not lpn_id.strip():
        # Record validation failure (SC-003)
        if server_metrics:
            server_metrics.record_validation(success=False)
        return McpErrorResponse.invalid_params(
            parameter=parameter_name,
            value=lpn_id,
            expected="Non-empty string",
            suggestion=f"Provide a valid {parameter_name} (e.g., '6####92020###249')",
        ).to_dict()

    if len(lpn_id.strip()) < 5:
        # Record validation failure (SC-003)
        if server_metrics:
            server_metrics.record_validation(success=False)
        # Sanitize user input to prevent log injection (M1)
        safe_input = lpn_id[:50].replace("\n", "").replace("\r", "")
        suggestion = (
            f"Provide full {parameter_name} " f"(e.g., '6####92020###249', not '{safe_input}')"
        )
        return McpErrorResponse.invalid_params(
            parameter=parameter_name,
            value=lpn_id,
            expected="Minimum 5 characters",
            suggestion=suggestion,
        ).to_dict()

    # Validation passed - record success (SC-003)
    if server_metrics:
        server_metrics.record_validation(success=True)

    return None


def validate_breed_id(breed_id: int, parameter_name: str = "breed_id") -> dict[str, Any] | None:
    """Validate breed ID parameter.

    Args:
        breed_id: Breed ID to validate
        parameter_name: Name of the parameter (for error messages)

    Returns:
        None if validation succeeds, error dict if validation fails

    Note:
        Breed IDs must be positive integers
    """
    if not isinstance(breed_id, int) or breed_id <= 0:
        # Record validation failure (SC-003)
        if server_metrics:
            server_metrics.record_validation(success=False)
        return McpErrorResponse.invalid_params(
            parameter=parameter_name,
            value=breed_id,
            expected="Positive integer",
            suggestion=f"Provide a valid {parameter_name} (e.g., 486 for Katahdin)",
        ).to_dict()

    # Validation passed - record success (SC-003)
    if server_metrics:
        server_metrics.record_validation(success=True)

    return None


def validate_pagination(page: int, page_size: int) -> dict[str, Any] | None:
    """Validate pagination parameters.

    Args:
        page: Page number (0-indexed)
        page_size: Results per page

    Returns:
        None if validation succeeds, error dict if validation fails
    """
    if page < 0:
        # Record validation failure (SC-003)
        if server_metrics:
            server_metrics.record_validation(success=False)
        return McpErrorResponse.invalid_params(
            parameter="page",
            value=page,
            expected="Non-negative integer (0-indexed)",
            suggestion=f"Use page=0 for first page, not page={page}",
        ).to_dict()

    if page_size < 1 or page_size > 100:
        # Record validation failure (SC-003)
        if server_metrics:
            server_metrics.record_validation(success=False)
        return McpErrorResponse.invalid_params(
            parameter="page_size",
            value=page_size,
            expected="Integer between 1 and 100",
            suggestion=f"Use page_size between 1-100 (e.g., 15), not {page_size}",
        ).to_dict()

    # Validation passed - record success (SC-003)
    if server_metrics:
        server_metrics.record_validation(success=True)

    return None


def handle_nsip_api_error(error: Exception, context: str = "") -> dict[str, Any]:
    """Convert NSIP API exceptions to structured MCP error responses.

    Args:
        error: Exception from NSIPClient
        context: Additional context about what operation failed

    Returns:
        Dict containing structured error response

    Example:
        >>> try:
        ...     client.get_animal_details("invalid")
        ... except NSIPNotFoundError as e:
        ...     return handle_nsip_api_error(e, "fetching animal details")
    """
    if isinstance(error, NSIPNotFoundError):
        error_response = McpErrorResponse.nsip_api_error(
            message=f"Animal not found: {context}",
            original_error=str(error),
        )
        logger.warning(f"NSIP API: Animal not found - {context}")
        return error_response.to_dict()

    elif isinstance(error, NSIPTimeoutError):
        error_response = McpErrorResponse.nsip_api_error(
            message=f"NSIP API timeout: {context}",
            original_error=str(error),
        )
        logger.error(f"NSIP API: Timeout - {context}")
        return error_response.to_dict()

    elif isinstance(error, NSIPValidationError):
        error_response = McpErrorResponse.validation_error(
            field="parameter", message=f"Validation failed: {str(error)}"
        )
        logger.warning(f"NSIP API: Validation error - {context}")
        return error_response.to_dict()

    elif isinstance(error, NSIPAPIError):
        error_response = McpErrorResponse.nsip_api_error(
            message=f"NSIP API error: {context}", original_error=str(error)
        )
        logger.error(f"NSIP API: Error - {context}")
        return error_response.to_dict()

    else:
        # Generic error
        error_response = McpErrorResponse.nsip_api_error(
            message=f"Unexpected error: {context}", original_error=str(error)
        )
        logger.exception(f"Unexpected error - {context}")
        return error_response.to_dict()


@mcp.tool()
@cached_api_call("get_date_last_updated")
def nsip_get_last_update() -> dict[str, Any]:
    """Get the date when the NSIP database was last updated.

    Returns:
        Dict containing the last update date

    Example:
        {'date': '09/23/2025'}
    """
    client = get_nsip_client()
    return client.get_date_last_updated()


@mcp.tool()
@cached_api_call("get_available_breed_groups")
def nsip_list_breeds() -> dict[str, Any]:
    """Get list of available breed groups in the NSIP database.

    Returns:
        Dict containing list of breed groups with their IDs and names,
        plus the individual breeds within each group.

    Example:
        {
            'success': True,
            'data': [
                {'id': 61, 'name': 'Range', 'breeds': [
                    {'id': 486, 'name': 'South African Meat Merino'},
                    {'id': 610, 'name': 'Targhee'}
                ]},
                {'id': 62, 'name': 'Maternal Wool', 'breeds': [...]},
                {'id': 64, 'name': 'Hair', 'breeds': [
                    {'id': 640, 'name': 'Katahdin'},
                    {'id': 641, 'name': 'St. Croix'}
                ]},
                {'id': 69, 'name': 'Terminal', 'breeds': [...]}
            ]
        }
    """
    client = get_nsip_client()
    breed_groups = client.get_available_breed_groups()
    return {
        "success": True,
        "data": [{"id": bg.id, "name": bg.name, "breeds": bg.breeds} for bg in breed_groups],
    }


@mcp.tool()
@cached_api_call("get_statuses_by_breed_group")
def nsip_get_statuses() -> dict[str, Any]:
    """Get list of available animal statuses.

    Returns:
        Dict containing list of status strings

    Example:
        {
            'success': True,
            'data': ['CURRENT', 'SOLD', 'DEAD', 'COMMERCIAL', 'CULL', 'EXPORTED']
        }
    """
    client = get_nsip_client()
    return {"success": True, "data": client.get_statuses_by_breed_group()}


@mcp.tool()
@cached_api_call("get_trait_ranges_by_breed")
def nsip_get_trait_ranges(breed_id: int) -> dict[str, Any]:
    """Get trait ranges (min/max values) for a specific breed.

    Args:
        breed_id: The breed ID to query (use nsip_list_breeds to find IDs)

    Returns:
        Dict mapping trait codes to min/max values, or error response

    Example:
        {
            'BWT': {'min': -0.713, 'max': 0.0},
            'WWT': {'min': -1.234, 'max': 2.456},
            ...
        }
    """
    try:
        # Validate breed_id parameter (T038)
        error = validate_breed_id(breed_id)
        if error:
            return error

        client = get_nsip_client()
        return client.get_trait_ranges_by_breed(breed_id)

    except Exception as e:
        # NSIP API error - convert to structured error (T039)
        return handle_nsip_api_error(e, f"getting trait ranges for breed {breed_id}")


@mcp.tool()
@cached_api_call("search_animals")
def nsip_search_animals(
    page: int = 0,
    page_size: int = 15,
    breed_id: int | None = None,
    sorted_trait: str | None = None,
    reverse: bool | None = None,
    search_criteria: dict[str, Any] | None = None,
    summarize: bool = False,
) -> dict[str, Any]:
    """Search for animals based on criteria with pagination.

    Args:
        page: Page number (0-indexed, default: 0)
        page_size: Number of results per page (1-100, default: 15)
        breed_id: Filter by breed ID (optional)
        sorted_trait: Trait to sort by, e.g. 'BWT', 'WWT' (optional)
        reverse: Sort in reverse order (optional)
        search_criteria: Additional filters as a dict (optional)
        summarize: If True, summarize large responses. Default False (no data loss)

    Returns:
        Dict containing results or error response. All data preserved by default.

    Example:
        {
            'results': [
                {'LpnId': '6####92020###249', 'Breed': 'Katahdin', ...},
                ...
            ],
            'total_count': 1523,
            'page': 0,
            'page_size': 15,
            '_summarized': False
        }
    """
    try:
        # Validate pagination parameters (T038)
        error = validate_pagination(page, page_size)
        if error:
            return error

        client = get_nsip_client()
        results = client.search_animals(
            page=page,
            page_size=page_size,
            breed_id=breed_id,
            sorted_trait=sorted_trait,
            reverse=reverse,
            search_criteria=search_criteria,
        )
        response = {
            "results": results.results,
            "total_count": results.total_count,
            "page": results.page,
            "page_size": results.page_size,
        }

        # Apply context management - NO automatic summarization (T029)
        return apply_context_management(response, summarize=summarize)

    except Exception as e:
        return handle_nsip_api_error(e, "searching animals")


@mcp.tool()
@cached_api_call("get_animal_details")
def nsip_get_animal(search_string: str, summarize: bool = False) -> dict[str, Any]:
    """Get detailed information about a specific animal.

    Args:
        search_string: LPN ID or registration number to search for
        summarize: If True, summarize the response. Default False (no data loss)

    Returns:
        Dict containing complete animal information. All data preserved by default.

    Example:
        {
            'lpn_id': '6####92020###249',
            'breed': 'Katahdin',
            'traits': {...},  # All traits included by default
            'contact_info': {...},
            '_summarized': False
        }
    """
    try:
        # Validate search_string parameter (T038)
        error = validate_lpn_id(search_string, parameter_name="search_string")
        if error:
            return error

        client = get_nsip_client()
        animal = client.get_animal_details(search_string)
        response = animal.to_dict()

        # Apply context management - NO automatic summarization (T030)
        return apply_context_management(response, summarize=summarize)

    except Exception as e:
        # NSIP API error - convert to structured error (T039)
        return handle_nsip_api_error(e, f"getting animal details for '{search_string}'")


@mcp.tool()
@cached_api_call("get_lineage")
def nsip_get_lineage(lpn_id: str, summarize: bool = False) -> dict[str, Any]:
    """Get the lineage/pedigree information for an animal.

    Args:
        lpn_id: The LPN ID of the animal
        summarize: If True, summarize the response. Default False (no data loss)

    Returns:
        Dict containing pedigree tree. All data preserved by default.

    Example:
        {
            'sire': '123ABC',
            'dam': '456DEF',
            'generations': [...],  # Full lineage included by default
            '_summarized': False
        }
    """
    try:
        # Validate lpn_id parameter (T038)
        error = validate_lpn_id(lpn_id)
        if error:
            return error

        client = get_nsip_client()
        lineage = client.get_lineage(lpn_id)
        response = lineage.to_dict()

        # Apply context management - NO automatic summarization (T031)
        return apply_context_management(response, summarize=summarize)

    except Exception as e:
        # NSIP API error - convert to structured error (T039)
        return handle_nsip_api_error(e, f"getting lineage for '{lpn_id}'")


@mcp.tool()
@cached_api_call("get_progeny")
def nsip_get_progeny(
    lpn_id: str, page: int = 0, page_size: int = 10, summarize: bool = False
) -> dict[str, Any]:
    """Get progeny (offspring) for a specific animal with pagination.

    Args:
        lpn_id: The LPN ID of the parent animal
        page: Page number (0-indexed, default: 0)
        page_size: Number of results per page (default: 10)
        summarize: If True, summarize the response. Default False (no data loss)

    Returns:
        Dict containing offspring records. All data preserved by default.

    Example:
        {
            'animals': [...],  # All offspring included by default
            'total_count': 6,
            'page': 0,
            'page_size': 10,
            '_summarized': False
        }
    """
    try:
        # Validate parameters (T038)
        error = validate_lpn_id(lpn_id)
        if error:
            return error

        error = validate_pagination(page, page_size)
        if error:
            return error

        client = get_nsip_client()
        progeny = client.get_progeny(lpn_id, page=page, page_size=page_size)
        response = {
            "animals": [animal.to_dict() for animal in progeny.animals],
            "total_count": progeny.total_count,
            "page": progeny.page,
            "page_size": progeny.page_size,
        }

        # Apply context management - NO automatic summarization (T032)
        return apply_context_management(response, summarize=summarize)

    except Exception as e:
        # NSIP API error - convert to structured error (T039)
        return handle_nsip_api_error(e, f"getting progeny for '{lpn_id}'")


@mcp.tool()
@cached_api_call("search_by_lpn")
def nsip_search_by_lpn(lpn_id: str, summarize: bool = False) -> dict[str, Any]:
    """Get complete profile for an animal by LPN ID (details + lineage + progeny).

    This is a convenience tool that combines three API calls into one comprehensive result.
    Note: Combined responses can be large. Use summarize=True to reduce token usage.

    Args:
        lpn_id: The LPN ID to search for
        summarize: If True, summarize the response. Default False (no data loss)

    Returns:
        Dict containing complete profile. All data preserved by default.

    Example (without summarization):
        {
            'details': {...},  # Full animal details
            'lineage': {...},  # Complete pedigree tree
            'progeny': {...},  # All offspring
            '_summarized': False
        }

    Example (with summarization):
        {
            'lpn_id': '6####92020###249',
            'breed': 'Katahdin',
            'sire': '123ABC',
            'dam': '456DEF',
            'total_progeny': 6,
            'top_traits': [
                {'trait': 'YWT', 'value': 2.1, 'accuracy': 0.92},
                ...
            ],
            '_summarized': True,
            '_reduction_percent': 78.85
        }
    """
    try:
        # Validate lpn_id parameter (T038)
        error = validate_lpn_id(lpn_id)
        if error:
            return error

        client = get_nsip_client()
        profile = client.search_by_lpn(lpn_id)
        response = {
            "details": profile["details"].to_dict(),
            "lineage": profile["lineage"].to_dict(),
            "progeny": {
                "animals": [animal.to_dict() for animal in profile["progeny"].animals],
                "total_count": profile["progeny"].total_count,
                "page": profile["progeny"].page,
                "page_size": profile["progeny"].page_size,
            },
        }

        # Apply context management - NO automatic summarization (T033)
        return apply_context_management(response, summarize=summarize)

    except Exception as e:
        # NSIP API error - convert to structured error (T039)
        return handle_nsip_api_error(e, f"searching complete profile for '{lpn_id}'")


# =============================================================================
# Shepherd Consultation Tools
# =============================================================================
# These tools expose the Shepherd agent's expert guidance as MCP tools,
# providing evidence-based advice on breeding, health, calendar, and economics.


@mcp.tool(
    name="shepherd_consult",
    description=(
        "Get expert sheep husbandry advice from the NSIP Shepherd. "
        "Use for general questions about breeding, health, management, or economics. "
        "The Shepherd provides evidence-based recommendations with a neutral, "
        "professional tone similar to a veterinarian."
    ),
)
async def shepherd_consult_tool(
    question: str,
    region: str = "",
) -> dict[str, Any]:
    """Get general Shepherd consultation for any sheep husbandry question.

    Args:
        question: Your sheep husbandry question (breeding, health, calendar, economics)
        region: Optional NSIP region for context (northeast, southeast, midwest,
                southwest, mountain, pacific). Auto-detected if not provided.

    Returns:
        Expert guidance with evidence-based recommendations
    """
    from nsip_mcp.prompts.shepherd_prompts import shepherd_consult_prompt

    try:
        # Access .fn to get the underlying async function from the FunctionPrompt
        messages = await cast(
            Awaitable[list[dict[str, Any]]],
            shepherd_consult_prompt.fn(question=question, region=region),
        )
        # Extract the text content from the prompt messages
        if messages and len(messages) > 0:
            for msg in messages:
                if msg.get("role") == "user":
                    content = msg.get("content", {})
                    if isinstance(content, dict):
                        return {"guidance": content.get("text", "")}
                    return {"guidance": str(content)}
        return {"error": "No guidance generated"}
    except Exception as e:
        return {"error": f"Shepherd consultation failed: {str(e)}"}


@mcp.tool(
    name="shepherd_breeding",
    description=(
        "Get expert breeding advice from the NSIP Shepherd. "
        "Covers genetic selection, EBV interpretation, mating plans, "
        "inbreeding management, and trait improvement strategies."
    ),
)
async def shepherd_breeding_tool(
    question: str,
    region: str = "midwest",
    production_goal: str = "balanced",
) -> dict[str, Any]:
    """Get Shepherd advice on breeding decisions.

    Args:
        question: Your breeding question or scenario
        region: NSIP region (northeast, southeast, midwest, southwest, mountain, pacific)
        production_goal: Production focus (terminal, maternal, hair, balanced)

    Returns:
        Expert breeding guidance with genetic principles and recommendations
    """
    from nsip_mcp.prompts.shepherd_prompts import shepherd_breeding_prompt

    try:
        # Access .fn to get the underlying async function from the FunctionPrompt
        messages = await cast(
            Awaitable[list[dict[str, Any]]],
            shepherd_breeding_prompt.fn(
                question=question, region=region, production_goal=production_goal
            ),
        )
        if messages and len(messages) > 0:
            for msg in messages:
                if msg.get("role") == "user":
                    content = msg.get("content", {})
                    if isinstance(content, dict):
                        return {"guidance": content.get("text", "")}
                    return {"guidance": str(content)}
        return {"error": "No guidance generated"}
    except Exception as e:
        return {"error": f"Shepherd breeding advice failed: {str(e)}"}


@mcp.tool(
    name="shepherd_health",
    description=(
        "Get expert health and nutrition advice from the NSIP Shepherd. "
        "Covers disease prevention, parasite management, vaccination schedules, "
        "feeding programs, and mineral supplementation."
    ),
)
async def shepherd_health_tool(
    question: str,
    region: str = "midwest",
    life_stage: str = "maintenance",
) -> dict[str, Any]:
    """Get Shepherd advice on health and nutrition.

    Args:
        question: Your health or nutrition question
        region: NSIP region for disease risk context
        life_stage: Life stage (maintenance, flushing, gestation, lactation)

    Returns:
        Expert health guidance with prevention and treatment approaches
    """
    from nsip_mcp.prompts.shepherd_prompts import shepherd_health_prompt

    try:
        # Access .fn to get the underlying async function from the FunctionPrompt
        messages = await cast(
            Awaitable[list[dict[str, Any]]],
            shepherd_health_prompt.fn(question=question, region=region, life_stage=life_stage),
        )
        if messages and len(messages) > 0:
            for msg in messages:
                if msg.get("role") == "user":
                    content = msg.get("content", {})
                    if isinstance(content, dict):
                        return {"guidance": content.get("text", "")}
                    return {"guidance": str(content)}
        return {"error": "No guidance generated"}
    except Exception as e:
        return {"error": f"Shepherd health advice failed: {str(e)}"}


@mcp.tool(
    name="shepherd_calendar",
    description=(
        "Get seasonal management advice from the NSIP Shepherd. "
        "Covers breeding schedules, lambing preparation, shearing timing, "
        "vaccination schedules, and seasonal task planning."
    ),
)
async def shepherd_calendar_tool(
    question: str,
    region: str = "midwest",
    task_type: str = "general",
) -> dict[str, Any]:
    """Get Shepherd advice on seasonal management.

    Args:
        question: Your calendar or planning question
        region: NSIP region for timing context
        task_type: Task category (breeding, lambing, shearing, health, general)

    Returns:
        Seasonal management guidance with timing and task priorities
    """
    from nsip_mcp.prompts.shepherd_prompts import shepherd_calendar_prompt

    try:
        # Access .fn to get the underlying async function from the FunctionPrompt
        messages = await cast(
            Awaitable[list[dict[str, Any]]],
            shepherd_calendar_prompt.fn(question=question, region=region, task_type=task_type),
        )
        if messages and len(messages) > 0:
            for msg in messages:
                if msg.get("role") == "user":
                    content = msg.get("content", {})
                    if isinstance(content, dict):
                        return {"guidance": content.get("text", "")}
                    return {"guidance": str(content)}
        return {"error": "No guidance generated"}
    except Exception as e:
        return {"error": f"Shepherd calendar advice failed: {str(e)}"}


@mcp.tool(
    name="shepherd_economics",
    description=(
        "Get economic analysis from the NSIP Shepherd. "
        "Covers cost analysis, breakeven calculations, ROI on genetics, "
        "marketing strategies, and profitability optimization."
    ),
)
async def shepherd_economics_tool(
    question: str,
    flock_size: str = "medium",
    market_focus: str = "balanced",
) -> dict[str, Any]:
    """Get Shepherd advice on economics and profitability.

    Args:
        question: Your economics or business question
        flock_size: Flock size category (small: 25-75, medium: 100-300, large: 500+)
        market_focus: Market focus (direct, auction, breeding_stock, balanced)

    Returns:
        Economic analysis with cost/revenue estimates and profitability strategies
    """
    from nsip_mcp.prompts.shepherd_prompts import shepherd_economics_prompt

    try:
        # Access .fn to get the underlying async function from the FunctionPrompt
        messages = await cast(
            Awaitable[list[dict[str, Any]]],
            shepherd_economics_prompt.fn(
                question=question, flock_size=flock_size, market_focus=market_focus
            ),
        )
        if messages and len(messages) > 0:
            for msg in messages:
                if msg.get("role") == "user":
                    content = msg.get("content", {})
                    if isinstance(content, dict):
                        return {"guidance": content.get("text", "")}
                    return {"guidance": str(content)}
        return {"error": "No guidance generated"}
    except Exception as e:
        return {"error": f"Shepherd economics advice failed: {str(e)}"}
