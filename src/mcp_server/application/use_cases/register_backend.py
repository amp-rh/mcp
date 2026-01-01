import asyncio
from typing import TYPE_CHECKING

from mcp_server.application.dtos import (
    BackendRegistrationRequest,
    BackendRegistrationResponse,
)
from mcp_server.application.ports import (
    MCPClientPort,
    PortAllocatorPort,
    ProcessManagerPort,
)
from mcp_server.domain.entities import Backend
from mcp_server.domain.exceptions import BackendAlreadyExistsError
from mcp_server.domain.repositories import BackendRepository, ConfigRepository
from mcp_server.domain.services.namespace_generator import NamespaceGenerator
from mcp_server.domain.value_objects import (
    BackendConfig,
    BackendSource,
    BackendSourceType,
    GitHubSpec,
    HealthCheckSettings,
    ProcessConfig,
)
from mcp_server.infrastructure.adapters import HTTPMCPClient

if TYPE_CHECKING:
    from mcp_server.application.use_cases import DiscoverCapabilities


class RegisterBackend:
    def __init__(
        self,
        backend_repository: BackendRepository,
        config_repository: ConfigRepository,
        process_manager: ProcessManagerPort,
        port_allocator: PortAllocatorPort,
        client_factory: dict[str, MCPClientPort],
        discover_capabilities: "DiscoverCapabilities",
    ) -> None:
        self.backend_repository = backend_repository
        self.config_repository = config_repository
        self.process_manager = process_manager
        self.port_allocator = port_allocator
        self.client_factory = client_factory
        self.discover_capabilities = discover_capabilities

    async def execute(
        self, request: BackendRegistrationRequest
    ) -> BackendRegistrationResponse:
        source = self._parse_source(request.source)
        namespace = request.namespace or NamespaceGenerator.generate(source)
        name = request.name or self._generate_name(source, namespace)

        if self.backend_repository.exists(name):
            raise BackendAlreadyExistsError(name)

        if source.process_config:
            port = await self.port_allocator.allocate_port()
            source = self._update_source_with_port(source, port)

        config = BackendConfig(
            name=name,
            source=source,
            namespace=namespace,
            priority=request.priority,
            auto_start=request.auto_start,
            health_check=HealthCheckSettings(enabled=request.health_check_enabled),
        )

        backend = Backend(config=config)

        started = False
        if config.source.process_config and config.auto_start:
            pid = await self.process_manager.start_process(config.source.process_config)
            backend.process_id = pid
            started = True
            await self._wait_for_ready(config.url)

        client = HTTPMCPClient(base_url=config.url, timeout=30)
        self.client_factory[name] = client

        await self.discover_capabilities.execute_for_backend(backend, client)

        self.backend_repository.add(backend)
        await self.config_repository.save_config(config)

        return BackendRegistrationResponse(
            backend_name=name,
            namespace=namespace,
            url=config.url,
            started=started,
            message=f"Backend '{name}' registered successfully",
        )

    def _parse_source(self, source_str: str) -> BackendSource:
        if source_str.startswith("http://") or source_str.startswith("https://"):
            return BackendSource(
                source_type=BackendSourceType.HTTP,
                http_url=source_str,
            )

        if source_str.startswith("github:"):
            github_spec = GitHubSpec.from_url(source_str)
            package_name = github_spec.to_package_name()
            process_config = ProcessConfig(
                command="uvx",
                args=(package_name,),
            )
            return BackendSource(
                source_type=BackendSourceType.GITHUB,
                github_spec=github_spec,
                process_config=process_config,
            )

        process_config = ProcessConfig(
            command="uvx",
            args=(source_str,),
        )
        return BackendSource(
            source_type=BackendSourceType.PACKAGE,
            package_name=source_str,
            process_config=process_config,
        )

    def _generate_name(self, source: BackendSource, namespace: str) -> str:
        if source.github_spec:
            return source.github_spec.repo.lower()
        if source.package_name:
            return source.package_name.split("/")[-1].lower().replace("-", "_")
        return namespace

    def _update_source_with_port(self, source: BackendSource, port: int) -> BackendSource:
        if not source.process_config:
            return source

        new_process_config = ProcessConfig(
            command=source.process_config.command,
            args=source.process_config.args,
            port=port,
            env={**source.process_config.env, "PORT": str(port)},
        )

        return BackendSource(
            source_type=source.source_type,
            http_url=source.http_url,
            github_spec=source.github_spec,
            package_name=source.package_name,
            process_config=new_process_config,
        )

    async def _wait_for_ready(self, url: str, timeout: int = 30) -> None:
        import httpx

        for _ in range(timeout):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{url}/health", timeout=1.0)
                    if response.status_code < 500:
                        return
            except Exception:
                pass
            await asyncio.sleep(1)
