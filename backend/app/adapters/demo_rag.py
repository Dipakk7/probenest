import httpx

from app.core.config import settings
from app.domain.case import EvaluationCase
from app.domain.target import TargetResponse


class DemoRAGAdapter:
    """TargetAdapter implementation communicating with DemoRAG application service."""

    def __init__(self, base_url: str | None = None) -> None:
        raw_url = base_url or getattr(settings, "DEMORAG_BASE_URL", "http://127.0.0.1:8001")
        self.base_url = raw_url.rstrip("/")

    def run(self, case: EvaluationCase) -> TargetResponse:
        """Send case input to DemoRAG /query API endpoint and convert to TargetResponse."""
        url = f"{self.base_url}/query"
        payload = {"question": case.input}

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(url, json=payload)
                if response.status_code != 200:
                    output = f"DemoRAG API error (HTTP {response.status_code}): {response.text}"
                    return TargetResponse(
                        output=output,
                        metadata={"adapter": "DemoRAGAdapter", "status_code": response.status_code},
                    )

                data = response.json()
                answer = data.get("answer", "")
                sources = data.get("sources", [])
                retrieved_chunks = data.get("retrieved_chunks", [])
                meta = data.get("metadata", {})

                context_texts = [c["text"] for c in retrieved_chunks if isinstance(c, dict) and "text" in c]

                return TargetResponse(
                    output=answer,
                    context=context_texts if context_texts else None,
                    tool_calls=None,
                    metadata={
                        "adapter": "DemoRAGAdapter",
                        "sources": sources,
                        "retrieved_chunks_count": len(retrieved_chunks),
                        "demorag_metadata": meta,
                    },
                )

        except httpx.ConnectError:
            error_msg = f"DemoRAG is unavailable at {self.base_url}. Start the DemoRAG service before running evaluations."
            return TargetResponse(
                output=error_msg,
                metadata={"adapter": "DemoRAGAdapter", "error": "connection_failed"},
            )
        except Exception as e:  # noqa: BLE001
            error_msg = f"Failed to communicate with DemoRAG at {self.base_url}: {e}"
            return TargetResponse(
                output=error_msg,
                metadata={"adapter": "DemoRAGAdapter", "error": str(e)},
            )
