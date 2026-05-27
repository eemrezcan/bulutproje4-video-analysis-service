import asyncio
from typing import Any

from boto3.dynamodb.conditions import Key

from app.core.config import settings
from app.models.schemas import AnalysisEvent
from app.repositories.dynamodb import from_dynamodb, table, to_dynamodb


class AnalysisRepository:
    def __init__(self) -> None:
        self._table = table(settings.analysis_table)

    async def put_event(self, event: AnalysisEvent) -> AnalysisEvent:
        await asyncio.to_thread(
            self._table.put_item, Item=to_dynamodb(event.model_dump())
        )
        return event

    async def list_by_camera(self, camera_id: str, limit: int = 50) -> list[AnalysisEvent]:
        return await asyncio.to_thread(self._list_by_camera_sync, camera_id, limit)

    def _list_by_camera_sync(self, camera_id: str, limit: int) -> list[AnalysisEvent]:
        response = self._table.query(
            KeyConditionExpression=Key("camera_id").eq(camera_id),
            ScanIndexForward=False,
            Limit=limit,
        )
        return self._events_from_items(response.get("Items", []))

    async def list_by_zone(self, zone: str, limit: int = 50) -> list[AnalysisEvent]:
        return await asyncio.to_thread(self._list_by_zone_sync, zone, limit)

    def _list_by_zone_sync(self, zone: str, limit: int) -> list[AnalysisEvent]:
        response = self._table.query(
            IndexName=settings.zone_timestamp_index,
            KeyConditionExpression=Key("zone").eq(zone),
            ScanIndexForward=False,
            Limit=limit,
        )
        return self._events_from_items(response.get("Items", []))

    async def latest_for_cameras(self, camera_ids: list[str]) -> list[AnalysisEvent]:
        results = await asyncio.gather(
            *(self.list_by_camera(camera_id, 1) for camera_id in camera_ids)
        )
        latest = [events[0] for events in results if events]
        return sorted(latest, key=lambda item: item.timestamp, reverse=True)

    def _events_from_items(self, items: list[dict[str, Any]]) -> list[AnalysisEvent]:
        return [AnalysisEvent(**from_dynamodb(item)) for item in items]
