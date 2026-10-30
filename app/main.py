"""Main FastAPI Application Entrypoint for KathaYantra."""

from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes import (
    ai_router,
    countries_router,
    dataset_router,
    export_router,
    folklore_router,
    health_router,
    search_router,
    sources_router,
    stories_router,
    urban_legends_router,
)
from app.core.config import settings
from app.repositories.story_repository import story_repository

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("kathayantra")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context for startup and shutdown tasks."""
    logger.info("Initializing %s v%s", settings.PROJECT_NAME, settings.PROJECT_VERSION)
    logger.info("Host: %s:%s | Debug: %s", settings.HOST, settings.PORT, settings.DEBUG)
    logger.info("Configured Ollama Endpoint: %s (Model: %s)", settings.OLLAMA_BASE_URL, settings.OLLAMA_MODEL)
    logger.info("Data Directory: %s", settings.DATA_DIR)

    # Pre-cache canonical dataset into memory repository
    story_repository.load()

    yield
    logger.info("Shutting down %s", settings.PROJECT_NAME)


def create_app() -> FastAPI:
    """Factory creating and configuring the FastAPI application."""
    app = FastAPI(
        title=f"{settings.PROJECT_NAME} — A Haunted Atlas of World Folklore",
        version=settings.PROJECT_VERSION,
        description=(
            "Local-first, rights-aware digital archive of folklore, ghost stories, "
            "and urban legends from 15 countries, powered by local open-weight AI (Gemma 2)."
        ),
        lifespan=lifespan,
    )

    # Restrict CORS to explicitly configured development origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    # Security Headers Middleware
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    # Custom Exception Handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error_code": "VALIDATION_ERROR",
                "message": "The request contains invalid parameters or malformed payload.",
                "detail": jsonable_encoder(exc.errors()),
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        if isinstance(exc.detail, dict) and "error_code" in exc.detail:
            content = exc.detail
        else:
            content = {
                "error_code": f"HTTP_{exc.status_code}",
                "message": str(exc.detail),
                "detail": None,
            }
        return JSONResponse(status_code=exc.status_code, content=content)

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled exception processing %s %s: %s", request.method, request.url.path, str(exc))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please consult backend logs.",
                "detail": None,
            },
        )

    # Root redirect / status
    @app.get("/", tags=["System"])
    async def root():
        return {
            "project": settings.PROJECT_NAME,
            "version": settings.PROJECT_VERSION,
            "tagline": "Preserve the story. Trace the source. Respect the culture. Keep the AI honest.",
            "health_endpoint": f"{settings.API_V1_PREFIX}/health",
            "documentation": "/docs",
        }

    # Register Routers
    app.include_router(health_router, prefix=settings.API_V1_PREFIX)
    app.include_router(countries_router, prefix=settings.API_V1_PREFIX)
    app.include_router(folklore_router, prefix=settings.API_V1_PREFIX)
    app.include_router(urban_legends_router, prefix=settings.API_V1_PREFIX)
    app.include_router(stories_router, prefix=settings.API_V1_PREFIX)
    app.include_router(search_router, prefix=settings.API_V1_PREFIX)
    app.include_router(sources_router, prefix=settings.API_V1_PREFIX)
    app.include_router(dataset_router, prefix=settings.API_V1_PREFIX)
    app.include_router(export_router, prefix=settings.API_V1_PREFIX)
    app.include_router(ai_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
