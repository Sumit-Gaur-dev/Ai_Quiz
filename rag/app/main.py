"""AI Quiz Platform — RAG Service Entrypoint."""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.api.health import router as health_router
from app.api.ingestion import router as ingestion_router
from app.api.internal import router as internal_router
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle handler."""
    setup_logging(log_level=settings.log_level)
    logger.info(
        "Starting RAG service on port %s in %s environment",
        settings.port,
        settings.app_env,
    )
    logger.info(
        "Configured embedding provider: %s, model: %s, dimensions: %s",
        settings.embedding_provider,
        settings.embedding_model,
        settings.embedding_dimensions,
    )
    yield
    logger.info("Shutting down RAG service")


app = FastAPI(
    title="AI Quiz Platform — RAG Service",
    description="Private AI service for ingestion, embeddings, quiz generation, and evaluation.",
    version="0.2.0",
    lifespan=lifespan,
)


# Request timing and structured access logging middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

    # Do not log query params or bodies that may contain sensitive data
    logger.info(
        "%s %s -> %s (%sms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


# Centralized exception handlers matching API contract
@app.exception_handler(AppException)
async def app_exception_handler(_request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                **({"details": exc.details} if exc.details else {}),
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    errors = [
        {"field": ".".join(str(loc) for loc in err.get("loc", [])), "message": err.get("msg")}
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request parameters",
                "details": errors,
            }
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(_request: Request, exc: Exception):
    logger.error("Unhandled server exception: %s", str(exc), exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected server error occurred",
            }
        },
    )


# Mount routers
app.include_router(health_router)
app.include_router(internal_router)
app.include_router(ingestion_router)
