from collections.abc import Awaitable, Callable
import time
import uuid

from fastapi import Request
from starlette.responses import Response

from app.utils.logger import logger


async def request_logging_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    started_at = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        logger.bind(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        ).exception("HTTP request failed")
        raise

    duration_ms = (time.perf_counter() - started_at) * 1000

    logger.bind(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round(duration_ms, 2),
    ).info("HTTP request completed")

    response.headers["X-Request-ID"] = request_id
    return response
