from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Parcel(Base):
    __tablename__ = "parcels"

    id: Mapped[int] = mapped_column(primary_key=True)

    session_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    weight: Mapped[Decimal] = mapped_column(
        Numeric(8, 3),
        nullable=False,
    )

    content_price_usd: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    parcel_type_id: Mapped[int] = mapped_column(
        ForeignKey("parcel_types.id"),
        nullable=False,
    )

    delivery_price_rub: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    company_id: Mapped[int | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
    )

    parcel_type = relationship(
        "ParcelType",
        back_populates="parcels",
    )

    __table_args__ = (Index("ix_parcels_session_type", "session_id", "parcel_type_id"),)


class ParcelType(Base):
    __tablename__ = "parcel_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    parcels = relationship("Parcel", back_populates="parcel_type")
