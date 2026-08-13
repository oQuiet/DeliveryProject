from decimal import Decimal

from app.application.repositories import LogRepository, ParcelRepository
from app.domain.delivery_price import calculate_delivery_price
from app.domain.entities import Parcel
from app.infrastructure.external.currency_client import CurrencyClient


class CalculateDeliveryPriceService:
    def __init__(
        self,
        repository: ParcelRepository,
        log_repository: LogRepository,
        currency_client: CurrencyClient,
    ) -> None:
        self.repository = repository
        self.log_repository = log_repository
        self.currency_client = currency_client

    async def calculate(self, session_id: str, parcel: dict) -> None:
        usd_rate = await self.currency_client.fetch_currency()
        parcel["delivery_price"] = calculate_delivery_price(
            parcel["weight"], parcel["content_price_usd"], usd_rate
        )
        result = await self.repository.add(session_id, parcel)
        await self._save(result, usd_rate)

    async def _save(self, parcel: Parcel, usd_rate: Decimal) -> None:
        await self.log_repository.create_logs(parcel, usd_rate)
