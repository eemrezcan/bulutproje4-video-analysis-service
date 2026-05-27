from app.analyzer.generator import generate_event
from app.models.schemas import AnalysisEvent
from app.repositories.analysis_repository import AnalysisRepository
from app.services.camera_service import CameraService


class AnalysisService:
    def __init__(
        self,
        repository: AnalysisRepository,
        camera_service: CameraService,
    ) -> None:
        self.repository = repository
        self.camera_service = camera_service

    async def generate_for_all_cameras(self) -> list[AnalysisEvent]:
        cameras = await self.camera_service.list_cameras()
        events = [generate_event(camera) for camera in cameras]
        for event in events:
            await self.repository.put_event(event)
        return events

    async def list_by_camera(self, camera_id: str, limit: int) -> list[AnalysisEvent]:
        return await self.repository.list_by_camera(camera_id, limit)

    async def list_by_zone(self, zone: str, limit: int) -> list[AnalysisEvent]:
        return await self.repository.list_by_zone(zone, limit)

    async def latest(self) -> list[AnalysisEvent]:
        cameras = await self.camera_service.list_cameras()
        return await self.repository.latest_for_cameras(
            [camera.camera_id for camera in cameras]
        )
