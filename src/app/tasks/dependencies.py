from app.application.delivery_price_service import CalculateDeliveryPriceService
from app.infrastructure.database import async_session_maker
from app.infrastructure.repositories.mongodb import MongoLogRepository
from app.infrastructure.repositories.postgresql import SQLAlchemyParcelRepository
from app.presentation.dependencies import get_currency_client
from app.utils.logger import logger


async def register_parcel_async(session_id: str, parcel_id: str, data: dict) -> None:
    async with async_session_maker.begin() as session:
        repository = SQLAlchemyParcelRepository(session)
        log_repository = MongoLogRepository()
        currency_client = get_currency_client()
        service = CalculateDeliveryPriceService(repository, log_repository, currency_client)

        await service.calculate(session_id, parcel_id, data)


async def update_currency() -> None:
    currency_client = get_currency_client()
    print("GET CURRENCY RATE")
    logger.info("GET CURRENCY RATE")

    await currency_client.update_currency()
