from app.models import DocumentChunk
from app.retrieval.retriever import TFIDFRetriever


def test_tfidf_retriever_ranking() -> None:
    """Test that TFIDFRetriever correctly ranks relevant chunks."""
    chunks = [
        DocumentChunk(
            id="c1",
            document_id="refund",
            title="Refund Policy",
            text="Customers can request a full refund within 30 days.",
        ),
        DocumentChunk(
            id="c2",
            document_id="shipping",
            title="Shipping Policy",
            text="Standard domestic shipping takes 3 to 5 business days.",
        ),
    ]

    retriever = TFIDFRetriever(top_k=2)
    retriever.fit(chunks)

    results = retriever.retrieve("refund 30 days")
    assert len(results) >= 1
    assert results[0].chunk.document_id == "refund"
    assert results[0].score > 0.0
