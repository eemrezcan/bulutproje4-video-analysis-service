from typing import Literal

from pydantic import BaseModel, Field


MotionLevel = Literal["low", "medium", "high"]
CrowdLevel = Literal["low", "medium", "high", "critical"]
CameraStatus = Literal["active", "passive", "maintenance"]


class Camera(BaseModel):
    camera_id: str
    zone: str
    name: str
    stream_url: str
    status: CameraStatus
    latitude: float
    longitude: float


class AnalysisEvent(BaseModel):
    camera_id: str
    zone: str
    people_count: int = Field(ge=0)
    vehicle_count: int = Field(ge=0)
    motion_level: MotionLevel
    crowd_level: CrowdLevel
    recognition_labels: list[str]
    timestamp: str


class StreamInfo(BaseModel):
    camera_id: str
    zone: str
    stream_url: str
    media_type: str
    mode: str
    playable: bool
    note: str | None = None


class AnalyzerStatus(BaseModel):
    running: bool
    interval_seconds: float


class HealthResponse(BaseModel):
    service: str
    status: str
    analyzer_running: bool
