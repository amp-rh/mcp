import asyncio
import logging
from typing import Any

from fastmcp import FastMCP

from mcp_server.config import RouterConfig, ServerConfig
from mcp_server.prompts import register_prompts
from mcp_server.resources import register_resources
from mcp_server.routing.backends import Backend, BackendManager
from mcp_server.routing.client import MCPClient
from mcp_server.routing.config_loader import load_backends_config
from mcp_server.routing.engine import RoutingEngine
from mcp_server.routing.exceptions import RouterError
from mcp_server.routing.health import HealthChecker
from mcp_server.tools import register_tools

logger = logging.getLogger(__name__)


def create_server(config: ServerConfig | None = None) -> FastMCP:
    """Create a traditional MCP server (template mode)."""
    config = config or ServerConfig.from_env()
    server = FastMCP(config.name)
    register_tools(server)
    register_resources(server)
    register_prompts(server)
    return server


async def create_router_server(
    config: RouterConfig | None = None,
) -> FastMCP:
    """Create an MCP router server that aggregates multiple backends.

    Args:
        config: Router configuration. If None, loads from environment.

    Returns:
        FastMCP server with proxied backend tools/resources/prompts

    Raises:
        ConfigurationError: If configuration is invalid
    """
    config = config or RouterConfig.from_env()
    server = FastMCP(config.name)

    logger.info(f"Creating router server: {config.name}")

    # Load backend configurations
    logger.info(f"Loading backends from: {config.backends_config_path}")
    backend_configs = load_backends_config(config.backends_config_path)
    logger.info(f"Loaded {len(backend_configs)} backend configurations")

    # Initialize routing components
    health_checker = HealthChecker(check_interval=config.health_check_interval)
    backend_manager = BackendManager(
        backend_configs,
        health_checker,
        capability_cache_ttl=config.capability_cache_ttl,
    )
    routing_engine = RoutingEngine(
        default_strategy=config.default_routing_strategy,
        max_retry_attempts=config.max_retry_attempts,
        retry_backoff_multiplier=config.retry_backoff_multiplier,
        max_retry_backoff=config.max_retry_backoff,
    )

    # Initialize backend clients
    for config_item in backend_configs:
        client = MCPClient(config_item.url, timeout=config.request_timeout)
        backend = Backend(config_item, client)
        backend_manager.backends[config_item.name] = backend
        logger.debug(f"Initialized backend client: {config_item.name}")

    # Discover backend capabilities on startup
    logger.info("Discovering backend capabilities...")
    await backend_manager.discover_capabilities()

    # Register proxied tools from backends
    await register_proxied_tools(
        server,
        backend_manager,
        routing_engine,
        config.enable_namespace_prefixing,
    )

    # Register proxied resources
    await register_proxied_resources(
        server,
        backend_manager,
        routing_engine,
        config.enable_namespace_prefixing,
    )

    # Register proxied prompts
    await register_proxied_prompts(
        server,
        backend_manager,
        routing_engine,
        config.enable_namespace_prefixing,
    )

    # Register router management tools
    register_router_tools(server, backend_manager, routing_engine)

    # Start background health checker
    await health_checker.start(backend_manager)

    logger.info("Router server initialization complete")

    return server


async def register_proxied_tools(
    server: FastMCP,
    backend_manager: BackendManager,
    routing_engine: RoutingEngine,
    enable_namespace_prefixing: bool,
) -> None:
    """Register tools from all backends as proxied tools on the router.

    Args:
        server: FastMCP server instance
        backend_manager: Backend manager with discovered tools
        routing_engine: Router for routing tool calls
        enable_namespace_prefixing: Whether to prefix tool names with namespace
    """
    tool_count = 0

    for backend_name, backend in backend_manager.backends.items():
        for tool_info in backend.tools:
            original_name = tool_info.get("name")
            if not original_name:
                continue

            # Apply namespace prefixing
            if enable_namespace_prefixing:
                proxied_name = (
                    f"{backend.config.namespace}.{original_name}"
                )
            else:
                proxied_name = original_name

            # Create proxy function
            def make_proxy(backend_ref: Backend, tool_name: str):
                async def proxy_tool(**kwargs: Any) -> Any:
                    try:
                        # Find appropriate route config for this tool
                        matching_backends = (
                            backend_manager.get_backends_for_tool(tool_name)
                        )
                        if not matching_backends:
                            matching_backends = [backend_ref]

                        # Route the call
                        decision = await routing_engine.route_by_capability(
                            tool_name,
                            matching_backends,
                        )
                        selected_backend = decision.backend

                        # Execute with retry
                        result = await routing_engine.call_with_retry(
                            selected_backend.client.call_tool,
                            tool_name,
                            kwargs,
                        )

                        backend_manager.health_checker.record_success(
                            selected_backend.config.name
                        )
                        return result

                    except Exception as e:
                        logger.error(
                            f"Error calling tool {tool_name} "
                            f"on {backend_ref.config.name}: {e}"
                        )
                        backend_manager.health_checker.record_failure(
                            backend_ref.config.name,
                            e,
                        )
                        raise RouterError(
                            f"Failed to call {proxied_name}: {e}",
                            backend=backend_ref.config.name,
                            original_error=e,
                        ) from e

                return proxy_tool

            proxy_fn = make_proxy(backend, original_name)
            proxy_fn.__name__ = proxied_name.replace(".", "_")
            description = tool_info.get("description", "")

            # Register with FastMCP
            server.tool(
                name=proxied_name,
                description=description,
            )(proxy_fn)

            tool_count += 1
            logger.debug(f"Registered proxied tool: {proxied_name}")

    logger.info(f"Registered {tool_count} proxied tools")


