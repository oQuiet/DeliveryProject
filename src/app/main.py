from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn

from app.config import get_settings
from app.infrastructure.mongo_client import mongo_client, mongo_database
from app.infrastructure.redis_client import redis_client
from app.infrastructure.repositories.mongodb import PriceDelivery
from app.presentation.routers.parcels import parcelsroute
from app.utils.exception_handlers import (
    custom_exception_handler,
    global_exception_handler,
    validation_exception_handler,
)
from app.utils.exceptions import CustomException
from app.utils.middleware import request_logging_middleware

setting = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    try:
        await mongo_database.command("ping")
        await init_beanie(database=mongo_database, document_models=[PriceDelivery])

        yield
    finally:
        await mongo_client.close()
        await redis_client.aclose()


app = FastAPI(lifespan=lifespan)

app.include_router(parcelsroute)
app.add_exception_handler(CustomException, custom_exception_handler)  # type: ignore
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
app.add_middleware(BaseHTTPMiddleware, request_logging_middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=setting.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

if __name__ == "__main__":
    uvicorn.run(app)
