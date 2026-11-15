from fastapi.testclient import TestClient

from app.database import create_repository
from app.main import app

app.dependency_overrides[create_repository] = lambda: None
client = TestClient(app)


def test_ping_is_empty() -> None:
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.content == b""


def test_invalid_reading_is_400() -> None:
    response = client.post(
        "/realty/1/readings",
        json={
            "user_id": 1,
            "gauge_id": 1,
            "tariff_id": 1,
            "reading_date": "2026-10-01",
            "day_kw": -1,
            "night_kw": 10,
        },
    )
    assert response.status_code == 400
    assert response.json() == {"message": 'invalid "day_kw" field'}


def test_missing_tariff_date_is_400() -> None:
    response = client.get("/tariffs")
    assert response.status_code == 400
    assert response.json() == {"message": 'invalid "date" parameter'}
