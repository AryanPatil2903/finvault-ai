"""
FastAPI middleware: CORS, request logging, rate limiting, timing headers.
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from config.logging_config import get_logger
from config.settings import settings

logger = get_logger("middleware")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Log every request with method, path, status code, and response time.
    Attaches a unique request_id header for traceability.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique ID per request
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception as exc:
            logger.error(
                "[%s] UNHANDLED EXCEPTION %s %s — %s",
                request_id, request.method, request.url.path, exc,
                exc_info=True,
            )
            raise

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Attach timing + trace headers to every response
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{elapsed_ms}ms"

        logger.info(
            "[%s] %s %s → %d (%sms)",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )

        return response


def setup_cors(app) -> None:
    """Attach CORS middleware with configured allowed origins."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Response-Time"],
    )