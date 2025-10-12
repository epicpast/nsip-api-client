"""MCP tool implementations for NSIP API.

This module defines all MCP tools that wrap NSIPClient methods, providing
LLM-friendly interfaces with automatic caching, context management, and error handling.
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from nsip_client.exceptions import (
    NSIPAPIError,
    NSIPNotFoundError,
    NSIPTimeoutError,
    NSIPValidationError,
)
from nsip_mcp.context import (
    ContextManagedResponse,
    should_summarize,
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


def apply_context_management(
    response: Dict[str, Any], force_summarize: bool = False
) -> Dict[str, Any]:
    """Apply context management (pass-through or summarization) to API response.

    Args:
        response: Original API response
        force_summarize: If True, always summarize regardless of size

    Returns:
        Context-managed response with metadata

    Example:
        >>> response = {"lpn_id": "ABC123", "breed": "Katahdin"}
        >>> managed = apply_context_management(response)
        >>> "_summarized" in managed
        True
    """
    try:
        if force_summarize or should_summarize(response):
            # Response exceeds 2000 tokens - summarize
            summarized = summarize_response(response)
            managed = ContextManagedResponse.create_summarized(response, summarized)
        else:
            # Response ≤2000 tokens - pass through unmodified
            managed = ContextManagedResponse.create_passthrough(response)

        return managed.final_response

    except Exception as e:
        # Summarization failed - fall back to pass-through (T041)
        logger.warning(f"Summarization failed: {e}. Falling back to pass-through.")
        response["_summarization_failed"] = True
        response["_summarization_error"] = str(e)
        return response


def validate_lpn_id(lpn_id: str, parameter_name: str = "lpn_id") -> Optional[Dict[str, Any]]:
    """Validate LPN ID parameter.

    Args:
        lpn_id: LPN ID to validate
        parameter_name: Name of the parameter (for error messages)

    Returns:
        None if validation succeeds, error dict if validation fails

    Note:
        LPN IDs must be at least 5 characters long
    """
    # Record validation attempt (SC-003)
    if server_metrics:
        server_metrics.record_validation(success=False)  # Assume failure initially

    if not lpn_id or not lpn_id.strip():
        return McpErrorResponse.invalid_params(
            parameter=parameter_name,
            value=lpn_id,
            expected="Non-empty string",
            suggestion=f"Provide a valid {parameter_name} (e.g., '6401492020FLE249')",
        ).to_dict()

    if len(lpn_id.strip()) < 5:
        return McpErrorResponse.invalid_params(
            parameter=parameter_name,
            value=lpn_id,
            expected="Minimum 5 characters",
            suggestion=f"Provide full {parameter_name} (e.g., '6401492020FLE249', not '{lpn_id}')",
        ).to_dict()

    # Validation passed - record success (SC-003)
    if server_metrics:
        server_metrics.record_validation(success=True)

    return None


def validate_breed_id(breed_id: int, parameter_name: str = "breed_id") -> Optional[Dict[str, Any]]:
    """Validate breed ID parameter.

    Args:
        breed_id: Breed ID to validate
        parameter_name: Name of the parameter (for error messages)

    Returns:
        None if validation succeeds, error dict if validation fails

    Note:
        Breed IDs must be positive integers
    """
    # Record validation attempt (SC-003)
    if server_metrics:
        server_metrics.record_validation(success=False)  # Assume failure initially

    if not isinstance(breed_id, int) or breed_id <= 0:
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


def validate_pagination(page: int, page_size: int) -> Optional[Dict[str, Any]]:
    """Validate pagination parameters.

    Args:
        page: Page number (0-indexed)
        page_size: Results per page

    Returns:
        None if validation succeeds, error dict if validation fails
    """
    # Record validation attempt (SC-003)
    if server_metrics:
        server_metrics.record_validation(success=False)  # Assume failure initially

    if page < 0:
        return McpErrorResponse.invalid_params(
            parameter="page",
            value=page,
            expected="Non-negative integer (0-indexed)",
            suggestion=f"Use page=0 for first page, not page={page}",
        ).to_dict()

    if page_size < 1 or page_size > 100:
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


def handle_nsip_api_error(error: Exception, context: str = "") -> Dict[str, Any]:
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
def nsip_get_last_update() -> Dict[str, Any]:
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
def nsip_list_breeds() -> List[Dict[str, Any]]:
    """Get list of available breed groups in the NSIP database.

    Returns:
        List of breed groups with their IDs and names

    Example:
        [
            {'id': 61, 'name': 'Range'},
            {'id': 62, 'name': 'Maternal Wool'},
            {'id': 64, 'name': 'Hair'},
            {'id': 69, 'name': 'Terminal'}
        ]
    """
    client = get_nsip_client()
    breed_groups = client.get_available_breed_groups()
    return [{"id": bg.id, "name": bg.name} for bg in breed_groups]


@mcp.tool()
@cached_api_call("get_statuses_by_breed_group")
def nsip_get_statuses() -> List[str]:
    """Get list of available animal statuses.

    Returns:
        List of status strings (e.g., CURRENT, SOLD, DEAD, COMMERCIAL, CULL)

    Example:
        ['CURRENT', 'SOLD', 'DEAD', 'COMMERCIAL', 'CULL', 'EXPORTED']
    """
    client = get_nsip_client()
    return client.get_statuses_by_breed_group()


@mcp.tool()
@cached_api_call("get_trait_ranges_by_breed")
def nsip_get_trait_ranges(breed_id: int) -> Dict[str, Any]:
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
    breed_id: Optional[int] = None,
    sorted_trait: Optional[str] = None,
    reverse: Optional[bool] = None,
    search_criteria: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Search for animals based on criteria with pagination.

    Args:
        page: Page number (0-indexed, default: 0)
        page_size: Number of results per page (1-100, default: 15)
        breed_id: Filter by breed ID (optional)
        sorted_trait: Trait to sort by, e.g. 'BWT', 'WWT' (optional)
        reverse: Sort in reverse order (optional)
        search_criteria: Additional filters as a dict (optional)

    Returns:
        Dict containing results or error response

    Example:
        {
            'results': [
                {'LpnId': '6401492020FLE249', 'Breed': 'Katahdin', ...},
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

        # Apply context management (T029)
        return apply_context_management(response)

    except Exception as e:
        return handle_nsip_api_error(e, "searching animals")


@mcp.tool()
@cached_api_call("get_animal_details")
def nsip_get_animal(search_string: str) -> Dict[str, Any]:
    """Get detailed information about a specific animal.

    Args:
        search_string: LPN ID or registration number to search for

    Returns:
        Dict containing complete animal information including traits, breeding values,
        pedigree info, and metadata. Large responses are automatically summarized.

    Example:
        {
            'lpn_id': '6401492020FLE249',
            'breed': 'Katahdin',
            'top_traits': [
                {'trait': 'YWT', 'value': 2.1, 'accuracy': 0.92},
                ...
            ],
            '_summarized': True,
            '_original_token_count': 3500,
            '_summary_token_count': 950,
            '_reduction_percent': 72.86
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

        # Apply context management (T030)
        return apply_context_management(response)

    except Exception as e:
        # NSIP API error - convert to structured error (T039)
        return handle_nsip_api_error(e, f"getting animal details for '{search_string}'")


@mcp.tool()
@cached_api_call("get_lineage")
def nsip_get_lineage(lpn_id: str) -> Dict[str, Any]:
    """Get the lineage/pedigree information for an animal.

    Args:
        lpn_id: The LPN ID of the animal

    Returns:
        Dict containing pedigree tree with sire, dam, and ancestor information.
        Large lineage trees are automatically summarized.

    Example:
        {
            'sire': '123ABC',
            'dam': '456DEF',
            '_summarized': True,
            '_original_token_count': 2500,
            '_summary_token_count': 720,
            '_reduction_percent': 71.20
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

        # Apply context management (T031)
        return apply_context_management(response)

    except Exception as e:
        # NSIP API error - convert to structured error (T039)
        return handle_nsip_api_error(e, f"getting lineage for '{lpn_id}'")


@mcp.tool()
@cached_api_call("get_progeny")
def nsip_get_progeny(lpn_id: str, page: int = 0, page_size: int = 10) -> Dict[str, Any]:
    """Get progeny (offspring) for a specific animal with pagination.

    Args:
        lpn_id: The LPN ID of the parent animal
        page: Page number (0-indexed, default: 0)
        page_size: Number of results per page (default: 10)

    Returns:
        Dict containing:
        - animals: List of offspring records (or summarized if large)
        - total_count: Total number of offspring
        - page: Current page number
        - page_size: Results per page
        - _summarized: True if response was summarized

    Example:
        {
            'total_count': 6,
            'page': 0,
            'page_size': 10,
            '_summarized': True,
            '_original_token_count': 2800,
            '_summary_token_count': 750,
            '_reduction_percent': 73.21
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

        # Apply context management (T032)
        return apply_context_management(response)

    except Exception as e:
        # NSIP API error - convert to structured error (T039)
        return handle_nsip_api_error(e, f"getting progeny for '{lpn_id}'")


@mcp.tool()
@cached_api_call("search_by_lpn")
def nsip_search_by_lpn(lpn_id: str) -> Dict[str, Any]:
    """Get complete profile for an animal by LPN ID (details + lineage + progeny).

    This is a convenience tool that combines three API calls into one comprehensive result.
    **ALWAYS returns a summarized response** due to the combined data size.

    Args:
        lpn_id: The LPN ID to search for

    Returns:
        Dict containing summarized profile with:
        - lpn_id: Animal identifier
        - breed: Breed name
        - sire: Sire LPN ID
        - dam: Dam LPN ID
        - total_progeny: Number of offspring
        - top_traits: Top 3 traits by accuracy
        - _summarized: Always True
        - _original_token_count: Original size before summarization
        - _summary_token_count: Size after summarization
        - _reduction_percent: Percentage reduction achieved

    Example:
        {
            'lpn_id': '6401492020FLE249',
            'breed': 'Katahdin',
            'sire': '123ABC',
            'dam': '456DEF',
            'total_progeny': 6,
            'top_traits': [
                {'trait': 'YWT', 'value': 2.1, 'accuracy': 0.92},
                ...
            ],
            '_summarized': True,
            '_original_token_count': 5200,
            '_summary_token_count': 1100,
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

        # Apply context management - ALWAYS summarize (T033)
        # Combined response always exceeds 2000 tokens
        return apply_context_management(response, force_summarize=True)

    except Exception as e:
        # NSIP API error - convert to structured error (T039)
        return handle_nsip_api_error(e, f"searching complete profile for '{lpn_id}'")
