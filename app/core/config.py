import os
from pathlib import Path


class Settings:
    service_name: str = os.getenv("SERVICE_NAME", "video-analysis-service")
    aws_region: str = os.getenv("AWS_REGION", "eu-central-1")
    dynamodb_endpoint_url: str | None = os.getenv("DYNAMODB_ENDPOINT_URL")
    cameras_table: str = os.getenv("VIDEO_CAMERAS_TABLE", "video_cameras")
    analysis_table: str = os.getenv(
        "VIDEO_ANALYSIS_TABLE", "video_analysis_results"
    )
    zone_timestamp_index: str = os.getenv(
        "VIDEO_ZONE_TIMESTAMP_INDEX", "zone-timestamp-index"
    )
    public_base_url: str = os.getenv("PUBLIC_BASE_URL", "http://localhost:8002")
    analyzer_interval_seconds: float = float(
        os.getenv("ANALYZER_INTERVAL_SECONDS", "5")
    )
    dynamodb_ready_timeout_seconds: int = int(
        os.getenv("DYNAMODB_READY_TIMEOUT_SECONDS", "60")
    )
    app_dir: Path = Path(__file__).resolve().parents[1]
    media_dir: Path = app_dir / "media"
    synthetic_video_path: Path = media_dir / "synthetic_city_loop.mp4"
    cors_origins: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    ]


settings = Settings()
