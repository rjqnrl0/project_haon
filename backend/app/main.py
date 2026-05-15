import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.background import router as background_router
from app.api.face import router as face_router
from app.api.fitting import router as fitting_router
from app.api.health import router as health_router
from app.api.recommend import router as recommend_router
from app.api.share import router as share_router
from app.core.config import get_settings
from app.core.errors import AppError, app_error_handler
from app.core.middleware import RequestLoggingMiddleware
from app.core.scheduler import periodic_cleanup
from app.services.file_manager import FileManagerService

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

settings = get_settings()

app = FastAPI(title="V-Suitcase API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

app.add_exception_handler(AppError, app_error_handler)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(face_router)
app.include_router(fitting_router)
app.include_router(background_router)
app.include_router(recommend_router)
app.include_router(share_router)


@app.on_event("startup")
async def startup():
    async def cleanup():
        pass  # Will be implemented with DB session in unit-fitting

    asyncio.create_task(periodic_cleanup(cleanup, interval_seconds=600))
