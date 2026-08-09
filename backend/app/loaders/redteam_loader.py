import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from app.domain.redteam import RedTeamCase
from app.loaders.dataset import DatasetLoadError


class RedTeamDatasetLoader:
    """Loader utility for reading and validating adversarial red-team datasets."""

    @staticmethod
    def load_from_file(file_path: str | Path) -> list[RedTeamCase]:
        """Load red-team cases from a JSON file path.

        Raises:
            DatasetLoadError: If file is missing, invalid JSON, or cases fail validation.
        """
        path = Path(file_path)

        if not path.is_file():
            raise DatasetLoadError(f"Red-team dataset file not found: '{file_path}'")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise DatasetLoadError(f"Invalid JSON in red-team dataset file '{file_path}': {e}") from e
        except Exception as e:
            raise DatasetLoadError(f"Failed to read red-team dataset file '{file_path}': {e}") from e

        return RedTeamDatasetLoader.load_from_data(data, source_name=str(file_path))

    @staticmethod
    def load_from_data(data: Any, source_name: str = "raw_data") -> list[RedTeamCase]:
        """Validate raw data into a list of RedTeamCase models."""
        if not isinstance(data, list):
            raise DatasetLoadError(f"Red-team dataset in '{source_name}' must be a JSON array of attack case objects.")

        cases: list[RedTeamCase] = []
        for index, item in enumerate(data):
            if not isinstance(item, dict):
                raise DatasetLoadError(f"Item at index {index} in '{source_name}' is not a valid JSON object.")
            try:
                case = RedTeamCase.model_validate(item)
                cases.append(case)
            except ValidationError as e:
                raise DatasetLoadError(
                    f"Validation failed for red-team case at index {index} in '{source_name}': {e}"
                ) from e

        return cases
