import pytest
from fastmcp import FastMCP

from mcp_server.config import ServerConfig
from mcp_server.server import create_server


@pytest.fixture
def server_config() -> ServerConfig:
    return ServerConfig(
        name="test-server",
        host="127.0.0.1",
        port=8000,
    )


@pytest.fixture
def mcp_server(server_config: ServerConfig) -> FastMCP:
    return create_server(server_config)

