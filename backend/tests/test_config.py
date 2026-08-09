from app.core.config import settings


def test_settings_load_defaults() -> None:
    """Test that application configuration loads default attributes correctly."""
    assert settings.APP_NAME == "Probenest"
    assert isinstance(settings.DEBUG, bool)
    assert settings.API_PORT == 8000
    assert "sqlite" in settings.DATABASE_URL
