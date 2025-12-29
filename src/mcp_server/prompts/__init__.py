from fastmcp import FastMCP

from mcp_server.prompts.example_prompts import register_example_prompts


def register_prompts(mcp: FastMCP) -> None:
    register_example_prompts(mcp)


__all__ = ["register_prompts"]
