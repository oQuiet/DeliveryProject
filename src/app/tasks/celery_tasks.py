import aiohttp
from celery import Task
from redis import RedisError

from app.config import get_settings
from app.infrastructure.celery_app import celery_app, run_async
from app.tasks.dependencies import register_parcel_async, update_currency
from app.utils.logger import logger

settings = get_settings()


@celery_app.task
def register_parcel_task(session_id: str, parcel_id: str, data: dict) -> None:
    task_logger = logger.bind(task_id=session_id, parcel_id=parcel_id)

    task_logger.info("Начата регистрация посылки")

    try:
        run_async(register_parcel_async(session_id, parcel_id, data))
    except Exception:
        task_logger.exception("Не удалось зарегистрировать посылку")
        raise

    task_logger.info("Посылка зарегистрирована")


@celery_app.task(name="currency.update", bind=True, max_retries=3)
def update_currency_rate(self: Task) -> None:
    try:
        run_async(update_currency())
        logger.info("Курс валюты обновлён")
    except (aiohttp.ClientError, TimeoutError, RedisError) as exc:
        logger.bind(
            task_id=self.request.id,
            attempt=self.request.retries + 1,
        ).warning("Не удалось обновить курс, задача будет повторена")

        raise self.retry(exc=exc, countdown=15) from exc

    except Exception:
        logger.exception("Неожиданная ошибка обновления курса")
        raise
