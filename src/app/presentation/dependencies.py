from typing import Annotated
from uuid import uuid4

from fastapi import Cookie, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.delivery_price_service import CalculateDeliveryPriceService
from app.application.get_daily_total import GetDailyDeliveryTotalService
from app.application.parcel_service import ParcelService
from app.application.repositories import LogRepository, ParcelRepository
from app.config import get_settings
from app.infrastructure.database import get_db
from app.infrastructure.external.currency_client import CurrencyClient
from app.infrastructure.redis_client import redis_client
from app.infrastructure.repositories import MongoLogRepository, SQLAlchemyParcelRepository

settings = get_settings()


def get_parcel_repository(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ParcelRepository:
    return SQLAlchemyParcelRepository(session)


def get_log_repository() -> LogRepository:
    return MongoLogRepository()


def get_currency_client() -> CurrencyClient:
    return CurrencyClient(redis_client, settings.CURRENCY_URL)


def create_session_id(response: Response) -> str:
    session_id = str(uuid4())  # Generate a unique session ID
    response.set_cookie(key="session_id", value=session_id, httponly=True, secure=True)
    return session_id


def get_session_id(response: Response, session_id: str | None = Cookie(default=None)) -> str:
    return session_id if session_id else create_session_id(response)


def get_parcel_service(
    repository: Annotated[
        ParcelRepository,
        Depends(get_parcel_repository),
    ],
) -> ParcelService:
    return ParcelService(repository)


def get_calculate_delivery_price_service(
    parcel_repository: Annotated[
        ParcelRepository,
        Depends(get_parcel_repository),
    ],
    log_repository: Annotated[
        LogRepository,
        Depends(get_log_repository),
    ],
    currency_client: Annotated[
        CurrencyClient,
        Depends(get_currency_client),
    ],
) -> CalculateDeliveryPriceService:
    return CalculateDeliveryPriceService(
        parcel_repository,
        log_repository,
        currency_client,
    )


def get_daily_total_service(
    log_repository: Annotated[LogRepository, Depends(get_log_repository)],
) -> GetDailyDeliveryTotalService:
    return GetDailyDeliveryTotalService(log_repository)
