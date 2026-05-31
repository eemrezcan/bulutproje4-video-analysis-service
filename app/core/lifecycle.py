from app.analyzer.worker import AnalyzerWorker
from app.core.config import settings
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.camera_repository import CameraRepository
from app.repositories.dynamodb import create_tables, wait_until_ready
from app.services.analysis_service import AnalysisService
from app.services.camera_service import CameraService

camera_repository = CameraRepository()
camera_service = CameraService(camera_repository)
analysis_repository = AnalysisRepository()
analysis_service = AnalysisService(analysis_repository, camera_service)
analyzer_worker = AnalyzerWorker(camera_service, analysis_service)

synthetic_video_ready = False


async def startup() -> None:
    global synthetic_video_ready
    await wait_until_ready()
    await create_tables()
    synthetic_video_ready = await camera_service.ensure_stream_media()
    await camera_service.seed_cameras()
    if settings.analyzer_autostart:
        await analyzer_worker.start()


async def shutdown() -> None:
    await analyzer_worker.stop()
