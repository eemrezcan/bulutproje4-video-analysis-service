from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.core.config import settings
from app.core.lifecycle import startup, shutdown


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup()
    try:
        yield
    finally:
        await shutdown()


app = FastAPI(
    title="Video Analysis Service",
    version="1.0.0",
    description="Smart city camera stream and video analysis simulation service.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/media", StaticFiles(directory=str(settings.media_dir)), name="media")
app.mount(
    "/api/video/media",
    StaticFiles(directory=str(settings.media_dir)),
    name="api-video-media",
)
app.include_router(router)
app.include_router(router, prefix="/api/video")
