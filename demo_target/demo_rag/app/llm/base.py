from typing import Protocol, runtime_checkable


class LLMProviderError(Exception):
    """Exception raised when an LLM provider generation request fails."""


@runtime_checkable
class LLMProvider(Protocol):
    """Protocol interface for language model generation providers."""

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """Generate response text for the provided prompt and system prompt."""
        ...
