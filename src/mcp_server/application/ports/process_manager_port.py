from abc import ABC, abstractmethod

from mcp_server.domain.value_objects import ProcessConfig


class ProcessManagerPort(ABC):
    @abstractmethod
    async def start_process(self, config: ProcessConfig) -> int:
        pass

    @abstractmethod
    async def stop_process(self, pid: int) -> None:
        pass

    @abstractmethod
    async def is_process_alive(self, pid: int) -> bool:
        pass

    @abstractmethod
    async def restart_process(self, pid: int, config: ProcessConfig) -> int:
        pass

    @abstractmethod
    async def shutdown_all(self) -> None:
        pass
