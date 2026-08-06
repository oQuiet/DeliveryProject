from decimal import Decimal
from typing import Annotated

from fastapi import Body, Depends, HTTPException, Query, status
from fastapi.routing import APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.get_daily_total import GetDailyDeliveryTotalService
from app.application.parcel_service import ParcelService
from app.domain.entities import Parcel
from app.infrastructure.database import get_db
from app.infrastructure.orm.models import ParcelType
from app.presentation.dependencies import (
    get_daily_total_service,
    get_parcel_service,
    get_session_id,
)
from app.presentation.schemas.models import ParcelRequest, ParcelResponse, ParcelTypeResponse
from app.presentation.schemas.parcel_query_params import ParcelQueryParams

parcelsroute = APIRouter()


@parcelsroute.post("/parcels")
async def register_parcel(
    parcel_request: ParcelRequest,
    session_id: Annotated[str, Depends(get_session_id)],
    service: Annotated[ParcelService, Depends(get_parcel_service)],
) -> int | None:
    """
    Позволяет зарегистрировать посылку
    """
    parcel = Parcel(**parcel_request.model_dump(), session_id=session_id)
    created = await service.register(parcel)
    return created.id


@parcelsroute.get("/parcels", response_model=list[ParcelResponse])
async def get_parcels(
    session_id: Annotated[str, Depends(get_session_id)],
    service: Annotated[ParcelService, Depends(get_parcel_service)],
    params: Annotated[ParcelQueryParams, Query()],
) -> list[ParcelResponse]:
    """
    Возвращает список посылок пользователя
    """
    parcels = await service.get_all(session_id, params)

    return [ParcelResponse.model_validate(parcel) for parcel in parcels]


@parcelsroute.get("/parcels/{parcel_id}")
async def get_concrete_parcel(
    parcel_id: int, service: Annotated[ParcelService, Depends(get_parcel_service)]
) -> ParcelResponse:
    """
    Возвращает информацию о посылке по ее id
    """
    parcel = await service.get_one(parcel_id)

    if parcel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Посылки с таким id не существует"
        )

    return ParcelResponse.model_validate(parcel)


@parcelsroute.patch("/parcels/{parcel_id}/company")
async def add_delivery_parcel_company(
    parcel_id: int,
    company_id: Annotated[int, Body(embed=True, gt=0)],
    service: Annotated[ParcelService, Depends(get_parcel_service)],
) -> ParcelResponse:
    """
    Позволяет добавить id компании к конкретной посылке по ее id
    """
    parcel = await service.assign_company(parcel_id, company_id)
    if parcel is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Посылка уже закреплена за другой транспортной компанией",
        )

    return ParcelResponse.model_validate(parcel)


@parcelsroute.get("/delivery-prices")
async def get_daily_delivery_total(
    service: Annotated[GetDailyDeliveryTotalService, Depends(get_daily_total_service)],
    parcel_type_id: Annotated[int, Query()],
) -> Decimal:
    """
    Возвращает сумму стоимости всех доставок по типу посылки за последние 3 дня
    """
    total = await service.get(parcel_type_id)
    return total


@parcelsroute.get("/parcels_types", response_model=list[ParcelTypeResponse])
async def get_parcels_types(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[ParcelTypeResponse]:
    """
    Возвращает доступные типы посылок и их id
    """
    models = await session.scalars(select(ParcelType))
    return [ParcelTypeResponse.model_validate(model) for model in models]
