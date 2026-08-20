import asyncio
from collections.abc import Coroutine
from typing import Any

import aiohttp
from beanie import init_beanie
from celery import Celery
from celery.signals import worker_process_init, worker_process_shutdown

from app.config import get_settings
from app.infrastructure.external.currency_client import CurrencyClient
from app.infrastructure.mongo_client import mongo_client, mongo_database
from app.infrastructure.redis_client import redis_client
from app.infrastructure.repositories.mongodb import PriceDelivery

setting = get_settings()
celery_app = Celery(
    "my_app",
    broker=str(setting.RABBIT_URL),
    backend=str(setting.REDIS_URL),
    include=["app.tasks.celery_tasks"],
)

_loop: asyncio.AbstractEventLoop | None = None
_http_session: aiohttp.ClientSession | None = None
_currency_client: CurrencyClient | None = None


async def _init_worker_resources() -> None:  # Инициализация всех зависиимостей в одной корутине
    global _http_session, _currency_client

    await init_beanie(
        database=mongo_database,
        document_models=[PriceDelivery],
    )

    _http_session = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=10),
    )

    _currency_client = CurrencyClient(
        redis=redis_client,
        url=setting.CURRENCY_URL,
        http_session=_http_session,
    )


async def _close_worker_resources() -> None:
    global _http_session, _currency_client

    if _http_session is not None:
        await _http_session.close()

    await redis_client.aclose()
    await mongo_client.close()

    _http_session = None
    _currency_client = None


@worker_process_init.connect
def init_worker(**_: object) -> None:
    global _loop

    _loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_loop)

    _loop.run_until_complete(_init_worker_resources())


@worker_process_shutdown.connect
def shutdown_worker(**_: object) -> None:
    global _loop

    if _loop is None:
        return

    try:
        _loop.run_until_complete(_close_worker_resources())
    finally:
        _loop.close()
        _loop = None


def get_worker_currency_client() -> CurrencyClient:
    if _currency_client is None:
        raise RuntimeError("Валютный клиент не инициализирован")

    return _currency_client


def run_async(coro: Coroutine[Any, Any, Any]) -> Any:
    if _loop is None:
        coro.close()
        raise RuntimeError("Celery worker не инициализирован")

    return _loop.run_until_complete(coro)


celery_app.conf.beat_schedule = {
    "update_currency_rate": {
        "task": "currency.update",
        "schedule": 3600,
    },
}
