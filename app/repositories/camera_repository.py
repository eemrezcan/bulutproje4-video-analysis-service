import asyncio

from botocore.exceptions import ClientError

from app.core.config import settings
from app.models.schemas import Camera
from app.repositories.dynamodb import from_dynamodb, table, to_dynamodb


class CameraRepository:
    def __init__(self) -> None:
        self._table = table(settings.cameras_table)

    async def upsert_many(self, cameras: list[Camera]) -> None:
        await asyncio.to_thread(self._upsert_many_sync, cameras)

    def _upsert_many_sync(self, cameras: list[Camera]) -> None:
        with self._table.batch_writer() as batch:
            for camera in cameras:
                batch.put_item(Item=to_dynamodb(camera.model_dump()))

    async def list_cameras(self) -> list[Camera]:
        return await asyncio.to_thread(self._list_cameras_sync)

    def _list_cameras_sync(self) -> list[Camera]:
        response = self._table.scan()
        items = [from_dynamodb(item) for item in response.get("Items", [])]
        while "LastEvaluatedKey" in response:
            response = self._table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            items.extend(from_dynamodb(item) for item in response.get("Items", []))
        return sorted((Camera(**item) for item in items), key=lambda item: item.zone)

    async def get_camera(self, camera_id: str) -> Camera | None:
        return await asyncio.to_thread(self._get_camera_sync, camera_id)

    def _get_camera_sync(self, camera_id: str) -> Camera | None:
        try:
            response = self._table.get_item(Key={"camera_id": camera_id})
        except ClientError:
            return None
        item = response.get("Item")
        return Camera(**from_dynamodb(item)) if item else None
