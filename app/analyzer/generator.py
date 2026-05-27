import random
from datetime import UTC, datetime

import cv2

from app.core.config import settings
from app.models.schemas import AnalysisEvent, Camera, CrowdLevel, MotionLevel


ZONE_PROFILES = {
    "Meydan": {"people": (95, 185), "vehicles": (20, 55), "labels": ["crowd", "public-square"]},
    "Otogar": {"people": (55, 135), "vehicles": (45, 105), "labels": ["traffic", "bus", "vehicle"]},
    "Kampus": {"people": (35, 115), "vehicles": (8, 35), "labels": ["pedestrian", "campus"]},
    "Hastane": {"people": (25, 95), "vehicles": (18, 65), "labels": ["emergency", "vehicle"]},
    "Sanayi": {"people": (20, 75), "vehicles": (35, 95), "labels": ["vehicle", "industrial"]},
}


def crowd_level(people_count: int, vehicle_count: int) -> CrowdLevel:
    if people_count >= 160 or vehicle_count >= 90:
        return "critical"
    if people_count >= 100 or vehicle_count >= 60:
        return "high"
    if people_count >= 50 or vehicle_count >= 30:
        return "medium"
    return "low"


def motion_level(vehicle_count: int, frame_motion_score: float) -> MotionLevel:
    score = vehicle_count + frame_motion_score
    if score >= 95:
        return "high"
    if score >= 45:
        return "medium"
    return "low"


def generate_event(camera: Camera) -> AnalysisEvent:
    profile = ZONE_PROFILES.get(
        camera.zone,
        {"people": (20, 90), "vehicles": (10, 50), "labels": ["normal"]},
    )
    people_count = random.randint(*profile["people"])
    vehicle_count = random.randint(*profile["vehicles"])
    frame_motion_score = _read_motion_score()
    crowd = crowd_level(people_count, vehicle_count)
    motion = motion_level(vehicle_count, frame_motion_score)
    labels = _labels_for(profile["labels"], crowd, motion, vehicle_count)

    return AnalysisEvent(
        camera_id=camera.camera_id,
        zone=camera.zone,
        people_count=people_count,
        vehicle_count=vehicle_count,
        motion_level=motion,
        crowd_level=crowd,
        recognition_labels=labels,
        timestamp=datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    )


def _read_motion_score() -> float:
    if not settings.synthetic_video_path.exists():
        return random.uniform(0, 35)

    capture = cv2.VideoCapture(str(settings.synthetic_video_path))
    try:
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
        first_index = random.randint(0, max(frame_count - 2, 0))
        capture.set(cv2.CAP_PROP_POS_FRAMES, first_index)
        ok_first, first = capture.read()
        ok_second, second = capture.read()
        if not ok_first or not ok_second:
            return random.uniform(0, 35)

        first_gray = cv2.cvtColor(first, cv2.COLOR_BGR2GRAY)
        second_gray = cv2.cvtColor(second, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(first_gray, second_gray)
        return min(float(diff.mean()) * 4, 45)
    finally:
        capture.release()


def _labels_for(
    base_labels: list[str],
    crowd: CrowdLevel,
    motion: MotionLevel,
    vehicle_count: int,
) -> list[str]:
    labels = set(base_labels)
    if crowd in {"high", "critical"}:
        labels.add("crowd")
    if vehicle_count >= 30:
        labels.add("traffic")
        labels.add("vehicle")
    if motion == "high":
        labels.add("motion")
    if crowd == "critical":
        labels.add("incident")
    if not labels:
        labels.add("normal")
    return sorted(labels)
