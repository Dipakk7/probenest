from app.documents.chunker import DocumentChunker
from app.models import Document


def test_document_chunker_deterministic_split() -> None:
    """Test that DocumentChunker deterministically splits documents and preserves metadata."""
    doc = Document(
        id="test_doc",
        title="Test Document",
        content="Alpha beta gamma delta epsilon. " * 20,
        metadata={"filename": "test_doc.md"},
    )

    chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
    chunks = chunker.chunk_document(doc)

    assert len(chunks) > 1
    assert chunks[0].document_id == "test_doc"
    assert chunks[0].title == "Test Document"
    assert chunks[0].id == "test_doc_000"
    assert chunks[1].id == "test_doc_001"
