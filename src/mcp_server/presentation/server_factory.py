import asyncio
import logging
from typing import Any

from fastmcp import FastMCP

from mcp_server.application.dtos import ToolCallRequest
from mcp_server.config import RouterConfig, ServerConfig
from mcp_server.presentation.composition_root import CompositionRoot
from mcp_server.prompts import register_prompts
from mcp_server.resources import register_resources
from mcp_server.tools import register_tools

logger = logging.getLogger(__name__)


def create_server(config: ServerConfig | None = None) -> FastMCP:
    config = config or ServerConfig.from_env()
    server = FastMCP(config.name)
    register_tools(server)
    register_resources(server)
    register_prompts(server)
    return server


async def create_router_server(config: RouterConfig | None = None) -> FastMCP:
    config = config or RouterConfig.from_env()
    server = FastMCP(config.name)

    logger.info(f"Creating router server: {config.name}")

    composition_root = CompositionRoot(
        backends_config_path=config.backends_config_path,
        request_timeout=config.request_timeout,
        max_retry_attempts=config.max_retry_attempts,
        retry_backoff_multiplier=config.retry_backoff_multiplier,
        max_retry_backoff=config.max_retry_backoff,
    )

    logger.info("Discovering backend capabilities...")
    await composition_root.discover_capabilities.execute()

    await _register_proxied_tools(
        server,
        composition_root,
        config.enable_namespace_prefixing,
    )

    await _register_proxied_resources(
        server,
        composition_root,
        config.enable_namespace_prefixing,
    )

    await _register_proxied_prompts(
        server,
        composition_root,
        config.enable_namespace_prefixing,
    )

    _register_router_tools(server, composition_root)

    asyncio.create_task(
        _run_health_checker(
            composition_root,
            config.health_check_interval,
        )
    )

    logger.info("Router server initialization complete")

    return server


async def _register_proxied_tools(
    server: FastMCP,
    composition_root: CompositionRoot,
    enable_namespace_prefixing: bool,
) -> None:
    tool_count = 0
    backends = composition_root.backend_repository.get_all()

    for backend in backends:
        for tool_info in backend.tools:
            original_name = tool_info.get("name")
            if not original_name:
                continue

            proxied_name = (
                f"{backend.config.namespace}.{original_name}"
                if enable_namespace_prefixing
                else original_name
            )

            def make_proxy(tool_name: str, display_name: str):
                async def proxy_tool(**kwargs: Any) -> Any:
                    request = ToolCallRequest(
                        tool_name=tool_name,
                        arguments=kwargs,
                    )
                    response = await composition_root.route_tool_call.execute(request)
                    return response.result

                return proxy_tool

            proxy_fn = make_proxy(original_name, proxied_name)
            proxy_fn.__name__ = proxied_name.replace(".", "_")
            description = tool_info.get("description", "")

            server.tool(
                name=proxied_name,
                description=description,
            )(proxy_fn)

            tool_count += 1
            logger.debug(f"Registered proxied tool: {proxied_name}")

    logger.info(f"Registered {tool_count} proxied tools")


async def _register_proxied_resources(
    server: FastMCP,
    composition_root: CompositionRoot,
    enable_namespace_prefixing: bool,
) -> None:
    resource_count = 0
    backends = composition_root.backend_repository.get_all()

    for backend in backends:
        for resource_info in backend.resources:
            original_uri = resource_info.get("uri")
            if not original_uri:
                continue

            proxied_uri = (
                f"{backend.config.namespace}://{original_uri}"
                if enable_namespace_prefixing
                else original_uri
            )

            def make_resource_proxy(backend_name: str, uri: str):
                async def proxy_resource() -> str:
                    client = composition_root.client_factory.get(backend_name)
                    if not client:
                        raise ValueError(f"Backend not found: {backend_name}")
                    return await client.get_resource(uri)

                return proxy_resource

            proxy_fn = make_resource_proxy(backend.name, original_uri)
            description = resource_info.get("description", "")

            server.resource(
                uri_template=proxied_uri,
                description=description,
            )(proxy_fn)

            resource_count += 1
            logger.debug(f"Registered proxied resource: {proxied_uri}")

    logger.info(f"Registered {resource_count} proxied resources")


async def _register_proxied_prompts(
    server: FastMCP,
    composition_root: CompositionRoot,
    enable_namespace_prefixing: bool,
) -> None:
    prompt_count = 0
    backends = composition_root.backend_repository.get_all()

    for backend in backends:
        for prompt_info in backend.prompts:
            original_name = prompt_info.get("name")
            if not original_name:
                continue

            proxied_name = (
                f"{backend.config.namespace}.{original_name}"
                if enable_namespace_prefixing
                else original_name
            )

            logger.debug(f"Registered proxied prompt: {proxied_name}")
            prompt_count += 1

    logger.info(f"Registered {prompt_count} proxied prompts")


def _register_router_tools(
    server: FastMCP,
    composition_root: CompositionRoot,
) -> None:
    @server.tool
    def list_backends() -> list[dict[str, Any]]:
        backends = composition_root.backend_repository.get_all()
        return [
            {
                "name": backend.name,
                "url": backend.config.url,
                "namespace": backend.config.namespace,
                "priority": backend.config.priority,
                "healthy": backend.is_healthy,
                "circuit_state": backend.health_status.circuit_state.value,
                "error_count": backend.health_status.error_count,
            }
            for backend in backends
        ]

    @server.tool
    def get_backend_health(backend_name: str) -> dict[str, Any]:
        backend = composition_root.backend_repository.get(backend_name)
        if not backend:
            raise ValueError(f"Backend not found: {backend_name}")

        return {
            "name": backend.name,
            "healthy": backend.is_healthy,
            "circuit_state": backend.health_status.circuit_state.value,
            "error_count": backend.health_status.error_count,
            "last_error": backend.health_status.last_error,
        }

    logger.info("Registered router management tools")


async def _run_health_checker(
    composition_root: CompositionRoot,
    interval: int,
) -> None:
    while True:
        await asyncio.sleep(interval)
        await composition_root.check_backend_health.execute()
