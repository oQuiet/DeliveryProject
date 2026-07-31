from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.application.repositories import ParcelRepository
from app.domain.delivery_price import calculate_delivery_price
from app.domain.entities import Parcel
from app.infrastructure.orm.models import Parcel as ParcelModel, ParcelType
from app.presentation.schemas.parcel_query_params import ParcelQueryParams


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
            delivery_price=parcel.delivery_price,
            company_id=parcel.company_id,
        )

        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)

        parcel.id = model.id
        return parcel

    async def list_by_session(self, session_id: str, params: ParcelQueryParams) -> list[Parcel]:
        # stmt = (
        #     select(ParcelModel)
        #     .where(ParcelModel.session_id == session_id, ParcelModel.parcel_type_id=)
        # )
        # statement = select(ParcelModel).where(ParcelModel.session_id == session_id)
        # models = (await self.session.scalars(statement)).all()

        # return [self._to_entity(model) for model in models]

        stmt = (
            select(ParcelModel)
            .options(selectinload(ParcelModel.parcel_type))
            .where(ParcelModel.session_id == session_id)
        )

        if params.parcel_type is not None:
            stmt = stmt.join(ParcelModel.parcel_type).where(ParcelType.name.in_(params.parcel_type))

        if params.has_delivery_price is True:
            stmt = stmt.where(ParcelModel.delivery_price.is_not(None))

        elif params.has_delivery_price is False:
            stmt = stmt.where(ParcelModel.delivery_price.is_(None))

        stmt = stmt.limit(params.limit).offset(params.offset)
        models = (await self.session.scalars(stmt)).all()

        return [self._to_entity(model) for model in models]

    async def get_by_id(self, parcel_id: int) -> Parcel | None:
        package = await self.session.get(ParcelModel, parcel_id)
        return self._to_entity(package) if package else None

    async def list_unprocessed(self) -> list[Parcel]:
        stmt = select(ParcelModel).where(ParcelModel.delivery_price.is_(None))
        unprocessed = (await self.session.scalars(stmt)).all()

        return [self._to_entity(model) for model in unprocessed]

    async def list_processed(self) -> list[Parcel]:
        stmt = select(ParcelModel).where(ParcelModel.delivery_price.is_not(None))
        processed = (await self.session.scalars(stmt)).all()

        return [self._to_entity(model) for model in processed]

    async def set_delivery_prices(self, usd_rate: Decimal) -> int:
        select_stmt = select(
            ParcelModel.id,
            ParcelModel.weight,
            ParcelModel.content_price_usd,
        ).where(ParcelModel.delivery_price.is_(None))

        result = await self.session.execute(select_stmt)
        rows = result.all()

        if not rows:
            return 0

        updates = [
            {
                "id": row.id,
                "delivery_price": calculate_delivery_price(
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
    #     stmt = select(ParcelModel).where(ParcelModel.delivery_price.is_(None))
    #     models = (await self.session.scalars(stmt)).all()

    #     if not models:
    #         return None

    #     for model in models:
    #         model.delivery_price = calculate_delivery_price(
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
            delivery_price=model.delivery_price,
            company_id=model.company_id,
        )
