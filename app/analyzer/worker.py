import asyncio

from app.core.config import settings
from app.services.analysis_service import AnalysisService
from app.services.camera_service import CameraService


class AnalyzerWorker:
    def __init__(
        self,
        camera_service: CameraService,
        analysis_service: AnalysisService,
    ) -> None:
        self.camera_service = camera_service
        self.analysis_service = analysis_service
        self._task: asyncio.Task | None = None
        self._stop_event = asyncio.Event()

    @property
    def running(self) -> bool:
        return self._task is not None and not self._task.done()

    async def start(self) -> bool:
        if self.running:
            return False
        self._stop_event = asyncio.Event()
        self._task = asyncio.create_task(self._run())
        return True

    async def stop(self) -> bool:
        if not self.running:
            return False
        self._stop_event.set()
        if self._task:
            await self._task
        self._task = None
        return True

    async def _run(self) -> None:
        await self.analysis_service.generate_for_all_cameras()
        while not self._stop_event.is_set():
            try:
                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=settings.analyzer_interval_seconds,
                )
            except asyncio.TimeoutError:
                await self.analysis_service.generate_for_all_cameras()
