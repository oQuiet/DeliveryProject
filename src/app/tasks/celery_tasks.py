from app.config import get_settings
from app.infrastructure.celery_app import celery_app, run_async
from app.tasks.dependencies import register_parcel_async, update_currency

settings = get_settings()


@celery_app.task
def register_parcel_task(id: str, data: dict) -> None:
    run_async(register_parcel_async(id, data))


@celery_app.task(name="currency.update")
def update_currency_rate() -> None:
    run_async(update_currency())
