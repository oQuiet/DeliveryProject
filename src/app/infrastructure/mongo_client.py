from typing import Any

from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
)

from app.config import get_settings

MongoDocument = dict[str, Any]

settings = get_settings()

mongo_client: AsyncIOMotorClient[MongoDocument] = AsyncIOMotorClient(str(settings.MONGO_URL))
mongo_database: AsyncIOMotorDatabase[MongoDocument] = mongo_client[settings.MONGO_DB_NAME]


def get_mongo_db() -> AsyncIOMotorDatabase[MongoDocument]:
    return mongo_database
