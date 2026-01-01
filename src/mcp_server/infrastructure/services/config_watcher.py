import asyncio
import logging
from typing import TYPE_CHECKING

from mcp_server.domain.repositories import ConfigRepository

if TYPE_CHECKING:
    from mcp_server.application.use_cases import ReloadBackendsConfig

logger = logging.getLogger(__name__)


class ConfigWatcher:
    def __init__(
        self,
        config_repository: ConfigRepository,
        reload_backends: "ReloadBackendsConfig",
    ) -> None:
        self.config_repository = config_repository
        self.reload_backends = reload_backends
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        self._task = asyncio.create_task(self._watch_loop())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _watch_loop(self) -> None:
        logger.info("Starting config file watcher")

        try:
            async for configs in self.config_repository.watch_changes():
                logger.info("Config file changed, reloading backends")
                try:
                    results = await self.reload_backends.execute()
                    logger.info(f"Reload complete: {results}")
                except Exception as e:
                    logger.error(f"Error reloading backends: {e}", exc_info=True)
        except asyncio.CancelledError:
            logger.info("Config watcher stopped")
        except Exception as e:
            logger.error(f"Config watcher error: {e}", exc_info=True)
