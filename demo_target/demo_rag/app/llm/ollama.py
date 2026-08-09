import httpx

from app.llm.base import LLMProviderError


class OllamaProvider:
    """Ollama API LLM generation provider (e.g. Qwen2.5:7b)."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen2.5:7b") -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """Send generation payload to Ollama HTTP API endpoint."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload)
                if response.status_code != 200:
                    raise LLMProviderError(
                        f"Ollama returned HTTP {response.status_code}: {response.text}"
                    )
                data = response.json()
                return data.get("response", "").strip()

        except httpx.ConnectError as e:
            raise LLMProviderError(
                f"Ollama is unavailable at {self.base_url}. Start Ollama and ensure the configured model '{self.model}' is available."
            ) from e
        except Exception as e:
            raise LLMProviderError(f"Ollama generation request failed: {e}") from e
