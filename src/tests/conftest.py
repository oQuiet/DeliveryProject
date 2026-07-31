from fastapi.testclient import TestClient
from app.main import app
import pytest


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client