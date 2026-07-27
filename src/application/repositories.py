from abc import ABC, abstractmethod

from src.domain.entities import Parcel


class ParcelRepository(ABC):
    @abstractmethod
    async def add(self, parcel: Parcel) -> Parcel: ...

    @abstractmethod
    async def get_by_id(self, parcel_id: int) -> Parcel | None: ...

    @abstractmethod
    async def list_by_session(self, session_id: str) -> list[Parcel]: ...
