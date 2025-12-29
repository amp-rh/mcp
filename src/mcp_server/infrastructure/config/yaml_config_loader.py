from pathlib import Path

import yaml

from mcp_server.domain.exceptions import InvalidConfigurationError
from mcp_server.domain.value_objects import (
    BackendConfig,
    CircuitBreakerSettings,
    HealthCheckSettings,
    RoutePattern,
)


def load_backend_configs(config_path: str) -> list[BackendConfig]:
    config_file = Path(config_path)

    if not config_file.exists():
        raise InvalidConfigurationError(f"Configuration file not found: {config_path}")

    try:
        with open(config_file) as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise InvalidConfigurationError(f"Invalid YAML in config file: {e}") from e
    except OSError as e:
        raise InvalidConfigurationError(f"Error reading config file: {e}") from e

    if not data or "backends" not in data:
        raise InvalidConfigurationError("Config must contain 'backends' key")

    backends = []
    for backend_data in data.get("backends", []):
        try:
            backend = _parse_backend_config(backend_data)
            backends.append(backend)
        except (KeyError, ValueError, TypeError) as e:
            backend_name = backend_data.get("name", "unknown")
            raise InvalidConfigurationError(
                f"Invalid backend config for '{backend_name}': {e}"
            ) from e

    if not backends:
        raise InvalidConfigurationError(
            "At least one backend must be configured.\n"
            "Please edit config/backends.yaml and add backend servers.\n"
            "See config/backends.yaml.example for examples.\n"
            "For a simple MCP server without routing, "
            "use 'mcp-server' instead of 'mcp-router'."
        )

    return backends


def _parse_backend_config(data: dict) -> BackendConfig:
    name = data.get("name")
    url = data.get("url")
    namespace = data.get("namespace")

    if not name or not url or not namespace:
        raise ValueError("Backend must have name, url, and namespace")

    priority = data.get("priority", 10)

    routes = []
    for route_data in data.get("routes", []):
        pattern = route_data.get("pattern")
        strategy = route_data.get("strategy", "capability")

        if not pattern:
            raise ValueError("Route must have a 'pattern'")

        route = RoutePattern(
            pattern=pattern,
            strategy=strategy,
            fallback_to=route_data.get("fallback_to"),
        )
        routes.append(route)

    health_check_data = data.get("health_check", {})
    health_check = HealthCheckSettings(
        enabled=health_check_data.get("enabled", True),
        interval_seconds=health_check_data.get("interval_seconds", 30),
        timeout_seconds=health_check_data.get("timeout_seconds", 5),
        endpoint=health_check_data.get("endpoint"),
    )

    cb_data = data.get("circuit_breaker", {})
    circuit_breaker = CircuitBreakerSettings(
        failure_threshold=cb_data.get("failure_threshold", 5),
        timeout_seconds=cb_data.get("timeout_seconds", 60),
        half_open_attempts=cb_data.get("half_open_attempts", 3),
    )

    return BackendConfig(
        name=name,
        url=url,
        namespace=namespace,
        priority=priority,
        routes=tuple(routes),
        health_check=health_check,
        circuit_breaker=circuit_breaker,
    )
