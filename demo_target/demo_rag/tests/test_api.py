from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_demorag_health_endpoint() -> None:
    """Test GET /health on DemoRAG service."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "demorag"


def test_demorag_query_endpoint() -> None:
    """Test POST /query on DemoRAG service."""
    response = client.post("/query", json={"question": "What is the return period?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert "retrieved_chunks" in data
