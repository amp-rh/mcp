"""Tests for MCPClient HTTP communication."""

import pytest

from mcp_server.routing.client import MCPClient


class TestMCPClient:
    """Test MCPClient initialization and basic properties."""

    def test_client_initialization(self):
        """Test MCPClient initialization."""
        client = MCPClient("http://localhost:8001", timeout=30)
        assert client.base_url == "http://localhost:8001"
        assert client.timeout == 30

    def test_base_url_trailing_slash_removed(self):
        """Test that trailing slash is removed from base URL."""
        client = MCPClient("http://localhost:8001/", timeout=30)
        assert client.base_url == "http://localhost:8001"

    def test_default_timeout(self):
        """Test default timeout value."""
        client = MCPClient("http://localhost:8001")
        assert client.timeout == 30

    def test_custom_timeout(self):
        """Test custom timeout value."""
        client = MCPClient("http://localhost:8001", timeout=60)
        assert client.timeout == 60

    def test_https_url(self):
        """Test HTTPS URL."""
        client = MCPClient("https://api.example.com/mcp", timeout=30)
        assert client.base_url == "https://api.example.com/mcp"

    def test_base_url_with_path(self):
        """Test base URL with path component."""
        client = MCPClient("http://localhost:8001/api/v1", timeout=30)
        assert client.base_url == "http://localhost:8001/api/v1"

    @pytest.mark.asyncio
    async def test_close(self):
        """Test closing the client."""
        client = MCPClient("http://localhost:8001")
        await client.close()
        # Should not raise any exception
