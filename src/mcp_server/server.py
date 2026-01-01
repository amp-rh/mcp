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
    async def _initialize() -> FastMCP:
        return await create_router_server()

    router = asyncio.run(_initialize())
    router.run()


if __name__ == "__main__":
    main()
