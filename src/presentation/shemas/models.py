from pydantic import BaseModel, Field


class ParcelRequest(BaseModel):
    name: str = Field(..., max_length=255)
    weight: float = Field(..., gt=0)
    content_price_usd: float = Field(..., gt=0)
    parcel_type_id: int = Field(..., gt=0)
    delivery_price_rub: float | None = Field(default=None, gt=0)
    company_id: int | None = Field(default=None, gt=0)


class ParcelResponse(BaseModel):
    pass
