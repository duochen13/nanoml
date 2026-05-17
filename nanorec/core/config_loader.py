"""Configuration loading and validation."""

import yaml
from pathlib import Path
from typing import Dict, Any
from jsonschema import validate, ValidationError
from nanorec.core.schema import CONFIG_SCHEMA


class ConfigValidationError(Exception):
    """Raised when config validation fails."""
    pass


class ConfigLoader:
    """Loads and validates NanoRec configuration files."""

    def load(self, config_path: Path) -> Dict[str, Any]:
        """
        Load and validate a config.yaml file.

        Args:
            config_path: Path to config.yaml

        Returns:
            Validated configuration dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
            ConfigValidationError: If config is invalid
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        # Load YAML
        with open(config_path) as f:
            config = yaml.safe_load(f)

        # Validate against schema
        try:
            validate(instance=config, schema=CONFIG_SCHEMA)
        except ValidationError as e:
            raise ConfigValidationError(
                f"Invalid configuration: {e.message}\n"
                f"Path: {' -> '.join(str(p) for p in e.path)}"
            ) from e

        return config
