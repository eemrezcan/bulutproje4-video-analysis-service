from app.core.config import settings
from app.models.schemas import Camera, StreamInfo
from app.repositories.camera_repository import CameraRepository


CAMERA_SEED = [
    {
        "camera_id": "cam_meydan_01",
        "zone": "Meydan",
        "name": "Meydan Ana Kamera",
        "latitude": 39.9208,
        "longitude": 32.8541,
    },
    {
        "camera_id": "cam_otogar_01",
        "zone": "Otogar",
        "name": "Otogar Giris Kamera",
        "latitude": 39.9357,
        "longitude": 32.8261,
    },
    {
        "camera_id": "cam_kampus_01",
        "zone": "Kampus",
        "name": "Kampus Meydan Kamera",
        "latitude": 39.8912,
        "longitude": 32.7849,
    },
    {
        "camera_id": "cam_hastane_01",
        "zone": "Hastane",
        "name": "Hastane Acil Kamera",
        "latitude": 39.9275,
        "longitude": 32.8652,
    },
    {
        "camera_id": "cam_sanayi_01",
        "zone": "Sanayi",
        "name": "Sanayi Bulvari Kamera",
        "latitude": 39.9571,
        "longitude": 32.7854,
    },
]


class CameraService:
    def __init__(self, repository: CameraRepository) -> None:
        self.repository = repository

    async def seed_cameras(self) -> list[Camera]:
        stream_url = f"{settings.public_base_url}/media/{self._stream_path().name}"
        cameras = [
            Camera(
                **seed,
                stream_url=stream_url,
                status="active",
            )
            for seed in CAMERA_SEED
        ]
        await self.repository.upsert_many(cameras)
        return cameras

    async def list_cameras(self) -> list[Camera]:
        return await self.repository.list_cameras()

    async def get_camera(self, camera_id: str) -> Camera | None:
        return await self.repository.get_camera(camera_id)

    async def get_stream(self, camera_id: str, playable: bool) -> StreamInfo | None:
        camera = await self.get_camera(camera_id)
        if not camera:
            return None
        stream_path = self._stream_path()
        return StreamInfo(
            camera_id=camera.camera_id,
            zone=camera.zone,
            stream_url=f"{settings.public_base_url}/media/{stream_path.name}",
            media_type="video/webm" if stream_path.suffix == ".webm" else "video/mp4",
            mode=f"looped_synthetic_{stream_path.suffix.lstrip('.')}",
            playable=playable,
            note=None
            if playable
            else "Synthetic video could not be created; stream metadata is still stable.",
        )

    @staticmethod
    def _stream_path():
        if settings.synthetic_webm_path.exists() and settings.synthetic_webm_path.stat().st_size > 0:
            return settings.synthetic_webm_path
        return settings.synthetic_video_path
