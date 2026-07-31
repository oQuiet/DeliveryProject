import pytest
from app.presentation.schemas.models import ParcelResponse
from app.presentation.routers.parcels import parcelsroute

@pytest.mark.parametrize(
    "parcel_id, expected_status, expected_result",
    [
        (1,200, ParcelResponse),
        (10,200, ParcelResponse),
        (20,200, ParcelResponse)
    ]
)
def test_get_concrete_parcel(parcel_id, expected_status, expected_result, client) -> None:
    response = client.get(f"/parcels/{parcel_id}")
    assert response.status_code == expected_status
