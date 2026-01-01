from typing import TYPE_CHECKING, Any

from mcp_server.application.dtos import BackendRegistrationRequest
from mcp_server.domain.repositories import BackendRepository, ConfigRepository

if TYPE_CHECKING:
    from mcp_server.application.use_cases import RegisterBackend, UnregisterBackend


class ReloadBackendsConfig:
    def __init__(
        self,
        backend_repository: BackendRepository,
        config_repository: ConfigRepository,
        register_backend: "RegisterBackend",
        unregister_backend: "UnregisterBackend",
    ) -> None:
        self.backend_repository = backend_repository
        self.config_repository = config_repository
        self.register_backend = register_backend
        self.unregister_backend = unregister_backend

    async def execute(self) -> dict[str, Any]:
        new_configs = await self.config_repository.load_configs()
        new_names = {cfg.name for cfg in new_configs}

        current_backends = self.backend_repository.get_all()
        current_names = {b.name for b in current_backends}

        to_remove = current_names - new_names
        to_add = new_names - current_names
        to_update = current_names & new_names

        results = {
            "added": [],
            "removed": [],
            "updated": [],
            "errors": [],
        }

        for name in to_remove:
            try:
                await self.unregister_backend.execute(name)
                results["removed"].append(name)
            except Exception as e:
                results["errors"].append(f"Error removing {name}: {e}")

        for config in new_configs:
            if config.name in to_add:
                try:
                    request = self._config_to_request(config)
                    await self.register_backend.execute(request)
                    results["added"].append(config.name)
                except Exception as e:
                    results["errors"].append(f"Error adding {config.name}: {e}")

        for config in new_configs:
            if config.name in to_update:
                current = self.backend_repository.get(config.name)
                if current and current.config != config:
                    try:
                        await self.unregister_backend.execute(config.name)
                        request = self._config_to_request(config)
                        await self.register_backend.execute(request)
                        results["updated"].append(config.name)
                    except Exception as e:
                        results["errors"].append(f"Error updating {config.name}: {e}")

        return results

    def _config_to_request(self, config) -> BackendRegistrationRequest:
        source_str = ""
        if config.source.http_url:
            source_str = config.source.http_url
        elif config.source.github_spec:
            source_str = (
                f"github:{config.source.github_spec.owner}/{config.source.github_spec.repo}"
            )
        elif config.source.package_name:
            source_str = config.source.package_name

        return BackendRegistrationRequest(
            source=source_str,
            name=config.name,
            namespace=config.namespace,
            priority=config.priority,
            auto_start=config.auto_start,
            health_check_enabled=config.health_check.enabled,
        )
