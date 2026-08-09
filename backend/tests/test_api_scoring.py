from fastapi.testclient import TestClient

from app.db.database import init_db
from app.main import app

client = TestClient(app)


def test_scoring_and_compare_api_endpoints() -> None:
    """Test GET /api/v1/evaluations/{run_id}/score and GET /api/v1/evaluations/compare/{baseline_id}/{candidate_id}."""
    init_db()

    # Trigger run 1
    res1 = client.post("/api/v1/evaluations", json={"target": "mock"})
    assert res1.status_code == 201
    run_id1 = res1.json()["run_id"]

    # Trigger run 2
    res2 = client.post("/api/v1/evaluations", json={"target": "mock"})
    assert res2.status_code == 201
    run_id2 = res2.json()["run_id"]

    # GET score
    score_res = client.get(f"/api/v1/evaluations/{run_id1}/score")
    assert score_res.status_code == 200
    score_data = score_res.json()
    assert "quality_score" in score_data
    assert "overall_score" in score_data

    # GET comparison
    comp_res = client.get(f"/api/v1/evaluations/compare/{run_id1}/{run_id2}")
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    assert "detected" in comp_data
    assert "comparison" in comp_data
