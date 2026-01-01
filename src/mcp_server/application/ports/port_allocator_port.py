from abc import ABC, abstractmethod


class PortAllocatorPort(ABC):
    @abstractmethod
    async def allocate_port(self) -> int:
        pass

    @abstractmethod
    async def release_port(self, port: int) -> None:
        pass
