from decimal import Decimal

from app.application.repositories import LogRepository, ParcelRepository
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

    async def calculate(self) -> int | None:
        usd_rate = await self.currency_client.fetch_currency()
        parcels = await self.repository.set_delivery_prices(usd_rate)

        if not parcels:
            return None

        await self._save(parcels, usd_rate)

        return len(parcels)

    async def _save(self, parcels: list[Parcel], usd_rate: Decimal) -> None:
        await self.log_repository.create_logs(parcels, usd_rate)
