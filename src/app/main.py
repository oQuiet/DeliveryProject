from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import FastAPI
import uvicorn

from app.infrastructure.mongo_client import mongo_client, mongo_database
from app.infrastructure.redis_client import redis_client
from app.infrastructure.repositories.mongodb import PriceDelivery
from app.presentation.routers.parcels import parcelsroute


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

if __name__ == "__main__":
    uvicorn.run(app)
