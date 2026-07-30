from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator

PositiveDecimal = Annotated[Decimal, Field(gt=0)]


class ParcelBase(BaseModel):
    name: str = Field(max_length=255)
    weight: PositiveDecimal
    content_price_usd: PositiveDecimal
    parcel_type_id: int = Field(gt=0)


class ParcelRequest(ParcelBase):
    pass


class ParcelResponse(ParcelBase):
    delivery_price_rub: PositiveDecimal | Literal["Не рассчитано"]
    company_id: int | None = None

    @field_validator("delivery_price_rub", mode="before")
    @classmethod
    def format_delivery_price(
        cls,
        value: Decimal | None,
    ) -> Decimal | str:
        return "Не рассчитано" if value is None else value

    model_config = {"from_attributes": True}


class ParcelTypeResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}
