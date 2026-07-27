from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.repositories import ParcelRepository
from src.domain.entities import Parcel
from src.infrastructure.orm.models import Parcel as ParcelModel


class SQLAlchemyParcelRepository(ParcelRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

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
