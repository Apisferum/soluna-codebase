from fastapi.testclient import TestClient

from app.main import app


def test_root() -> None:
    with TestClient(app) as client:
        response = client.get("/api/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Synestra unified backend is running",
        "service": "Synestra Unified Backend",
        "version": "1.0.0",
    }


def test_health() -> None:
    with TestClient(app) as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Synestra Unified Backend",
    }
