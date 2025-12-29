"""Backend management and capability discovery."""

import logging
from datetime import datetime, timedelta

from mcp_server.routing.exceptions import CapabilityDiscoveryError
from mcp_server.routing.models import BackendConfig, HealthStatus

logger = logging.getLogger(__name__)


class Backend:
    """Represents a single backend MCP server."""

    def __init__(self, config: BackendConfig, client: "MCPClient"):  # noqa: F821
        """Initialize a backend.

        Args:
            config: Backend configuration
            client: HTTP client for this backend
        """
        self.config = config
        self.client = client
        self.health_status = HealthStatus(backend_name=config.name)
        self.tools = []
        self.resources = []
        self.prompts = []


class BackendManager:
    """Manages all backend MCP servers and capability discovery."""

    def __init__(
        self,
        configs: list[BackendConfig],
        health_checker: "HealthChecker",  # noqa: F821
        capability_cache_ttl: int = 300,
    ):
        """Initialize backend manager.

        Args:
            configs: List of backend configurations
            health_checker: HealthChecker instance for monitoring
            capability_cache_ttl: Cache TTL for capabilities in seconds
        """
        self.configs = {config.name: config for config in configs}
        self.backends = {}
        self.health_checker = health_checker
        self.capability_cache_ttl = capability_cache_ttl
        self.capability_cache = {}
        self.last_capability_refresh = None

    async def discover_capabilities(self) -> None:
        """Discover capabilities from all backends on startup.

        This queries each backend for its available tools, resources, and prompts.

        Raises:
            CapabilityDiscoveryError: If critical discovery failures occur
        """
        for backend_name, backend in self.backends.items():
            try:
                logger.debug(f"Discovering capabilities for backend: {backend_name}")

                tools = await backend.client.list_tools()
                resources = await backend.client.list_resources()
                prompts = await backend.client.list_prompts()

                backend.tools = tools
                backend.resources = resources
                backend.prompts = prompts

                logger.info(
                    f"Discovered {len(tools)} tools, {len(resources)} resources, "
                    f"{len(prompts)} prompts from {backend_name}"
                )
            except Exception as e:
                logger.warning(
                    f"Failed to discover capabilities for {backend_name}: {e}"
                )
                self.health_checker.record_failure(backend_name, e)

        self.last_capability_refresh = datetime.now()
        self._update_capability_cache()

    async def refresh_capabilities(self) -> None:
        """Refresh capability cache (periodic background task)."""
        logger.debug("Refreshing backend capabilities")
        await self.discover_capabilities()

    def get_backends_for_tool(self, tool_name: str) -> list[Backend]:
        """Get backends that support a given tool.

        Args:
            tool_name: Name of the tool to find

        Returns:
            List of backends that have this tool
        """
        backends = []
        for backend in self.backends.values():
            if any(t.get("name") == tool_name for t in backend.tools):
                backends.append(backend)
        return backends

    def get_healthy_backends(self) -> list[Backend]:
        """Get all backends with healthy circuit breakers.

        Returns:
            List of backends that are currently healthy
        """
        return [
            backend
            for backend in self.backends.values()
            if not self.health_checker.is_circuit_open(backend.config.name)
        ]

    def _update_capability_cache(self) -> None:
        """Update the capability cache from current backend state."""
        cache = {}
        for backend_name, backend in self.backends.items():
            cache[backend_name] = {
                "tools": backend.tools,
                "resources": backend.resources,
                "prompts": backend.prompts,
                "timestamp": datetime.now(),
            }
        self.capability_cache = cache

    def is_capability_cache_expired(self) -> bool:
        """Check if capability cache has expired.

        Returns:
            True if cache is expired, False otherwise
        """
        if not self.last_capability_refresh:
            return True

        age = datetime.now() - self.last_capability_refresh
        return age > timedelta(seconds=self.capability_cache_ttl)

    def get_backend(self, name: str) -> Backend | None:
        """Get a backend by name.

        Args:
            name: Name of the backend

        Returns:
            Backend object or None if not found
        """
        return self.backends.get(name)
