from abc import ABC, abstractmethod
from decimal import Decimal

from app.domain.entities import Parcel
from app.presentation.schemas.parcel_query_params import ParcelQueryParams


class ParcelRepository(ABC):
    @abstractmethod
    async def add(self, parcel: Parcel) -> Parcel: ...

    @abstractmethod
    async def save(self, parcel_id: int, company_id: int) -> Parcel | None: ...

    @abstractmethod
    async def get_by_id(self, parcel_id: int) -> Parcel | None: ...

    @abstractmethod
    async def list_by_session(self, session_id: str, params: ParcelQueryParams) -> list[Parcel]: ...

    @abstractmethod
    async def set_delivery_prices(self, usd_rate: Decimal) -> list[Parcel]: ...


class LogRepository(ABC):
    @abstractmethod
    async def create_logs(self, parcels: list[Parcel], usd_rate: Decimal) -> None: ...

    @abstractmethod
    async def get_logs(self, type_id: int) -> Decimal: ...
