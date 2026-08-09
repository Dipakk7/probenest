from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    """Test GET /health returns 200 OK and expected JSON payload."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "probenest"


def test_root_endpoint() -> None:
    """Test GET / returns 200 OK and service metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Probenest"
    assert data["status"] == "running"
