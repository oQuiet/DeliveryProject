from typing import Literal

from pydantic import BaseModel, Field


class ParcelPagination(BaseModel):
    limit: int = Field(default=5, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class ParcelFilters(BaseModel):
    parcel_type: tuple[Literal["Одежда", "Электроника", "Разное"], ...] | None = None


class ParcelQueryParams(ParcelFilters, ParcelPagination):
    pass
