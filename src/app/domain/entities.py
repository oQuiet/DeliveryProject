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
    delivery_price: Decimal | None = None
    company_id: int | None = None

    def assign_company(self, company_id: int) -> None:
        if company_id <= 0:
            raise ValueError("Id компании должен быть положительным")

        self.company_id = company_id


@dataclass
class ParcelType:
    name: str
    id: int | None = None
