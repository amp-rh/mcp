import asyncio
import os
import signal

from mcp_server.application.ports import ProcessManagerPort
from mcp_server.domain.exceptions import ProcessManagementError
from mcp_server.domain.value_objects import ProcessConfig


class UvxProcessManager(ProcessManagerPort):
    def __init__(self) -> None:
        self._processes: dict[int, asyncio.subprocess.Process] = {}

    async def start_process(self, config: ProcessConfig) -> int:
        cmd = [config.command, *config.args]
        env = {**os.environ, **config.env}
        if config.port:
            env["PORT"] = str(config.port)

        process = await asyncio.create_subprocess_exec(
            *cmd,
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        if not process.pid:
            raise ProcessManagementError("Failed to start process")

        self._processes[process.pid] = process
        await asyncio.sleep(2)

        return process.pid

    async def stop_process(self, pid: int) -> None:
        process = self._processes.get(pid)
        if not process:
            return

        try:
            process.terminate()
            await asyncio.wait_for(process.wait(), timeout=5.0)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
        finally:
            self._processes.pop(pid, None)

    async def is_process_alive(self, pid: int) -> bool:
        process = self._processes.get(pid)
        if not process:
            return False

        return process.returncode is None

    async def restart_process(self, pid: int, config: ProcessConfig) -> int:
        await self.stop_process(pid)
        return await self.start_process(config)

    async def shutdown_all(self) -> None:
        for pid in list(self._processes.keys()):
            await self.stop_process(pid)
