from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

from beanie import DecimalAnnotation, Document
from pydantic import BaseModel, Field

from app.application.repositories import LogRepository
from app.domain.entities import Parcel


class PriceDelivery(Document):
    model_config = {"from_attributes": True}

    parcel_id: UUID
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
    async def create_logs(self, parcel: Parcel, usd_rate: Decimal) -> None:
        document = PriceDelivery.model_validate(
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

        await PriceDelivery.insert(document)

    async def get_logs(self, type_id: int) -> Decimal:
        three_days_ago = datetime.now() - timedelta(days=3)
        result = (
            await PriceDelivery.find(
                PriceDelivery.parcel_type_id == type_id,
                PriceDelivery.calculated_at >= three_days_ago,
            )
            .project(DeliveryPriceProjection)
            .sum(PriceDelivery.delivery_price)  # type: ignore
        )

        return Decimal(str(result))
