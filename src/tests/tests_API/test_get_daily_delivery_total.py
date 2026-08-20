import pytest
from decimal import Decimal

# -------------------------- Happy path --------------------------

@pytest.mark.asyncio
async def test_get_daily_delivery_total_happy_path(client, mongo_service):
    mongo_service.get.return_value=Decimal("1000.064")

    response = await client.get("/delivery_prices", params={"parcel_type_id": 1})

    assert response.status_code == 200
    assert response.json() == '1000.064'

    mongo_service.get.assert_awaited_once_with(1)


# -------------------------- Negative path --------------------------

@pytest.mark.asyncio
async def test_get_daily_delivery_total_negative_path(client, mongo_service):
    mongo_service.get.return_value=None

    response = await client.get("/delivery_prices", params={"parcel_type_id": 1})

    assert response.status_code == 404
    assert response.json() == {"Ошибка": "Посылок с таким типом за последние 3 дня не найдено"}

    mongo_service.get.assert_awaited_once_with(1)