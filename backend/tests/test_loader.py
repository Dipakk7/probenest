import pytest

from app.loaders.dataset import DatasetLoader, DatasetLoadError


def test_load_valid_data() -> None:
    """Test loading valid dictionary array into EvaluationCase models."""
    data = [
        {"id": "c1", "input": "input 1", "expected_output": "out 1"},
        {"id": "c2", "input": "input 2", "expected_output": "out 2"},
    ]
    cases = DatasetLoader.load_from_data(data)
    assert len(cases) == 2
    assert cases[0].id == "c1"
    assert cases[1].expected_output == "out 2"


def test_load_missing_file() -> None:
    """Test that missing file raises DatasetLoadError."""
    with pytest.raises(DatasetLoadError, match="Dataset file not found"):
        DatasetLoader.load_from_file("non_existent_file.json")


def test_load_malformed_json(tmp_path) -> None:
    """Test that malformed JSON raises DatasetLoadError."""
    file_path = tmp_path / "bad.json"
    file_path.write_text("{ not valid json }", encoding="utf-8")

    with pytest.raises(DatasetLoadError, match="Invalid JSON"):
        DatasetLoader.load_from_file(file_path)


def test_load_invalid_case_schema() -> None:
    """Test that invalid item schema raises DatasetLoadError."""
    data = [{"id": "c1"}]  # Missing required field 'input'
    with pytest.raises(DatasetLoadError, match="Validation failed"):
        DatasetLoader.load_from_data(data)
