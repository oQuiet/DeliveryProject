from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

PositiveDecimal = Annotated[Decimal, Field(gt=0)]


class ParcelRequest(BaseModel):
    name: str = Field(max_length=255, min_length=1)
    weight: PositiveDecimal
    content_price_usd: PositiveDecimal
    parcel_type_id: int = Field(gt=0, lt=4)
    company_id: int | None = Field(default=None, gt=0)


class ParcelResponse(BaseModel):
    id: UUID
    name: str = Field(max_length=255)
    weight: PositiveDecimal
    content_price_usd: PositiveDecimal
    delivery_price: PositiveDecimal | Literal["Не рассчитано"]
    company_id: int | Literal["Транспортная компания не указана"]
    parcel_type_id: Literal["Одежда", "Электроника", "Разное"] = Field(
        serialization_alias="parcel_type"
    )

    @field_validator("delivery_price", mode="before")
    @classmethod
    def format_delivery_price(cls, value: Decimal | None) -> Decimal | str:
        return "Не рассчитано" if value is None else value

    @field_validator("company_id", mode="before")
    @classmethod
    def format_company_id(cls, value: int | None) -> int | str:
        return "Транспортная компания не указана" if value is None else value

    @field_validator("parcel_type_id", mode="before")
    @classmethod
    def format_parcel_type(cls, value: int) -> str:
        return ("0", "Одежда", "Электроника", "Разное")[value]

    model_config = {"from_attributes": True}


class ParcelTypeResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}
