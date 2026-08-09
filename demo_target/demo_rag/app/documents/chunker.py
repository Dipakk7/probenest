from app.models import Document, DocumentChunk


class DocumentChunker:
    """Splits Documents into deterministic text chunks with configurable size and overlap."""

    def __init__(self, chunk_size: int = 400, chunk_overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, document: Document) -> list[DocumentChunk]:
        """Split a single Document into a list of DocumentChunks."""
        text = document.content.strip()
        if not text:
            return []

        chunks: list[DocumentChunk] = []
        start = 0
        text_len = len(text)
        chunk_idx = 0

        step = max(1, self.chunk_size - self.chunk_overlap)

        while start < text_len:
            end = min(text_len, start + self.chunk_size)
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunk_id = f"{document.id}_{chunk_idx:03d}"
                chunks.append(
                    DocumentChunk(
                        id=chunk_id,
                        document_id=document.id,
                        title=document.title,
                        text=chunk_text,
                        chunk_index=chunk_idx,
                        metadata={
                            "start_char": start,
                            "end_char": end,
                            "source_file": document.metadata.get("filename", ""),
                        },
                    )
                )
                chunk_idx += 1

            if end == text_len:
                break
            start += step

        return chunks

    def chunk_documents(self, documents: list[Document]) -> list[DocumentChunk]:
        """Split multiple Documents into DocumentChunks."""
        all_chunks: list[DocumentChunk] = []
        for doc in documents:
            all_chunks.extend(self.chunk_document(doc))
        return all_chunks
