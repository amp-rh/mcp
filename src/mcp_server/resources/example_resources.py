import json

from fastmcp import FastMCP

from mcp_server import __version__


def register_example_resources(mcp: FastMCP) -> None:
    @mcp.resource("config://server")
    def get_server_info() -> str:
        return json.dumps(
            {
                "name": "mcp-server",
                "version": __version__,
                "status": "running",
            }
        )

    @mcp.resource("config://capabilities")
    def get_capabilities() -> str:
        return json.dumps(
            {
                "tools": True,
                "resources": True,
                "prompts": True,
            }
        )

    @mcp.resource("data://items/{item_id}")
    def get_item(item_id: str) -> str:
        return json.dumps(
            {
                "id": item_id,
                "name": f"Item {item_id}",
                "description": f"This is item {item_id}",
            }
        )

