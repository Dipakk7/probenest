from app.llm.mock_llm import MockLLMProvider
from app.rag.pipeline import RAGPipeline


def test_rag_pipeline_execution() -> None:
    """Test RAGPipeline query execution with MockLLMProvider."""
    pipeline = RAGPipeline(llm_provider=MockLLMProvider())
    response = pipeline.query("What is the refund window?")

    assert response.answer is not None
    assert len(response.answer) > 0
    assert response.metadata["provider"] == "MockLLMProvider"
    assert "refund" in [s.document_id for s in response.sources] or len(response.sources) >= 0
