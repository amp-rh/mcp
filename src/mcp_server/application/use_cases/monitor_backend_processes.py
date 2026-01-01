from mcp_server.application.ports import ProcessManagerPort
from mcp_server.domain.repositories import BackendRepository


class MonitorBackendProcesses:
    def __init__(
        self,
        backend_repository: BackendRepository,
        process_manager: ProcessManagerPort,
    ) -> None:
        self.backend_repository = backend_repository
        self.process_manager = process_manager

    async def execute(self) -> None:
        backends = self.backend_repository.get_all()

        for backend in backends:
            if not backend.is_managed_process or not backend.process_id:
                continue

            alive = await self.process_manager.is_process_alive(backend.process_id)

            if not alive and backend.config.auto_start:
                try:
                    new_pid = await self.process_manager.start_process(
                        backend.config.source.process_config
                    )
                    backend.process_id = new_pid
                    backend.record_success()
                except Exception as e:
                    backend.record_failure(f"Failed to restart process: {e}")
