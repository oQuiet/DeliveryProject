from abc import ABC, abstractmethod
from decimal import Decimal

from app.domain.entities import Parcel
from app.presentation.schemas.parcel_query_params import ParcelQueryParams


class ParcelRepository(ABC):
    @abstractmethod
    async def add(self, parcel: Parcel) -> Parcel: ...

    @abstractmethod
    async def get_by_id(self, parcel_id: int) -> Parcel | None: ...

    @abstractmethod
    async def list_by_session(self, session_id: str, params: ParcelQueryParams) -> list[Parcel]: ...

    @abstractmethod
    async def list_unprocessed(self) -> list[Parcel]: ...

    @abstractmethod
    async def list_processed(self) -> list[Parcel]: ...

    @abstractmethod
    async def set_delivery_prices(self, usd_rate: Decimal) -> int | None: ...
