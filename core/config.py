from pathlib import Path
from typing import Any
import yaml


class Config:
    """NanoML project configuration."""

    def __init__(self, data: dict[str, Any]):
        self.name = data.get("name", "nanoml_project")
        self.version = data.get("version", "0.1.0")
        self.description = data.get("description", "")
        self._data = data

    def __getattr__(self, name: str) -> Any:
        """Allow attribute access to config data."""
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"Config has no attribute '{name}'")


def load_config(config_path: Path) -> Config:
    """Load NanoML configuration from nanoml.yaml.

    Args:
        config_path: Path to nanoml.yaml

    Returns:
        Config object
    """
    with open(config_path) as f:
        data = yaml.safe_load(f)
    return Config(data)
