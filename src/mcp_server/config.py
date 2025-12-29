import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ServerConfig:
    """Configuration for MCP server (template/legacy)."""

    name: str = "mcp-server"
    host: str = "0.0.0.0"
    port: int = 8000

    @classmethod
    def from_env(cls) -> "ServerConfig":
        return cls(
            name=os.getenv("MCP_SERVER_NAME", "mcp-server"),
            host=os.getenv("MCP_HOST", "0.0.0.0"),
            port=int(os.getenv("MCP_PORT", "8000")),
        )


@dataclass(frozen=True)
class RouterConfig:
    """Configuration for MCP router server."""

    name: str = "mcp-router"
    host: str = "0.0.0.0"
    port: int = 8000
    backends_config_path: str = "config/backends.yaml"
    # Routing settings
    default_routing_strategy: str = "capability"
    enable_namespace_prefixing: bool = True
    capability_cache_ttl: int = 300  # seconds
    request_timeout: int = 30  # seconds
    # Health check settings
    health_check_interval: int = 30  # seconds
    health_check_timeout: int = 5  # seconds
    # Retry settings
    max_retry_attempts: int = 3
    retry_backoff_multiplier: float = 2.0
    max_retry_backoff: int = 10  # seconds
    # Circuit breaker defaults
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_timeout: int = 60  # seconds
    circuit_breaker_half_open_attempts: int = 3

    @classmethod
    def from_env(cls) -> "RouterConfig":
        """Load router configuration from environment variables."""
        return cls(
            name=os.getenv("MCP_SERVER_NAME", "mcp-router"),
            host=os.getenv("MCP_HOST", "0.0.0.0"),
            port=int(os.getenv("MCP_PORT", "8000")),
            backends_config_path=os.getenv(
                "MCP_BACKENDS_CONFIG",
                "config/backends.yaml",
            ),
            default_routing_strategy=os.getenv(
                "MCP_DEFAULT_STRATEGY",
                "capability",
            ),
            enable_namespace_prefixing=os.getenv(
                "MCP_ENABLE_NAMESPACES",
                "true",
            ).lower() == "true",
            capability_cache_ttl=int(os.getenv("MCP_CACHE_TTL", "300")),
            request_timeout=int(os.getenv("MCP_REQUEST_TIMEOUT", "30")),
            health_check_interval=int(
                os.getenv("MCP_HEALTH_CHECK_INTERVAL", "30")
            ),
            health_check_timeout=int(
                os.getenv("MCP_HEALTH_CHECK_TIMEOUT", "5")
            ),
            max_retry_attempts=int(os.getenv("MCP_MAX_RETRIES", "3")),
            retry_backoff_multiplier=float(
                os.getenv("MCP_RETRY_BACKOFF", "2.0")
            ),
            max_retry_backoff=int(os.getenv("MCP_MAX_BACKOFF", "10")),
        )

