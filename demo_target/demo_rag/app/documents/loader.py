from pathlib import Path

from app.models import Document


class DocumentLoader:
    """Discovers and loads Markdown (.md) and text (.txt) files into Document models."""

    @staticmethod
    def load_directory(directory_path: str | Path) -> list[Document]:
        """Load all .md and .txt files from the target directory."""
        dir_path = Path(directory_path)
        if not dir_path.is_dir():
            return []

        documents: list[Document] = []
        for file_path in sorted(dir_path.glob("*")):
            if file_path.suffix.lower() in [".md", ".txt"]:
                doc = DocumentLoader.load_file(file_path)
                if doc:
                    documents.append(doc)
        return documents

    @staticmethod
    def load_file(file_path: str | Path) -> Document | None:
        """Load a single document file."""
        path = Path(file_path)
        if not path.is_file():
            return None

        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None

        doc_id = path.stem
        # Extract title from first markdown header if available
        lines = content.strip().splitlines()
        title = doc_id.replace("_", " ").title()
        if lines and lines[0].startswith("#"):
            title = lines[0].lstrip("#").strip()

        return Document(
            id=doc_id,
            title=title,
            content=content,
            metadata={"filename": path.name, "file_path": str(path)},
        )
