import pytest
from fastapi.testclient import TestClient
from tests._compat import app


@pytest.fixture
def client():
    return TestClient(app)
