"""Fill parcel_types and parcels with test data

Revision ID: 9b8d3d4a1c01
Revises: 6c43264be7f5
Create Date: 2026-07-24 11:10:00

"""

from typing import Sequence, Union
from decimal import Decimal
from datetime import datetime, timedelta
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9b8d3d4a1c01"
down_revision: Union[str, Sequence[str], None] = "6c43264be7f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


parcel_types = sa.table(
    "parcel_types",
    sa.column("id", sa.Integer),
    sa.column("name", sa.String),
)

parcels = sa.table(
    "parcels",
    sa.column("session_id", sa.String),
    sa.column("name", sa.String),
    sa.column("weight", sa.Numeric),
    sa.column("content_price_usd", sa.Numeric),
    sa.column("parcel_type_id", sa.Integer),
    sa.column("delivery_price_rub", sa.Numeric),
    sa.column("company_id", sa.Integer),
    sa.column("created_at", sa.DateTime),
    sa.column("updated_at", sa.DateTime),
)


def upgrade() -> None:
    op.bulk_insert(
        parcel_types,
        [
            {"id": 1, "name": "Одежда"},
            {"id": 2, "name": "Электроника"},
            {"id": 3, "name": "Разное"},
        ],
    )

    now = datetime.now()

    session_ids = [
        str(uuid.UUID("11111111-1111-1111-1111-111111111111")),
        str(uuid.UUID("22222222-2222-2222-2222-222222222222")),
        str(uuid.UUID("33333333-3333-3333-3333-333333333333")),
    ]

    rows = [
        {
            "session_id": session_ids[i % 3],
            "name": name,
            "weight": weight,
            "content_price_usd": price,
            "parcel_type_id": parcel_type,
            "delivery_price_rub": delivery,
            "company_id": company,
            "created_at": now + timedelta(minutes=i),
            "updated_at": now + timedelta(minutes=i),
        }
        for i, (name, weight, price, parcel_type, delivery, company) in enumerate([
            ("Футболка Nike", Decimal("0.35"), Decimal("35.00"), 1, Decimal("850.00"), 1),
            ("Джинсы Levi's", Decimal("0.80"), Decimal("70.00"), 1, Decimal("1200.00"), 1),
            ("Куртка Columbia", Decimal("1.20"), Decimal("120.00"), 1, Decimal("1800.00"), 2),
            ("Кроссовки Adidas", Decimal("0.95"), Decimal("90.00"), 1, Decimal("1500.00"), 2),
            ("Шапка", Decimal("0.15"), Decimal("15.00"), 1, Decimal("500.00"), 1),
            ("iPhone 15", Decimal("0.45"), Decimal("999.00"), 2, Decimal("4500.00"), 3),
            ("Samsung Galaxy", Decimal("0.40"), Decimal("850.00"), 2, Decimal("4200.00"), 3),
            ("Ноутбук Lenovo", Decimal("2.30"), Decimal("1200.00"), 2, Decimal("5500.00"), 2),
            ("Наушники Sony", Decimal("0.28"), Decimal("180.00"), 2, Decimal("1300.00"), 1),
            ("Планшет Xiaomi", Decimal("0.70"), Decimal("320.00"), 2, Decimal("2400.00"), 3),
            ("Книга", Decimal("0.55"), Decimal("18.00"), 3, Decimal("600.00"), 1),
            ("Игрушка LEGO", Decimal("1.10"), Decimal("65.00"), 3, Decimal("1400.00"), 2),
            ("Кружка", Decimal("0.40"), Decimal("12.00"), 3, Decimal("700.00"), 2),
            ("Настольная лампа", Decimal("0.90"), Decimal("45.00"), 3, Decimal("1200.00"), 1),
            ("Рюкзак", Decimal("0.85"), Decimal("55.00"), 3, Decimal("1350.00"), 3),
            ("Часы Casio", Decimal("0.22"), Decimal("80.00"), 2, Decimal("1100.00"), 2),
            ("Худи", Decimal("0.75"), Decimal("60.00"), 1, Decimal("1400.00"), 1),
            ("Пауэрбанк", Decimal("0.33"), Decimal("40.00"), 2, Decimal("900.00"), 3),
            ("Зонт", Decimal("0.50"), Decimal("20.00"), 3, Decimal("750.00"), 2),
            ("Сумка", Decimal("0.68"), Decimal("48.00"), 1, Decimal("1250.00"), 1),
        ])
    ]

    op.bulk_insert(parcels, rows)


def downgrade() -> None:
    op.execute("DELETE FROM parcels")
    op.execute("DELETE FROM parcel_types")