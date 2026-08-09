from app.adapters.demo_rag import DemoRAGAdapter
from app.domain.case import EvaluationCase


def test_demorag_adapter_offline_graceful_handling() -> None:
    """Test that DemoRAGAdapter returns a graceful error in TargetResponse when service is offline."""
    adapter = DemoRAGAdapter(base_url="http://127.0.0.1:59999")
    case = EvaluationCase(id="c1", input="What is the refund period?")

    response = adapter.run(case)
    assert response.output is not None
    assert "DemoRAG is unavailable" in response.output
    assert response.metadata.get("error") == "connection_failed"
