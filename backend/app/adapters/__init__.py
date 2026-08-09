"""Target application adapters package."""
from app.adapters.demo_rag import DemoRAGAdapter
from app.adapters.mock_target import MockTargetAdapter

__all__ = ["DemoRAGAdapter", "MockTargetAdapter"]
