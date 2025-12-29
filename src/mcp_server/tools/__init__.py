from fastmcp import FastMCP

from mcp_server.tools.example_tools import register_example_tools


def register_tools(mcp: FastMCP) -> None:
    register_example_tools(mcp)


__all__ = ["register_tools"]

