import logging
from typing import Any

import httpx

from mcp_server.application.ports import MCPClientPort

logger = logging.getLogger(__name__)


class HTTPMCPClient(MCPClientPort):
    def __init__(self, base_url: str, timeout: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/tools/{tool_name}",
                json=arguments,
            )
            response.raise_for_status()
            return response.json()

    async def get_resource(self, uri: str) -> str:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/resources",
                params={"uri": uri},
            )
            response.raise_for_status()
            return response.text

    async def get_prompt(self, prompt_name: str, arguments: dict[str, Any]) -> str:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/prompts/{prompt_name}",
                json=arguments,
            )
            response.raise_for_status()
            return response.text

    async def list_tools(self) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/tools")
            response.raise_for_status()
            data = response.json()
            return data.get("tools", [])

    async def list_resources(self) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/resources")
            response.raise_for_status()
            data = response.json()
            return data.get("resources", [])

    async def list_prompts(self) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/prompts")
            response.raise_for_status()
            data = response.json()
            return data.get("prompts", [])
