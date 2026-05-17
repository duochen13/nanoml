import pytest
from pathlib import Path
from nanoml.core.config_loader import ConfigLoader, ConfigValidationError


def test_load_valid_config():
    """Should successfully load and validate a valid config."""
    config_path = Path(__file__).parent / "fixtures" / "valid_config.yaml"
    loader = ConfigLoader()
    config = loader.load(config_path)

    assert config["environment"] == "local"
    assert config["project"]["name"] == "test-project"


def test_load_invalid_config():
    """Should raise ConfigValidationError for invalid config."""
    config_path = Path(__file__).parent / "fixtures" / "invalid_config.yaml"
    loader = ConfigLoader()

    with pytest.raises(ConfigValidationError) as exc_info:
        loader.load(config_path)

    assert "environment" in str(exc_info.value).lower()


def test_load_nonexistent_config():
    """Should raise FileNotFoundError for missing config."""
    loader = ConfigLoader()

    with pytest.raises(FileNotFoundError):
        loader.load(Path("nonexistent.yaml"))
