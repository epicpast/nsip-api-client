"""MCP tool wrapper infrastructure for NSIP API.

This module provides base functionality for wrapping NSIPClient methods as MCP tools,
including caching and client lifecycle management.
"""

import functools
import inspect
from collections.abc import Callable
from typing import Any

from nsip_client.client import NSIPClient
from nsip_mcp.cache import response_cache

# Lazy-initialized client instance (created on first use)
_client_instance: NSIPClient | None = None


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

    Example:
        >>> @cached_api_call("get_animal_details")
        >>> def nsip_get_animal(search_string: str) -> dict:
        >>>     client = get_nsip_client()
        >>>     return client.get_animal_details(search_string=search_string)
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Convert positional args to kwargs for consistent cache key generation
            if args:
                sig = inspect.signature(func)
                param_names = list(sig.parameters.keys())
                for i, arg in enumerate(args):
                    if i < len(param_names):
                        kwargs[param_names[i]] = arg

            # Generate cache key from method name and parameters
            cache_key = response_cache.make_key(method_name, **kwargs)

            # Check cache first
            cached_result = response_cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Cache miss - call the actual function (use kwargs since we converted args)
            result = func(**kwargs)

            # Store in cache
            response_cache.set(cache_key, result)

            return result

        return wrapper

    return decorator


def reset_client() -> None:
    """Reset the client instance (primarily for testing).

    Forces re-initialization of the client on next get_nsip_client() call.
    Useful for testing credential changes or client configuration.
    """
    global _client_instance
    _client_instance = None