async def register_proxied_resources(
    server: FastMCP,
    backend_manager: BackendManager,
    routing_engine: RoutingEngine,
    enable_namespace_prefixing: bool,
) -> None:
    """Register resources from all backends as proxied resources.

    Args:
        server: FastMCP server instance
        backend_manager: Backend manager with discovered resources
        routing_engine: Router for routing resource calls
        enable_namespace_prefixing: Whether to prefix resource URIs with namespace
    """
    resource_count = 0

    for backend_name, backend in backend_manager.backends.items():
        for resource_info in backend.resources:
            original_uri = resource_info.get("uri")
            if not original_uri:
                continue

            # Apply namespace prefixing
            if enable_namespace_prefixing:
                proxied_uri = (
                    f"{backend.config.namespace}://{original_uri}"
                )
            else:
                proxied_uri = original_uri

            # Create proxy function
            def make_resource_proxy(backend_ref: Backend, uri: str):
                async def proxy_resource() -> str:
                    try:
                        result = await routing_engine.call_with_retry(
                            backend_ref.client.get_resource,
                            uri,
                        )
                        backend_manager.health_checker.record_success(
                            backend_ref.config.name
                        )
                        return result

                    except Exception as e:
                        logger.error(
                            f"Error fetching resource {uri} "
                            f"from {backend_ref.config.name}: {e}"
                        )
                        backend_manager.health_checker.record_failure(
                            backend_ref.config.name,
                            e,
                        )
                        raise RouterError(
                            f"Failed to get resource {proxied_uri}: {e}",
                            backend=backend_ref.config.name,
                            original_error=e,
                        ) from e

                return proxy_resource

            proxy_fn = make_resource_proxy(backend, original_uri)
            description = resource_info.get("description", "")

            # Register with FastMCP
            server.resource(
                uri_template=proxied_uri,
                description=description,
            )(proxy_fn)

            resource_count += 1
            logger.debug(f"Registered proxied resource: {proxied_uri}")

    logger.info(f"Registered {resource_count} proxied resources")


async def register_proxied_prompts(
    server: FastMCP,
    backend_manager: BackendManager,
    routing_engine: RoutingEngine,
    enable_namespace_prefixing: bool,
) -> None:
    """Register prompts from all backends as proxied prompts.

    Args:
        server: FastMCP server instance
        backend_manager: Backend manager with discovered prompts
        routing_engine: Router for routing prompt calls
        enable_namespace_prefixing: Whether to prefix prompt names with namespace
    """
    prompt_count = 0

    for backend_name, backend in backend_manager.backends.items():
        for prompt_info in backend.prompts:
            original_name = prompt_info.get("name")
            if not original_name:
                continue

            # Apply namespace prefixing
            if enable_namespace_prefixing:
                proxied_name = (
                    f"{backend.config.namespace}.{original_name}"
                )
            else:
                proxied_name = original_name

            # Create proxy function - for now just log
            description = prompt_info.get("description", "")
            logger.debug(f"Registered proxied prompt: {proxied_name}")
            prompt_count += 1

    logger.info(f"Registered {prompt_count} proxied prompts")


def register_router_tools(
    server: FastMCP,
    backend_manager: BackendManager,
    routing_engine: RoutingEngine,
) -> None:
    """Register router management tools.

    Args:
        server: FastMCP server instance
        backend_manager: Backend manager
        routing_engine: Routing engine
    """

    @server.tool
    def list_backends() -> list[dict[str, Any]]:
        """List all configured backends with their health status."""
        return [
            {
                "name": backend.config.name,
                "url": backend.config.url,
                "namespace": backend.config.namespace,
                "priority": backend.config.priority,
                "healthy": not backend_manager.health_checker.is_circuit_open(
                    backend.config.name
                ),
                "circuit_state": backend.health_status.circuit_state,
                "error_count": backend.health_status.error_count,
            }
            for backend in backend_manager.backends.values()
        ]

    @server.tool
    def get_backend_health(backend_name: str) -> dict[str, Any]:
        """Get detailed health information for a specific backend.

        Args:
            backend_name: Name of the backend to check

        Returns:
            Dictionary with health status details
        """
        status = backend_manager.health_checker.get_health_status(
            backend_name
        )
        return {
            "name": backend_name,
            "healthy": status.is_healthy,
            "circuit_state": status.circuit_state,
            "error_count": status.error_count,
            "last_error": status.last_error,
        }

    logger.info("Registered router management tools")


# Module-level mcp instance for backward compatibility
mcp = create_server()


def main() -> None:
    """Entry point for traditional server."""
    mcp.run()


def main_router() -> None:
    """Entry point for router server mode."""
    asyncio.run(_run_router())


async def _run_router() -> None:
    """Run the router server."""
    router = await create_router_server()
    await router.run()


if __name__ == "__main__":
    main()

