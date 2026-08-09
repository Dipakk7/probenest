import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from app.domain.case import EvaluationCase


class DatasetLoadError(Exception):
    """Exception raised when loading or parsing a dataset fails."""


class DatasetLoader:
    """Loader utility for reading and validating evaluation dataset files."""

    @staticmethod
    def load_from_file(file_path: str | Path) -> list[EvaluationCase]:
        """Load evaluation cases from a JSON file path.

        Raises:
            DatasetLoadError: If file is missing, invalid JSON, or cases fail validation.
        """
        path = Path(file_path)

        if not path.is_file():
            raise DatasetLoadError(f"Dataset file not found: '{file_path}'")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise DatasetLoadError(f"Invalid JSON in dataset file '{file_path}': {e}") from e
        except Exception as e:
            raise DatasetLoadError(f"Failed to read dataset file '{file_path}': {e}") from e

        return DatasetLoader.load_from_data(data, source_name=str(file_path))

    @staticmethod
    def load_from_data(data: Any, source_name: str = "raw_data") -> list[EvaluationCase]:
        """Validate raw dictionary/list data into a list of EvaluationCase models."""
        if not isinstance(data, list):
            raise DatasetLoadError(f"Dataset in '{source_name}' must be a JSON array of case objects.")

        cases: list[EvaluationCase] = []
        for index, item in enumerate(data):
            if not isinstance(item, dict):
                raise DatasetLoadError(f"Item at index {index} in '{source_name}' is not a valid JSON object.")
            try:
                case = EvaluationCase.model_validate(item)
                cases.append(case)
            except ValidationError as e:
                raise DatasetLoadError(
                    f"Validation failed for case at index {index} in '{source_name}': {e}"
                ) from e

        return cases
