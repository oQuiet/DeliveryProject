from celery import Task

from app.config import get_settings
from app.infrastructure.celery_app import celery_app, run_async
from app.tasks.dependencies import register_parcel_async, update_currency
from app.utils.logger import logger

settings = get_settings()


@celery_app.task
@logger.catch
def register_parcel_task(session_id: str, parcel_id: str, data: dict) -> None:
    run_async(register_parcel_async(session_id, parcel_id, data))


@celery_app.task(name="currency.update", bind=True, max_retries=3)
@logger.catch
def update_currency_rate(self: Task) -> None:
    try:
        run_async(update_currency())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=15) from exc


# Как работает try except и logger.catch вместе?
