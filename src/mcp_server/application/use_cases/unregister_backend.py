from mcp_server.application.ports import (
    MCPClientPort,
    PortAllocatorPort,
    ProcessManagerPort,
)
from mcp_server.domain.exceptions import BackendNotFoundError
from mcp_server.domain.repositories import BackendRepository, ConfigRepository


class UnregisterBackend:
    def __init__(
        self,
        backend_repository: BackendRepository,
        config_repository: ConfigRepository,
        process_manager: ProcessManagerPort,
        port_allocator: PortAllocatorPort,
        client_factory: dict[str, MCPClientPort],
    ) -> None:
        self.backend_repository = backend_repository
        self.config_repository = config_repository
        self.process_manager = process_manager
        self.port_allocator = port_allocator
        self.client_factory = client_factory

    async def execute(self, backend_name: str) -> None:
        backend = self.backend_repository.get(backend_name)
        if not backend:
            raise BackendNotFoundError(backend_name)

        if backend.is_managed_process and backend.process_id:
            await self.process_manager.stop_process(backend.process_id)

            if backend.config.source.process_config and backend.config.source.process_config.port:
                await self.port_allocator.release_port(
                    backend.config.source.process_config.port
                )

        self.client_factory.pop(backend_name, None)
        self.backend_repository.remove(backend_name)
        await self.config_repository.remove_config(backend_name)
