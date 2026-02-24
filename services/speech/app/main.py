"""DRAVIS Speech Microservice - Application Entry Point"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .config import settings
from .routes import router

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(name)-20s | %(levelname)-7s | %(message)s",
)
logger = logging.getLogger(settings.SERVICE_NAME)


@asynccontextmanager
async def lifespan(application: FastAPI):
    logger.info(f"Starting {settings.SERVICE_NAME} service on port {settings.SERVICE_PORT}")
    yield
    logger.info(f"Shutting down {settings.SERVICE_NAME} service")


app = FastAPI(title="DRAVIS Speech Service", version="1.0.0", lifespan=lifespan)
app.include_router(router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {exc}")
    return JSONResponse(status_code=500, content={"error": "Internal server error", "detail": str(exc)})
