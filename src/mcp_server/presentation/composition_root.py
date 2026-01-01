import logging
from pathlib import Path

from mcp_server.application.ports import (
    MCPClientPort,
    PortAllocatorPort,
    ProcessManagerPort,
)
from mcp_server.application.use_cases import (
    CheckBackendHealth,
    DiscoverCapabilities,
    MonitorBackendProcesses,
    RegisterBackend,
    ReloadBackendsConfig,
    RouteToolCall,
    UnregisterBackend,
)
from mcp_server.domain.entities import Backend
from mcp_server.domain.repositories import BackendRepository, ConfigRepository
from mcp_server.infrastructure.adapters import HTTPMCPClient, PortAllocator, UvxProcessManager
from mcp_server.infrastructure.config.yaml_backend_config_repository import (
    YamlBackendConfigRepository,
)
from mcp_server.infrastructure.repositories import InMemoryBackendRepository
from mcp_server.infrastructure.services import ConfigWatcher

logger = logging.getLogger(__name__)


class CompositionRoot:
    def __init__(
        self,
        backends_config_path: str,
        request_timeout: int = 30,
        max_retry_attempts: int = 3,
        retry_backoff_multiplier: float = 2.0,
        max_retry_backoff: int = 10,
    ) -> None:
        self.backends_config_path = str(Path(backends_config_path).expanduser())
        self.request_timeout = request_timeout
        self.max_retry_attempts = max_retry_attempts
        self.retry_backoff_multiplier = retry_backoff_multiplier
        self.max_retry_backoff = max_retry_backoff

        self._backend_repository: BackendRepository | None = None
        self._client_factory: dict[str, MCPClientPort] | None = None
        self._route_tool_call: RouteToolCall | None = None
        self._discover_capabilities: DiscoverCapabilities | None = None
        self._check_backend_health: CheckBackendHealth | None = None
        self._config_repository: ConfigRepository | None = None
        self._process_manager: ProcessManagerPort | None = None
        self._port_allocator: PortAllocatorPort | None = None
        self._register_backend: RegisterBackend | None = None
        self._unregister_backend: UnregisterBackend | None = None
        self._reload_backends: ReloadBackendsConfig | None = None
        self._monitor_processes: MonitorBackendProcesses | None = None
        self._config_watcher: ConfigWatcher | None = None

    @property
    def backend_repository(self) -> BackendRepository:
        if self._backend_repository is None:
            self._backend_repository = InMemoryBackendRepository()
        return self._backend_repository

    @property
    def client_factory(self) -> dict[str, MCPClientPort]:
        if self._client_factory is None:
            self._client_factory = {}
        return self._client_factory

    @property
    def route_tool_call(self) -> RouteToolCall:
        if self._route_tool_call is None:
            self._route_tool_call = RouteToolCall(
                backend_repository=self.backend_repository,
                client_factory=self.client_factory,
                max_retry_attempts=self.max_retry_attempts,
                retry_backoff_multiplier=self.retry_backoff_multiplier,
                max_retry_backoff=self.max_retry_backoff,
            )
        return self._route_tool_call

    @property
    def discover_capabilities(self) -> DiscoverCapabilities:
        if self._discover_capabilities is None:
            self._discover_capabilities = DiscoverCapabilities(
                backend_repository=self.backend_repository,
                client_factory=self.client_factory,
            )
        return self._discover_capabilities

    @property
    def check_backend_health(self) -> CheckBackendHealth:
        if self._check_backend_health is None:
            self._check_backend_health = CheckBackendHealth(
                backend_repository=self.backend_repository,
            )
        return self._check_backend_health

    @property
    def config_repository(self) -> ConfigRepository:
        if self._config_repository is None:
            self._config_repository = YamlBackendConfigRepository(
                self.backends_config_path
            )
        return self._config_repository

    @property
    def process_manager(self) -> ProcessManagerPort:
        if self._process_manager is None:
            self._process_manager = UvxProcessManager()
        return self._process_manager

    @property
    def port_allocator(self) -> PortAllocatorPort:
        if self._port_allocator is None:
            self._port_allocator = PortAllocator()
        return self._port_allocator

    @property
    def register_backend(self) -> RegisterBackend:
        if self._register_backend is None:
            self._register_backend = RegisterBackend(
                backend_repository=self.backend_repository,
                config_repository=self.config_repository,
                process_manager=self.process_manager,
                port_allocator=self.port_allocator,
                client_factory=self.client_factory,
                discover_capabilities=self.discover_capabilities,
            )
        return self._register_backend

    @property
    def unregister_backend(self) -> UnregisterBackend:
        if self._unregister_backend is None:
            self._unregister_backend = UnregisterBackend(
                backend_repository=self.backend_repository,
                config_repository=self.config_repository,
                process_manager=self.process_manager,
                port_allocator=self.port_allocator,
                client_factory=self.client_factory,
            )
        return self._unregister_backend

    @property
    def reload_backends(self) -> ReloadBackendsConfig:
        if self._reload_backends is None:
            self._reload_backends = ReloadBackendsConfig(
                backend_repository=self.backend_repository,
                config_repository=self.config_repository,
                register_backend=self.register_backend,
                unregister_backend=self.unregister_backend,
            )
        return self._reload_backends

    @property
    def monitor_processes(self) -> MonitorBackendProcesses:
        if self._monitor_processes is None:
            self._monitor_processes = MonitorBackendProcesses(
                backend_repository=self.backend_repository,
                process_manager=self.process_manager,
            )
        return self._monitor_processes

    @property
    def config_watcher(self) -> ConfigWatcher:
        if self._config_watcher is None:
            self._config_watcher = ConfigWatcher(
                config_repository=self.config_repository,
                reload_backends=self.reload_backends,
            )
        return self._config_watcher

    async def initialize_backends(self) -> None:
        logger.info(f"Loading backends from: {self.backends_config_path}")

        configs = await self.config_repository.load_configs()
        logger.info(f"Loaded {len(configs)} backend configurations")

        for config in configs:
            backend = Backend(config=config)

            if config.source.process_config and config.auto_start:
                try:
                    pid = await self.process_manager.start_process(
                        config.source.process_config
                    )
                    backend.process_id = pid
                    logger.info(f"Started process for {config.name} (PID: {pid})")
                except Exception as e:
                    logger.error(f"Failed to start {config.name}: {e}")
                    continue

            client = HTTPMCPClient(
                base_url=config.url,
                timeout=self.request_timeout,
            )
            self.client_factory[config.name] = client

            self.backend_repository.add(backend)
            logger.debug(f"Initialized backend: {config.name}")

    async def shutdown(self) -> None:
        logger.info("Shutting down composition root")

        if self._config_watcher:
            await self._config_watcher.stop()

        if self._process_manager:
            await self._process_manager.shutdown_all()
