from app.application.repositories import ParcelRepository
from app.infrastructure.external.currency_client import CurrencyClient


class CalculateDeliveryPriceService:
    def __init__(self, repository: ParcelRepository, currency_client: CurrencyClient) -> None:
        self.repository = repository
        self.currency_client = currency_client

    async def execute(self) -> int | None:
        usd_rate = await self.currency_client.fetch_currency()

        return await self.repository.set_delivery_prices(usd_rate)
