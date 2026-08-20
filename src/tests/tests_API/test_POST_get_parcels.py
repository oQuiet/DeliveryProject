from decimal import Decimal
from unittest.mock import Mock
from uuid import UUID

import pytest

from app.tasks.celery_tasks import register_parcel_task

SESSION_ID = "536fb57b-2711-4237-ae38-2e710e68fb03"
VALID_PARCEL_DATA = {
    "name": "Холодильник Haier",
    "weight": "50.00",
    "content_price_usd": "1000.00",
    "parcel_type_id": 2,
}


# -------------------------- Happy path --------------------------


@pytest.mark.asyncio
async def test_register_parcel_happy_path_with_existing_session(
    client,
    monkeypatch,
):
    parcel_id = UUID("11111111-1111-1111-1111-111111111111")
    delay_mock = Mock()

    client.cookies.set("session_id", SESSION_ID)
    monkeypatch.setattr("app.presentation.routers.parcels.uuid.uuid4", lambda: parcel_id)
    monkeypatch.setattr(register_parcel_task, "delay", delay_mock)

    response = await client.post("/parcels", json=VALID_PARCEL_DATA)

    assert response.status_code == 201
    assert response.json() == str(parcel_id)
    delay_mock.assert_called_once_with(
        SESSION_ID,
        parcel_id,
        {
            "name": "Холодильник Haier",
            "weight": Decimal("50.00"),
            "content_price_usd": Decimal("1000.00"),
            "parcel_type_id": 2,
            "company_id": None,
        },
    )


@pytest.mark.asyncio
async def test_register_parcel_creates_session_cookie(
    client,
    monkeypatch,
):
    parcel_id = UUID("11111111-1111-1111-1111-111111111111")
    delay_mock = Mock()

    monkeypatch.setattr("app.presentation.routers.parcels.uuid.uuid4", lambda: parcel_id)
    monkeypatch.setattr(register_parcel_task, "delay", delay_mock)

    response = await client.post("/parcels", json=VALID_PARCEL_DATA)

    session_id = response.cookies.get("session_id")

    assert response.status_code == 201
    assert session_id is not None
    UUID(session_id)
    assert delay_mock.call_args.args[0] == session_id


# -------------------------- Negative path --------------------------


@pytest.mark.parametrize(
    "invalid_fields",
    [
        {"weight": 0},
        {"content_price_usd": -1},
        {"parcel_type_id": 4},
        {"name": "x" * 256},
    ],
)
@pytest.mark.asyncio
async def test_register_parcel_invalid_body(
    client,
    monkeypatch,
    invalid_fields,
):
    delay_mock = Mock()
    request_data = VALID_PARCEL_DATA | invalid_fields

    monkeypatch.setattr(register_parcel_task, "delay", delay_mock)

    response = await client.post("/parcels", json=request_data)

    assert response.status_code == 422
    assert response.json() == {"Ошибка": "Переданы некорректные данные"}
    delay_mock.assert_not_called()
