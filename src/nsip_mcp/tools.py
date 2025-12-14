"""MCP tool wrapper infrastructure for NSIP API.

This module provides base functionality for wrapping NSIPClient methods as MCP tools,
including caching and client lifecycle management.
"""

import functools
import inspect
from collections.abc import Callable
from inspect import Parameter
from typing import Any, TypedDict

from nsip_client.client import NSIPClient
from nsip_mcp.cache import response_cache

# Lazy-initialized client instance (created on first use)
_client_instance: NSIPClient | None = None


class ParamInfo(TypedDict):
    """Type definition for parameter extraction results."""

    names: list[str]
    has_positional_only: bool
    has_self: bool


def get_nsip_client() -> NSIPClient:
    """Get or create the NSIPClient instance.

    Returns:
        Configured NSIPClient instance

    Note:
        - Client is initialized once and reused across all tool invocations
        - NSIP API is public and requires no authentication
        - Default timeout is 30 seconds
    """
    global _client_instance

    if _client_instance is None:
        _client_instance = NSIPClient()

    return _client_instance


def cached_api_call(method_name: str) -> Callable:
    """Decorator to add caching to API method calls.

    Generates cache key from method name and parameters, checks cache before
    making API call, and stores result in cache on cache miss.

    Args:
        method_name: Name of the API method being called

    Returns:
        Decorator function that wraps the tool function

    Note:
        - self/cls parameters are excluded from cache keys (methods share cache)
        - VAR_POSITIONAL (*args) and VAR_KEYWORD (**kwargs) are excluded from cache keys
        - Positional-only parameters are supported for cache keys but kept positional for calls

    Example:
        >>> @cached_api_call("get_animal_details")
        >>> def nsip_get_animal(search_string: str) -> dict:
        >>>     client = get_nsip_client()
        >>>     return client.get_animal_details(search_string=search_string)
    """

    def decorator(func: Callable) -> Callable:
        # Cache signature at decoration time for performance (M2)
        sig = inspect.signature(func)
        # Build param info, filtering out VAR_POSITIONAL/VAR_KEYWORD (H1) and self/cls
        param_info = _extract_param_info(sig)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Build cache kwargs from positional and keyword args
            cache_kwargs = _build_cache_kwargs(args, kwargs, param_info, func.__name__)

            # Check cache first
            cache_key = response_cache.make_key(method_name, **cache_kwargs)
            cached_result = response_cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Cache miss - call function
            # Use original args if: has positional-only params OR is a method (has self/cls)
            if param_info["has_positional_only"] or param_info["has_self"]:
                result = func(*args, **kwargs)
            else:
                result = func(**cache_kwargs)

            response_cache.set(cache_key, result)
            return result

        return wrapper

    return decorator


def _extract_param_info(sig: inspect.Signature) -> ParamInfo:
    """Extract parameter information from signature for caching logic."""
    positional_names: list[str] = []
    has_positional_only = False
    has_self = False

    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            has_self = True
            continue
        if param.kind == Parameter.POSITIONAL_ONLY:
            positional_names.append(name)
            has_positional_only = True
        elif param.kind in (Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY):
            positional_names.append(name)
        # VAR_POSITIONAL and VAR_KEYWORD are filtered out

    return {
        "names": positional_names,
        "has_positional_only": has_positional_only,
        "has_self": has_self,
    }


def _build_cache_kwargs(
    args: tuple, kwargs: dict, param_info: ParamInfo, func_name: str
) -> dict[str, Any]:
    """Convert positional args to kwargs for cache key generation."""
    cache_kwargs = dict(kwargs)
    param_names = param_info["names"]
    # Skip first arg if this is a method (self/cls)
    arg_offset = 1 if param_info["has_self"] else 0

    for i, arg in enumerate(args[arg_offset:]):
        if i < len(param_names):
            param = param_names[i]
            if param in cache_kwargs:
                raise TypeError(f"{func_name}() got multiple values for argument '{param}'")
            cache_kwargs[param] = arg

    return cache_kwargs


def reset_client() -> None:
    """Reset the client instance (primarily for testing).

    Forces re-initialization of the client on next get_nsip_client() call.
    Useful for testing credential changes or client configuration.
    """
    global _client_instance
    _client_instance = None
