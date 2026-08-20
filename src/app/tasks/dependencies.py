from app.application.delivery_price_service import CalculateDeliveryPriceService
from app.infrastructure.celery_app import get_worker_currency_client
from app.infrastructure.database import async_session_maker
from app.infrastructure.repositories.mongodb import MongoLogRepository
from app.infrastructure.repositories.postgresql import SQLAlchemyParcelRepository
from app.utils.logger import logger


async def register_parcel_async(session_id: str, parcel_id: str, data: dict) -> None:
    async with async_session_maker.begin() as session:
        repository = SQLAlchemyParcelRepository(session)
        log_repository = MongoLogRepository()
        currency_client = get_worker_currency_client()
        service = CalculateDeliveryPriceService(repository, log_repository, currency_client)

        await service.calculate(session_id, parcel_id, data)


async def update_currency() -> None:
    currency_client = get_worker_currency_client()
    logger.bind(beat="Celery_Beat").info("Курс доллара обновлён")

    await currency_client.update_currency()
