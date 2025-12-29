import logging

from mcp_server.application.ports import MCPClientPort
from mcp_server.application.use_cases import (
    CheckBackendHealth,
    DiscoverCapabilities,
    RouteToolCall,
)
from mcp_server.domain.entities import Backend
from mcp_server.domain.repositories import BackendRepository
from mcp_server.domain.value_objects import BackendConfig
from mcp_server.infrastructure.adapters import HTTPMCPClient
from mcp_server.infrastructure.config import load_backend_configs
from mcp_server.infrastructure.repositories import InMemoryBackendRepository

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
        self.backends_config_path = backends_config_path
        self.request_timeout = request_timeout
        self.max_retry_attempts = max_retry_attempts
        self.retry_backoff_multiplier = retry_backoff_multiplier
        self.max_retry_backoff = max_retry_backoff

        self._backend_repository: BackendRepository | None = None
        self._client_factory: dict[str, MCPClientPort] | None = None
        self._route_tool_call: RouteToolCall | None = None
        self._discover_capabilities: DiscoverCapabilities | None = None
        self._check_backend_health: CheckBackendHealth | None = None

    @property
    def backend_repository(self) -> BackendRepository:
        if self._backend_repository is None:
            self._backend_repository = InMemoryBackendRepository()
            self._initialize_backends()
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

    def _initialize_backends(self) -> None:
        logger.info(f"Loading backends from: {self.backends_config_path}")
        backend_configs = load_backend_configs(self.backends_config_path)
        logger.info(f"Loaded {len(backend_configs)} backend configurations")

        for config in backend_configs:
            backend = self._create_backend(config)
            self.backend_repository.add(backend)

            client = self._create_client(config)
            self.client_factory[config.name] = client

            logger.debug(f"Initialized backend: {config.name}")

    def _create_backend(self, config: BackendConfig) -> Backend:
        return Backend(config=config)

    def _create_client(self, config: BackendConfig) -> MCPClientPort:
        return HTTPMCPClient(
            base_url=config.url,
            timeout=self.request_timeout,
        )
