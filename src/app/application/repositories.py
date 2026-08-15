from abc import ABC, abstractmethod
from decimal import Decimal
from uuid import UUID

from app.domain.entities import Parcel
from app.presentation.schemas.parcel_query_params import ParcelQueryParams


class ParcelRepository(ABC):
    @abstractmethod
    async def add(self, session_id: str, parcel: dict) -> Parcel: ...

    @abstractmethod
    async def save(self, parcel_id: UUID, company_id: int) -> Parcel | None: ...

    @abstractmethod
    async def get_by_id(self, parcel_id: UUID) -> Parcel | None: ...

    @abstractmethod
    async def list_by_session(self, session_id: str, params: ParcelQueryParams) -> list[Parcel]: ...


class LogRepository(ABC):
    @abstractmethod
    async def create_logs(self, parcel: Parcel, usd_rate: Decimal) -> None: ...

    @abstractmethod
    async def get_logs(self, type_id: int) -> Decimal | None: ...
