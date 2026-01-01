from fastmcp import FastMCP

from mcp_server.tools.meta.testing import register_testing_tools


def register_meta_tools(mcp: FastMCP) -> None:
    register_testing_tools(mcp)


__all__ = ["register_meta_tools"]
