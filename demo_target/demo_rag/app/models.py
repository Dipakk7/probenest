from typing import Any

from pydantic import BaseModel, Field


class Document(BaseModel):
    """Represents a loaded raw document."""

    id: str = Field(description="Unique document identifier")
    title: str = Field(description="Document title")
    content: str = Field(description="Raw text content of the document")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Document metadata")


class DocumentChunk(BaseModel):
    """Represents a text chunk extracted from a Document."""

    id: str = Field(description="Unique chunk identifier")
    document_id: str = Field(description="ID of parent Document")
    title: str = Field(description="Title of parent Document")
    text: str = Field(description="Text snippet of the chunk")
    chunk_index: int = Field(default=0, description="Sequential chunk index")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Chunk metadata")


class RetrievedChunk(BaseModel):
    """Represents a chunk retrieved by the search engine with relevance score."""

    chunk: DocumentChunk = Field(description="The matching document chunk")
    score: float = Field(description="Relevance similarity score (0.0 to 1.0)")


class SourceMetadata(BaseModel):
    """Citation metadata for retrieved sources."""

    document_id: str = Field(description="ID of source document")
    title: str = Field(description="Title of source document")
    score: float = Field(description="Retrieval relevance score")


class QueryRequest(BaseModel):
    """Payload for DemoRAG /query API endpoint."""

    question: str = Field(description="User question or query string")


class QueryResponse(BaseModel):
    """Response payload returned by DemoRAG /query API endpoint."""

    answer: str = Field(description="Generated response answer")
    sources: list[SourceMetadata] = Field(default_factory=list, description="Source document citations")
    retrieved_chunks: list[dict[str, Any]] = Field(default_factory=list, description="Detailed retrieved chunk payloads")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Pipeline execution metadata")
