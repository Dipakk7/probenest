from fastapi.testclient import TestClient

from app.db.database import init_db
from app.main import app

client = TestClient(app)


def test_trigger_and_get_redteam_api() -> None:
    """Test POST /api/v1/redteam and GET /api/v1/redteam/{run_id}."""
    init_db()
    post_res = client.post("/api/v1/redteam", json={"target": "mock"})
    assert post_res.status_code == 201
    data = post_res.json()
    assert "run_id" in data
    assert data["status"] == "completed"

    run_id = data["run_id"]

    # Test GET list
    list_res = client.get("/api/v1/redteam")
    assert list_res.status_code == 200
    runs = list_res.json()
    assert len(runs) >= 1

    # Test GET single
    get_res = client.get(f"/api/v1/redteam/{run_id}")
    assert get_res.status_code == 200
    single_data = get_res.json()
    assert single_data["run_id"] == run_id
