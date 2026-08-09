from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class DemoRAGSettings(BaseSettings):
    """DemoRAG configuration settings."""

    DEMORAG_HOST: str = "127.0.0.1"
    DEMORAG_PORT: int = 8001
    LLM_PROVIDER: str = "mock"  # "mock" or "ollama"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:7b"
    DOCUMENTS_DIR: str = "data/documents"
    CHUNK_SIZE: int = 400
    CHUNK_OVERLAP: int = 50
    TOP_K: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def resolve_documents_dir(self) -> Path:
        """Resolve documents directory relative to package root if needed."""
        path = Path(self.DOCUMENTS_DIR)
        if path.is_absolute() and path.exists():
            return path

        # Try relative to package root
        package_root = Path(__file__).resolve().parent.parent
        resolved = package_root / self.DOCUMENTS_DIR
        if resolved.exists():
            return resolved

        return path.resolve()


settings = DemoRAGSettings()
