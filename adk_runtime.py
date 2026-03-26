"""Minimal ADK integration helpers.

Why this module exists:
- It gives a single place to adapt to ADK API changes.
- It keeps the rest of the app focused on interview logic, not framework glue.
"""

from typing import Any, Callable, Dict

TOOL_REGISTRY: Dict[str, Callable[..., Any]] = {}


def adk_tool(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator for registering tools by name.

    This registry is used by the executor. If the installed Google ADK version
    exposes a tool object type, this module can be expanded to instantiate those
    wrappers from the same registry.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        TOOL_REGISTRY[name] = func
        return func

    return decorator


def get_tool(name: str) -> Callable[..., Any]:
    """Returns a registered callable tool by name."""
    if name not in TOOL_REGISTRY:
        raise KeyError(f"Tool '{name}' is not registered.")
    return TOOL_REGISTRY[name]
