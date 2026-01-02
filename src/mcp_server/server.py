import asyncio

from fastmcp import FastMCP

from mcp_server.config import ServerConfig
from mcp_server.presentation.server_factory import create_router_server, create_server

mcp = create_server()


def main() -> None:
    config = ServerConfig.from_env()
    server = create_server(config)
    server.run()


def main_router() -> None:
    """Run the MCP router with HTTP/SSE transport."""
    import os

    async def _initialize() -> FastMCP:
        return await create_router_server()

    router = asyncio.run(_initialize())

    # Use HTTP/SSE transport when running in container or when MCP_PORT is set
    port = int(os.getenv("MCP_PORT", "0"))
    host = os.getenv("MCP_HOST", "127.0.0.1")

    if port > 0:
        # HTTP transport for container deployment
        # Use streamable-http for MCP-over-HTTP with POST support
        router.run(transport="streamable-http", port=port, host=host)
    else:
        # Stdio transport for Claude Code
        router.run()


if __name__ == "__main__":
    main()
