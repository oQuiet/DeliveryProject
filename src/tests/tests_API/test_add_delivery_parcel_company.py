from uuid import UUID

import pytest

# -------------------------- Happy path --------------------------

@pytest.mark.asyncio
async def test_add_delivery_parcel_company_happy_path(client, parcel_service, parcel):
    parcel_id = UUID("11111111-1111-1111-1111-111111111111")
    company_id = 3

    parcel.assign_company(company_id)
    parcel_service.assign_company.return_value = parcel

    response = await client.patch(
        f"/parcels/{parcel_id}/company",
        json={"company_id": company_id},
    )

    expected_response = {
        "id": str(parcel_id),
        "name": "Холодильник Haier",
        "weight": "50.00",
        "content_price_usd": "1000.00",
        "delivery_price": "2800.00",
        "company_id": company_id,
        "parcel_type": "Одежда",
    }

    assert response.status_code == 200
    assert response.json() == expected_response

    parcel_service.assign_company.assert_awaited_once_with(
        parcel_id,
        company_id,
    )


# -------------------------- Negative path --------------------------

@pytest.mark.asyncio
async def test_add_delivery_parcel_company_negative_path(client, parcel_service):
    parcel_id = UUID("11111111-1111-1111-1111-111111111111")
    company_id = 2

    parcel_service.assign_company.return_value = None


    response = await client.patch(
        f"/parcels/{parcel_id}/company",
        json={"company_id": company_id}
    )

    assert response.status_code == 409
    assert response.json() == {"Ошибка": "Посылка уже закреплена за другой транспортной компанией"}

    parcel_service.assign_company.assert_awaited_once_with(parcel_id, company_id)
