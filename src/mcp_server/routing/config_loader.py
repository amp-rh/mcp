"""Load and validate backend configurations from YAML files."""

from pathlib import Path

import yaml

from mcp_server.routing.exceptions import ConfigurationError
from mcp_server.routing.models import (
    BackendConfig,
    CircuitBreakerConfig,
    HealthCheckConfig,
    RouteConfig,
)


def load_backends_config(config_path: str) -> list[BackendConfig]:
    """Load and parse backend configurations from a YAML file.

    Args:
        config_path: Path to the YAML configuration file

    Returns:
        List of BackendConfig objects

    Raises:
        ConfigurationError: If config file is invalid or missing
    """
    config_file = Path(config_path)

    if not config_file.exists():
        raise ConfigurationError(f"Configuration file not found: {config_path}")

    try:
        with open(config_file) as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML in config file: {e}") from e
    except OSError as e:
        raise ConfigurationError(f"Error reading config file: {e}") from e

    if not data or "backends" not in data:
        raise ConfigurationError("Config must contain 'backends' key")

    backends = []
    for backend_data in data.get("backends", []):
        try:
            backend = _parse_backend_config(backend_data)
            backends.append(backend)
        except (KeyError, ValueError, TypeError) as e:
            backend_name = backend_data.get("name", "unknown")
            raise ConfigurationError(
                f"Invalid backend config for '{backend_name}': {e}"
            ) from e

    if not backends:
        raise ConfigurationError("At least one backend must be configured")

    return backends


def _parse_backend_config(data: dict) -> BackendConfig:
    """Parse a single backend configuration dict.

    Args:
        data: Dictionary containing backend configuration

    Returns:
        BackendConfig object

    Raises:
        KeyError: If required fields are missing
        ValueError: If field values are invalid
    """
    # Required fields
    name = data.get("name")
    url = data.get("url")
    namespace = data.get("namespace")

    if not name:
        raise ValueError("Backend must have a 'name'")
    if not url:
        raise ValueError("Backend must have a 'url'")
    if not namespace:
        raise ValueError("Backend must have a 'namespace'")

    # Optional fields
    priority = data.get("priority", 10)
    if not isinstance(priority, int) or priority < 0:
        raise ValueError("Priority must be a non-negative integer")

    # Parse routes
    routes = []
    for route_data in data.get("routes", []):
        pattern = route_data.get("pattern")
        strategy = route_data.get("strategy", "capability")

        if not pattern:
            raise ValueError("Route must have a 'pattern'")
        if strategy not in ("path", "capability", "fallback"):
            raise ValueError(f"Invalid strategy: {strategy}")

        route = RouteConfig(
            pattern=pattern,
            strategy=strategy,
            fallback_to=route_data.get("fallback_to"),
        )
        routes.append(route)

    # Parse health check config
    health_check_data = data.get("health_check", {})
    health_check = HealthCheckConfig(
        enabled=health_check_data.get("enabled", True),
        interval_seconds=health_check_data.get("interval_seconds", 30),
        timeout_seconds=health_check_data.get("timeout_seconds", 5),
        endpoint=health_check_data.get("endpoint"),
    )

    # Parse circuit breaker config
    cb_data = data.get("circuit_breaker", {})
    circuit_breaker = CircuitBreakerConfig(
        failure_threshold=cb_data.get("failure_threshold", 5),
        timeout_seconds=cb_data.get("timeout_seconds", 60),
        half_open_attempts=cb_data.get("half_open_attempts", 3),
    )

    return BackendConfig(
        name=name,
        url=url,
        namespace=namespace,
        priority=priority,
        routes=routes,
        health_check=health_check,
        circuit_breaker=circuit_breaker,
    )
