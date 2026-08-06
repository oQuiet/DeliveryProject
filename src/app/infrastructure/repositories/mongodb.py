from datetime import datetime
from decimal import Decimal

from beanie import DecimalAnnotation, Document
from pydantic import BaseModel, Field

from app.application.repositories import LogRepository
from app.domain.entities import Parcel


class PriceDelivery(Document):
    model_config = {"from_attributes": True}

    parcel_id: int
    name: str
    weight: DecimalAnnotation
    content_price_usd: DecimalAnnotation
    delivery_price: DecimalAnnotation
    usd_rate: DecimalAnnotation
    company_id: int | None
    parcel_type_id: int
    calculated_at: datetime = Field(default_factory=datetime.now)


class DeliveryPriceProjection(BaseModel):
    delivery_price: Decimal


class MongoLogRepository(LogRepository):
    async def create_logs(self, parcels: list[Parcel], usd_rate: Decimal) -> None:
        documents = [
            PriceDelivery.model_validate(
                {
                    "parcel_id": parcel.id,
                    "name": parcel.name,
                    "weight": parcel.weight,
                    "content_price_usd": parcel.content_price_usd,
                    "delivery_price": parcel.delivery_price,
                    "usd_rate": usd_rate,
                    "company_id": parcel.company_id,
                    "parcel_type_id": parcel.parcel_type_id,
                }
            )
            for parcel in parcels
        ]

        await PriceDelivery.insert_many(documents)

    async def get_logs(self, type_id: int) -> Decimal:
        result = (
            await PriceDelivery.find(PriceDelivery.parcel_type_id == type_id)
            .project(DeliveryPriceProjection)
            .sum(PriceDelivery.delivery_price)  # type: ignore
        )

        return Decimal(str(result))
