from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import UUID
from uuid import uuid4

from fastapi import Cookie, Response
from httpx2 import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import pytest
import pytest_asyncio

from app.application.parcel_service import ParcelService
from app.domain.entities import Parcel
from app.infrastructure.database import get_db
from app.main import app
from app.presentation.dependencies import get_parcel_service, get_session_id


@pytest.fixture
def parcel() -> Parcel:
    return Parcel(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        name="Холодильник Haier",
        weight=Decimal("50.00"),
        parcel_type_id=1,
        content_price_usd=Decimal("1000.00"),
        session_id="536fb57b-2711-4237-ae38-2e710e68fb03",
        delivery_price=Decimal("2800.00"),
        company_id=1,
    )

@pytest.fixture
def parcel_service() -> AsyncMock:
    return AsyncMock(spec=ParcelService)

@pytest_asyncio.fixture
def db_session() -> AsyncMock:
    return AsyncMock(spec=AsyncSession)

@pytest_asyncio.fixture
async def client(parcel_service: AsyncMock, db_session: AsyncMock):

    async def override_parcel_service() -> AsyncMock:
        return parcel_service

    async def override_get_db() -> AsyncMock:
        return db_session

    app.dependency_overrides[get_parcel_service] = override_parcel_service
    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(
            transport=transport,
            base_url="https://test",
        ) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
