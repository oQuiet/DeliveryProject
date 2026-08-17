"""Seed parcel_types

Revision ID: d2b40e3896b5
Revises: 804decd45398
Create Date: 2026-08-17 17:25:23.355439

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd2b40e3896b5'
down_revision: Union[str, Sequence[str], None] = '804decd45398'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


parcel_types = sa.table(
    "parcel_types",
    sa.column("id", sa.Integer()),
    sa.column("name", sa.String(length=100)),
)


def upgrade() -> None:
    """Add the parcel types required by the application."""
    op.bulk_insert(
        parcel_types,
        [
            {"id": 1, "name": "Одежда"},
            {"id": 2, "name": "Электроника"},
            {"id": 3, "name": "Разное"},
        ],
    )

    # Explicit IDs do not advance a PostgreSQL sequence automatically.
    op.execute(
        "SELECT setval("
        "pg_get_serial_sequence('parcel_types', 'id'), "
        "(SELECT MAX(id) FROM parcel_types)"
        ")"
    )


def downgrade() -> None:
    """Remove the parcel types added by this revision."""
    op.execute(
        parcel_types.delete().where(
            parcel_types.c.id.in_([1, 2, 3]),
        )
    )
