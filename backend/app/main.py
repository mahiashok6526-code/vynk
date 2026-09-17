import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db, dispose_db
from app.api.v1.api import api_router

# Configure production-safe standard logging
logging.basicConfig(
    level=logging.INFO if settings.ENV == "production" else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("vynk")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENV}]")
    await init_db()
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}...")
    await dispose_db()
    logger.info("Database connections disposed successfully.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Vynk — Ideas Meet Opportunities. Professional networking and sponsorship platform API.",
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.ENV != "production" or settings.DEBUG else None,
    docs_url=f"{settings.API_V1_STR}/docs" if settings.ENV != "production" or settings.DEBUG else None,
    redoc_url=f"{settings.API_V1_STR}/redoc" if settings.ENV != "production" or settings.DEBUG else None,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Inject security headers into all responses."""
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # Only set HSTS when request is over HTTPS or forwarded as HTTPS
    is_https = request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https"
    if is_https and settings.ENV == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Production-safe fallback exception handler."""
    logger.exception(f"Unhandled error processing request: {request.method} {request.url.path}")

    if settings.ENV == "production":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An unexpected internal server error occurred. Please try again later.",
            },
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected internal server error occurred.",
            "type": type(exc).__name__,
        },
    )


# Mount v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
async def root():
    return {
        "app": "Vynk",
        "tagline": "Ideas Meet Opportunities",
        "version": settings.VERSION,
        "environment": settings.ENV,
        "docs": f"{settings.API_V1_STR}/docs" if settings.ENV != "production" or settings.DEBUG else "Disabled in production",
        "health": f"{settings.API_V1_STR}/health",
        "workflow": "Discover -> AI Match -> Connect -> Commit -> Track -> Complete -> Build Trust"
    }
