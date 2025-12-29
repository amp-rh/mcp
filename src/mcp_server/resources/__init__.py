from fastmcp import FastMCP

from mcp_server.resources.example_resources import register_example_resources


def register_resources(mcp: FastMCP) -> None:
    register_example_resources(mcp)


__all__ = ["register_resources"]

