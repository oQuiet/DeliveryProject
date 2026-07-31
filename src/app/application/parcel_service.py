from app.application.repositories import ParcelRepository
from app.domain.entities import Parcel
from app.presentation.schemas.parcel_query_params import ParcelQueryParams


class ParcelService:
    def __init__(self, repository: ParcelRepository) -> None:
        self.repository = repository

    async def register(self, parcel: Parcel) -> Parcel:
        # Здесь проверки и бизнес-правила.
        return await self.repository.add(parcel)

    async def get_all(self, session_id: str, params: ParcelQueryParams) -> list[Parcel]:
        return await self.repository.list_by_session(session_id, params)

    async def get_one(self, parcel_id: int) -> Parcel | None:
        return await self.repository.get_by_id(parcel_id)
