"""
FastAPI application factory with lifespan management.
This is the entry point for the ASGI server (uvicorn).
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from api.middleware import RequestLoggingMiddleware, setup_cors
from api.routes import ai_chat, auth, budgets, dashboard, expenses, incomes, loans
from config.logging_config import get_logger, setup_logging
from config.settings import settings
from database.connection import dispose_db, init_db

setup_logging()
logger = get_logger("app")


# -- Lifespan: startup + shutdown ---------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and graceful shutdown."""
    logger.info("FinVault AI starting up... (env: %s)", settings.ENVIRONMENT)
    await init_db()
    logger.info("Database tables ready.")
    yield
    logger.info("FinVault AI shutting down...")
    await dispose_db()
    logger.info("Database connections closed.")


# -- Application factory ------------------------------------------------------
def create_app() -> FastAPI:
    """Build and configure the FastAPI application instance."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI-powered personal finance & EMI management platform.",
        docs_url="/docs" if settings.DEBUG else None,     # Disable docs in prod
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # -- Middleware --
    setup_cors(app)
    app.add_middleware(RequestLoggingMiddleware)

    # -- Routers --
    api_prefix = "/api/v1"
    app.include_router(auth.router, prefix=api_prefix)
    app.include_router(expenses.router, prefix=api_prefix)
    app.include_router(incomes.router, prefix=api_prefix)
    app.include_router(budgets.router, prefix=api_prefix)
    app.include_router(loans.router, prefix=api_prefix)
    app.include_router(dashboard.router, prefix=api_prefix)
    app.include_router(ai_chat.router, prefix=api_prefix)

    # -- Health check --
    @app.get("/health", tags=["System"])
    async def health_check() -> JSONResponse:
        """Simple liveness probe."""
        return JSONResponse({"status": "ok", "version": settings.APP_VERSION})

    logger.info("All routers registered.")
    return app


# -- ASGI entry point ---------------------------------------------------------
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )