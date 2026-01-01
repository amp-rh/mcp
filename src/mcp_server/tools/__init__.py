from fastmcp import FastMCP

from mcp_server.tools.meta import register_meta_tools


def register_tools(mcp: FastMCP) -> None:
    register_meta_tools(mcp)


__all__ = ["register_tools"]
