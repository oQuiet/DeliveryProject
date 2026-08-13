import asyncio

from beanie import init_beanie
from celery import Celery
from celery.signals import worker_process_init

from app.config import get_settings
from app.infrastructure.mongo_client import mongo_database
from app.infrastructure.repositories.mongodb import PriceDelivery

setting = get_settings()
celery_app = Celery(
    "my_app",
    broker=str(setting.RABBIT_URL),
    backend=str(setting.REDIS_URL),
    include=["app.tasks.celery_tasks"],
)

_loop: asyncio.AbstractEventLoop | None = None


@worker_process_init.connect
def _init_loop(**_):
    global _loop
    _loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_loop)

    _loop.run_until_complete(init_beanie(database=mongo_database, document_models=[PriceDelivery]))


def run_async(coro):
    global _loop
    if _loop is None:
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)
    return _loop.run_until_complete(coro)


celery_app.conf.beat_schedule = {
    "update_currency_rate": {
        "task": "currency.update",
        "schedule": 3600,
    },
}
