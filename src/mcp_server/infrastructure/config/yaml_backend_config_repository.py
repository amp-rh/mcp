from collections.abc import AsyncIterator
from pathlib import Path

import yaml
from watchfiles import awatch

from mcp_server.domain.exceptions import ConfigurationWatchError, InvalidConfigurationError
from mcp_server.domain.repositories import ConfigRepository
from mcp_server.domain.services.namespace_generator import NamespaceGenerator
from mcp_server.domain.value_objects import (
    BackendConfig,
    BackendSource,
    BackendSourceType,
    CircuitBreakerSettings,
    GitHubSpec,
    HealthCheckSettings,
    ProcessConfig,
    RoutePattern,
)


class YamlBackendConfigRepository(ConfigRepository):
    def __init__(self, config_path: str) -> None:
        self.config_path = Path(config_path).expanduser()
        self._ensure_config_exists()

    def _ensure_config_exists(self) -> None:
        if not self.config_path.exists():
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self.config_path.write_text("backends: []\n")

    async def load_configs(self) -> list[BackendConfig]:
        if not self.config_path.exists():
            return []

        try:
            with open(self.config_path) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise InvalidConfigurationError(f"Invalid YAML: {e}") from e

        if not data or "backends" not in data:
            return []

        configs = []
        for backend_data in data.get("backends", []):
            config = self._parse_backend_config(backend_data)
            configs.append(config)

        return configs

    async def save_config(self, config: BackendConfig) -> None:
        configs = await self.load_configs()
        configs = [c for c in configs if c.name != config.name]
        configs.append(config)
        await self._write_configs(configs)

    async def remove_config(self, backend_name: str) -> None:
        configs = await self.load_configs()
        configs = [c for c in configs if c.name != backend_name]
        await self._write_configs(configs)

    async def watch_changes(self) -> AsyncIterator[list[BackendConfig]]:
        async for changes in awatch(self.config_path):
            try:
                configs = await self.load_configs()
                yield configs
            except Exception as e:
                raise ConfigurationWatchError(f"Error reloading config: {e}") from e

    async def _write_configs(self, configs: list[BackendConfig]) -> None:
        data = {"backends": [self._config_to_dict(c) for c in configs]}

        temp_path = self.config_path.with_suffix(".tmp")
        with open(temp_path, "w") as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)

        temp_path.replace(self.config_path)

    def _parse_backend_config(self, data: dict) -> BackendConfig:
        name = data.get("name")
        if not name:
            raise InvalidConfigurationError("Backend name is required")

        source_str = data.get("source") or data.get("url")
        if not source_str:
            raise InvalidConfigurationError(f"Backend {name} missing source or url")

        namespace = data.get("namespace")
        source = self._parse_source(source_str, data)

        if not namespace:
            namespace = NamespaceGenerator.generate(source)

        routes = []
        for route_data in data.get("routes", []):
            routes.append(
                RoutePattern(
                    pattern=route_data.get("pattern", "*"),
                    strategy=route_data.get("strategy", "capability"),
                    fallback_to=route_data.get("fallback_to"),
                )
            )

        health_check_data = data.get("health_check", {})
        health_check = HealthCheckSettings(
            enabled=health_check_data.get("enabled", True),
            interval_seconds=health_check_data.get("interval_seconds", 30),
            timeout_seconds=health_check_data.get("timeout_seconds", 5),
            endpoint=health_check_data.get("endpoint"),
        )

        circuit_breaker_data = data.get("circuit_breaker", {})
        circuit_breaker = CircuitBreakerSettings(
            failure_threshold=circuit_breaker_data.get("failure_threshold", 5),
            timeout_seconds=circuit_breaker_data.get("timeout_seconds", 60),
            half_open_attempts=circuit_breaker_data.get("half_open_attempts", 3),
        )

        return BackendConfig(
            name=name,
            source=source,
            namespace=namespace,
            priority=data.get("priority", 10),
            routes=tuple(routes),
            health_check=health_check,
            circuit_breaker=circuit_breaker,
            auto_start=data.get("auto_start", True),
        )

    def _parse_source(self, source_str: str, data: dict) -> BackendSource:
        if source_str.startswith("http://") or source_str.startswith("https://"):
            return BackendSource(
                source_type=BackendSourceType.HTTP,
                http_url=source_str,
            )

        if source_str.startswith("github:"):
            github_spec = GitHubSpec.from_url(source_str)
            port = data.get("port")

            process_config = ProcessConfig(
                command="uvx",
                args=(github_spec.to_package_name(),),
                port=port,
            )

            return BackendSource(
                source_type=BackendSourceType.GITHUB,
                github_spec=github_spec,
                process_config=process_config,
            )

        port = data.get("port")
        process_config = ProcessConfig(
            command="uvx",
            args=(source_str,),
            port=port,
        )

        return BackendSource(
            source_type=BackendSourceType.PACKAGE,
            package_name=source_str,
            process_config=process_config,
        )

    def _config_to_dict(self, config: BackendConfig) -> dict:
        if config.source.http_url:
            source_str = config.source.http_url
        elif config.source.github_spec:
            source_str = f"github:{config.source.github_spec.owner}/{config.source.github_spec.repo}"
        else:
            source_str = config.source.package_name

        result = {
            "name": config.name,
            "source": source_str,
            "namespace": config.namespace,
            "priority": config.priority,
            "auto_start": config.auto_start,
        }

        if config.source.process_config and config.source.process_config.port:
            result["port"] = config.source.process_config.port

        if config.routes:
            result["routes"] = [
                {
                    "pattern": r.pattern,
                    "strategy": r.strategy,
                    **({"fallback_to": r.fallback_to} if r.fallback_to else {}),
                }
                for r in config.routes
            ]

        result["health_check"] = {
            "enabled": config.health_check.enabled,
            "interval_seconds": config.health_check.interval_seconds,
            "timeout_seconds": config.health_check.timeout_seconds,
        }
        if config.health_check.endpoint:
            result["health_check"]["endpoint"] = config.health_check.endpoint

        result["circuit_breaker"] = {
            "failure_threshold": config.circuit_breaker.failure_threshold,
            "timeout_seconds": config.circuit_breaker.timeout_seconds,
            "half_open_attempts": config.circuit_breaker.half_open_attempts,
        }

        return result
