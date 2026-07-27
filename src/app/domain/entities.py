from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Parcel:
    name: str
    weight: Decimal
    parcel_type_id: int
    content_price_usd: Decimal
    session_id: str
    id: int | None = None
    delivery_price_rub: Decimal | None = None
    company_id: int | None = None


@dataclass
class ParcelType:
    name: str
    id: int | None = None
