"""MCP tool wrapper infrastructure for NSIP API.

This module provides base functionality for wrapping NSIPClient methods as MCP tools,
including caching and client lifecycle management.
"""

import functools
import inspect
from collections.abc import Callable
from inspect import Parameter
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
        # Cache signature at decoration time for performance (M2)
        sig = inspect.signature(func)
        # Build lists of param names by kind for proper handling
        # Filter out VAR_POSITIONAL (*args) and VAR_KEYWORD (**kwargs) parameters (H1)
        positional_only_names: list[str] = []
        convertible_names: list[str] = []  # POSITIONAL_OR_KEYWORD params
        keyword_only_names: list[str] = []

        for name, param in sig.parameters.items():
            # Skip 'self' and 'cls' for methods - they can't be serialized for cache keys
            if name in ("self", "cls"):
                continue
            if param.kind == Parameter.POSITIONAL_ONLY:
                positional_only_names.append(name)
            elif param.kind == Parameter.POSITIONAL_OR_KEYWORD:
                convertible_names.append(name)
            elif param.kind == Parameter.KEYWORD_ONLY:
                keyword_only_names.append(name)
            # VAR_POSITIONAL and VAR_KEYWORD are filtered out

        # Combined list for positional arg handling (excludes keyword-only)
        positional_param_names = positional_only_names + convertible_names

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Track positional-only args separately (they must stay positional)
            positional_only_args: list[Any] = []
            cache_kwargs: dict[str, Any] = dict(kwargs)

            # Convert positional args to kwargs for cache key generation
            # But keep positional-only args separate for the actual call
            if args:
                # Skip 'self'/'cls' if this is a method (first arg is the instance)
                arg_offset = 0
                if (
                    args
                    and hasattr(args[0], "__class__")
                    and not isinstance(
                        args[0], (str, int, float, bool, type(None), list, dict, tuple)
                    )
                ):
                    # Likely a method call - first arg is self/cls, skip it for caching
                    arg_offset = 1

                for i, arg in enumerate(args):
                    param_idx = i - arg_offset
                    if param_idx < 0:
                        # This is 'self' or 'cls' - pass through but don't cache
                        continue
                    if param_idx < len(positional_param_names):
                        param = positional_param_names[param_idx]
                        if param in cache_kwargs:
                            raise TypeError(
                                f"{func.__name__}() got multiple values for argument '{param}'"
                            )
                        # Add to cache kwargs for key generation
                        cache_kwargs[param] = arg
                        # Track positional-only args separately
                        if param_idx < len(positional_only_names):
                            positional_only_args.append(arg)

            # Generate cache key from method name and parameters (use cache_kwargs)
            cache_key = response_cache.make_key(method_name, **cache_kwargs)

            # Check cache first
            cached_result = response_cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Cache miss - call the actual function
            # For methods and positional-only params, pass original args
            # For regular functions, use converted kwargs
            if positional_only_args or (args and len(args) > len(positional_param_names)):
                # Has positional-only args or extra positional args - use original call style
                result = func(*args, **kwargs)
            else:
                # All args converted to kwargs safely
                result = func(**cache_kwargs)

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
