from mcp_server.domain.entities import Backend
from mcp_server.domain.repositories import BackendRepository


class InMemoryBackendRepository(BackendRepository):
    def __init__(self) -> None:
        self._backends: dict[str, Backend] = {}

    def add(self, backend: Backend) -> None:
        self._backends[backend.name] = backend

    def get(self, name: str) -> Backend | None:
        return self._backends.get(name)

    def get_all(self) -> list[Backend]:
        return list(self._backends.values())

    def get_healthy(self) -> list[Backend]:
        return [b for b in self._backends.values() if b.is_healthy]

    def get_with_tool(self, tool_name: str) -> list[Backend]:
        return [b for b in self._backends.values() if b.has_tool(tool_name)]

    def remove(self, name: str) -> None:
        self._backends.pop(name, None)

    def exists(self, name: str) -> bool:
        return name in self._backends
