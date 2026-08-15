from fastapi import Request
from fastapi.responses import JSONResponse

from app.utils.exceptions import CustomException
from app.utils.logger import logger


async def custom_exception_handler(request: Request, exc: CustomException) -> JSONResponse:
    route = request.scope.get("route")
    route_path = getattr(route, "path", None)
    logger.bind(route=route_path, status_code=exc.status_code, detail=exc.detail).warning(
        f"Возникла ошибка при запросе к {route_path}"
    )
    return JSONResponse(status_code=exc.status_code, content={"Ошибка": exc.detail})


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Возникла неизвестная ошибка {exc}")
    return JSONResponse(status_code=500, content={"Ошибка": "Internal server error"})
