from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models import DocumentChunk, RetrievedChunk


class TFIDFRetriever:
    """Local vector-like retriever using TF-IDF and Cosine Similarity."""

    def __init__(self, top_k: int = 3) -> None:
        self.top_k = top_k
        self.chunks: list[DocumentChunk] = []
        self.vectorizer: TfidfVectorizer | None = None
        self.tfidf_matrix = None

    def fit(self, chunks: list[DocumentChunk]) -> None:
        """Fit TF-IDF matrix on indexed document chunks."""
        self.chunks = chunks
        if not chunks:
            self.vectorizer = None
            self.tfidf_matrix = None
            return

        corpus = [c.text for c in chunks]
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def retrieve(self, query: str, top_k: int | None = None) -> list[RetrievedChunk]:
        """Search and rank top-k relevant document chunks for a query string."""
        if not self.chunks or self.vectorizer is None or self.tfidf_matrix is None or not query.strip():
            return []

        k = top_k or self.top_k
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()

        # Sort indices by score descending
        ranked_indices = similarities.argsort()[::-1]

        results: list[RetrievedChunk] = []
        for idx in ranked_indices[:k]:
            score = float(similarities[idx])
            # Only include chunks with non-zero similarity if available
            if score > 0.0 or len(results) == 0:
                results.append(
                    RetrievedChunk(
                        chunk=self.chunks[idx],
                        score=round(score, 4),
                    )
                )

        return results
