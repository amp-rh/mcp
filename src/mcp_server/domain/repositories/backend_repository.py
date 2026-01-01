from abc import ABC, abstractmethod

from mcp_server.domain.entities import Backend


class BackendRepository(ABC):
    @abstractmethod
    def add(self, backend: Backend) -> None:
        pass

    @abstractmethod
    def get(self, name: str) -> Backend | None:
        pass

    @abstractmethod
    def get_all(self) -> list[Backend]:
        pass

    @abstractmethod
    def get_healthy(self) -> list[Backend]:
        pass

    @abstractmethod
    def get_with_tool(self, tool_name: str) -> list[Backend]:
        pass

    @abstractmethod
    def remove(self, name: str) -> None:
        pass

    @abstractmethod
    def exists(self, name: str) -> bool:
        pass
