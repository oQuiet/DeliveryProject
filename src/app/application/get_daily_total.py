from decimal import Decimal

from app.application.repositories import LogRepository


class GetDailyDeliveryTotalService:
    def __init__(self, log_repository: LogRepository):
        self.log_repository = log_repository

    async def get(self, type_id: int) -> Decimal:
        return await self.log_repository.get_logs(type_id)
