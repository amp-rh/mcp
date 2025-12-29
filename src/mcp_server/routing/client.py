"""HTTP/SSE client for communicating with backend MCP servers."""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class MCPClient:
    """Async HTTP client for communicating with MCP servers via HTTP/SSE transport."""

    def __init__(self, base_url: str, timeout: int = 30):
        """Initialize MCP client.

        Args:
            base_url: Base URL of the MCP server (e.g., http://localhost:8001)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self) -> None:
        """Close the HTTP client connection."""
        await self.client.aclose()

    async def list_tools(self) -> list[dict[str, Any]]:
        """List available tools from the backend.

        Returns:
            List of tool definitions

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self.client.post(
            f"{self.base_url}/tools/list",
            json={},
        )
        response.raise_for_status()
        data = response.json()
        return data.get("tools", [])

    async def list_resources(self) -> list[dict[str, Any]]:
        """List available resources from the backend.

        Returns:
            List of resource definitions

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self.client.post(
            f"{self.base_url}/resources/list",
            json={},
        )
        response.raise_for_status()
        data = response.json()
        return data.get("resources", [])

    async def list_prompts(self) -> list[dict[str, Any]]:
        """List available prompts from the backend.

        Returns:
            List of prompt definitions

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self.client.post(
            f"{self.base_url}/prompts/list",
            json={},
        )
        response.raise_for_status()
        data = response.json()
        return data.get("prompts", [])

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any:
        """Execute a tool on the backend.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments as a dictionary

        Returns:
            Tool result

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self.client.post(
            f"{self.base_url}/tools/call",
            json={
                "name": tool_name,
                "arguments": arguments,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data.get("result")

    async def get_resource(self, uri: str) -> str:
        """Fetch a resource from the backend.

        Args:
            uri: Resource URI (e.g., config://server)

        Returns:
            Resource content as string

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self.client.post(
            f"{self.base_url}/resources/read",
            json={
                "uri": uri,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data.get("contents", "")

    async def health_check(self) -> bool:
        """Check if the backend is healthy.

        Performs a simple health check by calling the health endpoint.

        Returns:
            True if backend is healthy, False otherwise
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/health",
                timeout=min(self.timeout, 5),
            )
            return response.status_code == 200
        except httpx.RequestError:
            return False
