from typing import Any

from pymongo import AsyncMongoClient

from app.config import get_settings

MongoDocument = dict[str, Any]

settings = get_settings()

mongo_client: AsyncMongoClient[MongoDocument] = AsyncMongoClient(str(settings.MONGO_URL))
mongo_database = mongo_client[settings.MONGO_DB_NAME]
