"""MCP Server Template.

A FastMCP server template with organized tools, resources, and prompts.
"""

__version__ = "0.1.0"

__all__ = ["create_server", "mcp", "__version__"]


def __getattr__(name):
    """Lazy load server components to avoid import errors in tests."""
    if name == "create_server":
        from mcp_server.server import create_server
        return create_server
    elif name == "mcp":
        from mcp_server.server import mcp
        return mcp
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

