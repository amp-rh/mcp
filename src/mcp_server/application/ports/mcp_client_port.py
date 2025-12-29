from abc import ABC, abstractmethod
from typing import Any


class MCPClientPort(ABC):
    @abstractmethod
    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        pass

    @abstractmethod
    async def get_resource(self, uri: str) -> str:
        pass

    @abstractmethod
    async def get_prompt(self, prompt_name: str, arguments: dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def list_tools(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def list_resources(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def list_prompts(self) -> list[dict[str, Any]]:
        pass
