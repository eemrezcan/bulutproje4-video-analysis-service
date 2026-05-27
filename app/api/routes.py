from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.core import lifecycle
from app.core.config import settings
from app.models.schemas import (
    AnalysisEvent,
    AnalyzerStatus,
    Camera,
    HealthResponse,
    StreamInfo,
)

router = APIRouter()
Limit = Annotated[int, Query(ge=1, le=200)]


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        service=settings.service_name,
        status="ok",
        analyzer_running=lifecycle.analyzer_worker.running,
    )


@router.get("/cameras", response_model=list[Camera])
async def list_cameras() -> list[Camera]:
    return await lifecycle.camera_service.list_cameras()


@router.get("/cameras/{camera_id}", response_model=Camera)
async def get_camera(camera_id: str) -> Camera:
    camera = await lifecycle.camera_service.get_camera(camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


@router.get("/cameras/{camera_id}/stream", response_model=StreamInfo)
async def get_camera_stream(camera_id: str) -> StreamInfo:
    stream = await lifecycle.camera_service.get_stream(
        camera_id,
        playable=lifecycle.synthetic_video_ready,
    )
    if not stream:
        raise HTTPException(status_code=404, detail="Camera not found")
    return stream


@router.get("/analysis/latest", response_model=list[AnalysisEvent])
async def latest_analysis() -> list[AnalysisEvent]:
    return await lifecycle.analysis_service.latest()


@router.get("/analysis", response_model=list[AnalysisEvent])
async def analysis_by_camera(camera_id: str, limit: Limit = 50) -> list[AnalysisEvent]:
    camera = await lifecycle.camera_service.get_camera(camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return await lifecycle.analysis_service.list_by_camera(camera_id, limit)


@router.get("/zones/{zone}/analysis", response_model=list[AnalysisEvent])
async def analysis_by_zone(zone: str, limit: Limit = 50) -> list[AnalysisEvent]:
    return await lifecycle.analysis_service.list_by_zone(zone, limit)


@router.post("/analysis/generate", response_model=list[AnalysisEvent])
async def generate_analysis() -> list[AnalysisEvent]:
    return await lifecycle.analysis_service.generate_for_all_cameras()


@router.post("/analyzer/start", response_model=AnalyzerStatus)
async def start_analyzer() -> AnalyzerStatus:
    await lifecycle.analyzer_worker.start()
    return AnalyzerStatus(
        running=lifecycle.analyzer_worker.running,
        interval_seconds=settings.analyzer_interval_seconds,
    )


@router.post("/analyzer/stop", response_model=AnalyzerStatus)
async def stop_analyzer() -> AnalyzerStatus:
    await lifecycle.analyzer_worker.stop()
    return AnalyzerStatus(
        running=lifecycle.analyzer_worker.running,
        interval_seconds=settings.analyzer_interval_seconds,
    )
