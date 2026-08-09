from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_trigger_and_get_evaluation_api() -> None:
    """Test POST /api/v1/evaluations and GET /api/v1/evaluations/{run_id}."""
    post_res = client.post("/api/v1/evaluations", json={})
    assert post_res.status_code == 201
    data = post_res.json()
    assert "run_id" in data
    assert data["status"] == "completed"
    assert data["total_cases"] == 5

    run_id = data["run_id"]

    # Test GET list
    list_res = client.get("/api/v1/evaluations")
    assert list_res.status_code == 200
    runs = list_res.json()
    assert len(runs) >= 1

    # Test GET single
    get_res = client.get(f"/api/v1/evaluations/{run_id}")
    assert get_res.status_code == 200
    single_data = get_res.json()
    assert single_data["run_id"] == run_id
    assert len(single_data["results"]) == 20  # 5 cases * 4 quality evaluators
