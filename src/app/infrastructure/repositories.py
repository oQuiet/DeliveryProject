from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.repositories import ParcelRepository
from app.domain.delivery_price import calculate_delivery_price
from app.domain.entities import Parcel
from app.infrastructure.orm.models import Parcel as ParcelModel


class SQLAlchemyParcelRepository(ParcelRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        # self.statement = (select(ParcelModel).options(selectinload(ParcelModel.parcel_type)))

    async def add(self, parcel: Parcel) -> Parcel:
        model = ParcelModel(
            session_id=parcel.session_id,
            name=parcel.name,
            weight=parcel.weight,
            content_price_usd=parcel.content_price_usd,
            parcel_type_id=parcel.parcel_type_id,
            delivery_price_rub=parcel.delivery_price_rub,
            company_id=parcel.company_id,
        )

        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)

        parcel.id = model.id
        return parcel

    async def list_by_session(self, session_id: str) -> list[Parcel]:
        statement = select(ParcelModel).where(ParcelModel.session_id == session_id)
        models = (await self.session.scalars(statement)).all()

        return [self._to_entity(model) for model in models]

    async def get_by_id(self, parcel_id: int) -> Parcel | None:
        package = await self.session.get(ParcelModel, parcel_id)
        return self._to_entity(package) if package else None

    async def list_unprocessed(self) -> list[Parcel]:
        stmt = select(ParcelModel).where(ParcelModel.delivery_price_rub.is_(None))
        unprocessed = (await self.session.scalars(stmt)).all()

        return [self._to_entity(model) for model in unprocessed]

    async def list_processed(self) -> list[Parcel]:
        stmt = select(ParcelModel).where(ParcelModel.delivery_price_rub.is_not(None))
        processed = (await self.session.scalars(stmt)).all()

        return [self._to_entity(model) for model in processed]

    async def set_delivery_prices(self, usd_rate: Decimal) -> int:
        select_stmt = select(
            ParcelModel.id,
            ParcelModel.weight,
            ParcelModel.content_price_usd,
        ).where(ParcelModel.delivery_price_rub.is_(None))

        result = await self.session.execute(select_stmt)
        rows = result.all()

        if not rows:
            return 0

        updates = [
            {
                "id": row.id,
                "delivery_price_rub": calculate_delivery_price(
                    weight=row.weight,
                    content_price_usd=row.content_price_usd,
                    usd_rate=usd_rate,
                ),
            }
            for row in rows
        ]

        await self.session.execute(
            update(ParcelModel),
            updates,
        )

        await self.session.commit()

        return len(updates)

    # async def set_delivery_prices(self, usd_rate: Decimal) -> int | None:
    #     stmt = select(ParcelModel).where(ParcelModel.delivery_price_rub.is_(None))
    #     models = (await self.session.scalars(stmt)).all()

    #     if not models:
    #         return None

    #     for model in models:
    #         model.delivery_price_rub = calculate_delivery_price(
    #             model.weight,
    #             model.content_price_usd,
    #             usd_rate )

    #     await self.session.commit()

    #     return len(models)

    @staticmethod
    def _to_entity(model: ParcelModel) -> Parcel:
        return Parcel(
            id=model.id,
            session_id=model.session_id,
            name=model.name,
            weight=model.weight,
            content_price_usd=model.content_price_usd,
            parcel_type_id=model.parcel_type_id,
            delivery_price_rub=model.delivery_price_rub,
            company_id=model.company_id,
        )
