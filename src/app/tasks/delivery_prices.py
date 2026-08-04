import asyncio

import aiohttp
from redis.exceptions import RedisError

from app.application.delivery_price_service import CalculateDeliveryPriceService
from app.config import get_settings
from app.infrastructure.database import async_session_maker
from app.infrastructure.external.currency_client import CurrencyClient
from app.infrastructure.mongo_client import mongo_client
from app.infrastructure.redis_client import redis_client
from app.infrastructure.repositories import MongoLogRepository, SQLAlchemyParcelRepository


async def calculate_delivery_prices_once() -> int | None:
    settings = get_settings()

    async with async_session_maker() as session:
        repository = SQLAlchemyParcelRepository(session)
        log_repository = MongoLogRepository(mongo_client)
        currency_client = CurrencyClient(redis_client, settings.CURRENCY_URL)

        service = CalculateDeliveryPriceService(repository, log_repository, currency_client)

        return await service.calculate()


async def delivery_price_worker() -> None:
    INTERVAL = 300

    while True:
        await asyncio.sleep(INTERVAL)
        try:
            await calculate_delivery_prices_once()
        except asyncio.CancelledError:
            print("Задача отменилась")
            raise
        except Exception as e:
            print("Ошибка расчета стоимости доставки", e)


async def cache_currency_worker() -> None:
    INTERVAL = 3600
    settings = get_settings()
    currency_client = CurrencyClient(redis_client, settings.CURRENCY_URL)

    while True:
        try:
            await currency_client.update_currency()
        except (TimeoutError, aiohttp.ClientError) as e:
            print("Проблемы с клиентом aiohttp или сервером: ", e)
        except RedisError:
            print("Ошибка связана с Redis")
        except Exception as e:
            print("Прочие ошибки", e)
        await asyncio.sleep(INTERVAL)
