from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from mcp_server.domain.value_objects import BackendConfig


class ConfigRepository(ABC):
    @abstractmethod
    async def load_configs(self) -> list[BackendConfig]:
        pass

    @abstractmethod
    async def save_config(self, config: BackendConfig) -> None:
        pass

    @abstractmethod
    async def remove_config(self, backend_name: str) -> None:
        pass

    @abstractmethod
    async def watch_changes(self) -> AsyncIterator[list[BackendConfig]]:
        pass
        yield
