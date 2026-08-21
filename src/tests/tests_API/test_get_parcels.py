
import pytest

from app.presentation.schemas.parcel_query_params import ParcelQueryParams

# -------------------------- Happy path --------------------------

@pytest.mark.asyncio
async def test_get_parcels_empty_case(client, parcel_service):
    parcel_service.get_all.return_value = []

    response = await client.get("/parcels")

    assert response.status_code == 200
    assert response.json() == []

    parcel_service.get_all.assert_awaited_once_with(
        response.cookies.get("session_id"), ParcelQueryParams()
    )


@pytest.mark.asyncio
async def test_get_parcels_content_case(
    client,
    parcel_service,
    parcel,
):
    session_id = "536fb57b-2711-4237-ae38-2e710e68fb03"

    parcel_service.get_all.return_value = [parcel]
    client.cookies.set("session_id", session_id)

    response = await client.get("/parcels")

    assert response.status_code == 200

    expected_response = [
    {
        "id": "11111111-1111-1111-1111-111111111111",
        "name": "Холодильник Haier",
        "weight": "50.00",
        "content_price_usd": "1000.00",
        "delivery_price": "2800.00",
        "company_id": 'Транспортная компания не указана',
        "parcel_type": "Одежда",
    }
]

    assert response.json() == expected_response

    parcel_service.get_all.assert_awaited_once_with(
        session_id,
        ParcelQueryParams(),
    )

@pytest.mark.asyncio
async def test_get_parcels_with_query_params(client, parcel_service):
    parcel_service.get_all.return_value = []

    response = await client.get(
        "/parcels",
        params={"limit": 5, "offset": 0},
    )

    assert response.status_code == 200
    assert response.json() == []

    parcel_service.get_all.assert_awaited_once_with(
        response.cookies.get("session_id"),
        ParcelQueryParams(limit=5, offset=0),
    )

# -------------------------- Negative path --------------------------

@pytest.mark.parametrize(
    "params",
    [
        {"limit": 0},
        {"limit": 101},
        {"offset": -1},
    ],
)
@pytest.mark.asyncio
async def test_get_parcels_invalid_query_params(
    client,
    parcel_service,
    params,
):
    response = await client.get("/parcels", params=params)

    assert response.status_code == 422
    parcel_service.get_all.assert_not_awaited()
