from mcp_server.application.ports import MCPClientPort
from mcp_server.domain.repositories import BackendRepository


class DiscoverCapabilities:
    def __init__(
        self,
        backend_repository: BackendRepository,
        client_factory: dict[str, MCPClientPort],
    ) -> None:
        self.backend_repository = backend_repository
        self.client_factory = client_factory

    async def execute(self) -> None:
        backends = self.backend_repository.get_all()

        for backend in backends:
            client = self.client_factory.get(backend.name)
            if not client:
                continue

            try:
                tools = await client.list_tools()
                resources = await client.list_resources()
                prompts = await client.list_prompts()

                backend.update_capabilities(tools, resources, prompts)
                backend.record_success()

            except Exception as e:
                backend.record_failure(str(e))
