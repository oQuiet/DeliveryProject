from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator

PositivePrice = Annotated[Decimal, Field(gt=0)]


class ParcelResponse(BaseModel):
    name: str = Field(..., max_length=255)
    weight: float = Field(..., gt=0)
    content_price_usd: PositivePrice
    parcel_type_id: int = Field(..., gt=0)
    delivery_price_rub: PositivePrice | Literal["Не рассчитано"]
    company_id: int | None = Field(default=None, gt=0)

    @field_validator("delivery_price_rub", mode="before")
    @classmethod
    def format_delivery_price(
        cls,
        value: Decimal | None,
    ) -> Decimal | str:
        return "Не рассчитано" if value is None else value

    model_config = {"from_attributes": True}


class ParcelRequest(ParcelResponse): ...


class ParcelTypeResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}
