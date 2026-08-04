from fastapi.testclient import TestClient
from app.main import app
import pytest
from collections.abc import Iterator


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client

