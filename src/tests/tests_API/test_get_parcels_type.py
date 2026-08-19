import pytest
from types import SimpleNamespace


@pytest.mark.asyncio
async def test_get_parcels_type(client, db_session):
    db_session.scalars.return_value = [
        SimpleNamespace(id=1, name="Одежда"),
        SimpleNamespace(id=2, name="Электроника"),
        SimpleNamespace(id=3, name="Разное"),
    ]

    response = await client.get("/parcels_types")

    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "name": "Одежда"},
        {"id": 2, "name": "Электроника"},
        {"id": 3, "name": "Разное"},
    ]

    db_session.scalars.assert_awaited_once()