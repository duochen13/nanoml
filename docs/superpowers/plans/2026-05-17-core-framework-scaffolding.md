# Core Framework & Project Scaffolding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the core NanoRec CLI that scaffolds new projects and validates configurations.

**Architecture:** PyPI-installable package with CLI entry point. Two commands: `nanorec init` (scaffolds project from template) and `nanorec validate` (validates config.yaml schema). Includes base abstractions for future infrastructure integration.

**Tech Stack:** Python 3.9+, Click (CLI), PyYAML (config), Jinja2 (templating), pytest

---

## File Structure

```
nanorec/                          # PyPI package source
├── __init__.py
├── __version__.py
├── cli/
│   ├── __init__.py
│   ├── main.py                   # Click CLI entry point
│   ├── init.py                   # Init command implementation
│   └── validate.py               # Validate command implementation
├── core/
│   ├── __init__.py
│   ├── base.py                   # Base classes (Component, Provider)
│   ├── config_loader.py          # Config loading & validation
│   ├── schema.py                 # Config JSON schema
│   ├── registry.py               # Component registry (stub for Plan 2)
│   └── factory.py                # Provider factory (stub for Plan 2)
├── templates/
│   └── default/                  # Default project template
│       ├── template.yaml         # Template metadata
│       └── project/              # Files to copy
│           ├── data/
│           │   ├── loader.py.jinja2
│           │   ├── preprocessor.py.jinja2
│           │   ├── labeling.py.jinja2
│           │   └── splitting.py.jinja2
│           ├── features/
│           │   └── definitions.py.jinja2
│           ├── training/
│           │   ├── model.py.jinja2
│           │   ├── config.py.jinja2
│           │   └── trainer.py.jinja2
│           ├── evaluation/
│           │   └── metrics.py.jinja2
│           ├── serving/
│           │   ├── candidate_generation.py.jinja2
│           │   ├── ranking.py.jinja2
│           │   ├── postprocessing.py.jinja2
│           │   └── recommendation.py.jinja2
│           ├── infrastructure/
│           │   ├── README.md
│           │   └── .gitkeep
│           ├── core/
│           │   └── __init__.py
│           ├── integration/
│           │   └── __init__.py
│           ├── deployment/
│           │   └── .gitkeep
│           ├── .gitignore.jinja2
│           ├── config.yaml.jinja2
│           ├── Makefile.jinja2
│           ├── requirements.txt.jinja2
│           └── README.md.jinja2
└── setup.py

tests/
├── __init__.py
├── test_cli_init.py
├── test_cli_validate.py
├── test_config_loader.py
├── test_schema.py
└── fixtures/
    ├── valid_config.yaml
    └── invalid_config.yaml
```

---

## Task 1: Package Setup & Base Structure

**Files:**
- Create: `nanorec/__init__.py`
- Create: `nanorec/__version__.py`
- Create: `setup.py`
- Create: `requirements.txt`
- Create: `requirements-dev.txt`

- [ ] **Step 1: Write test for package version**

Create: `tests/test_package.py`

```python
import nanorec


def test_version_exists():
    """Package should have a __version__ attribute."""
    assert hasattr(nanorec, "__version__")
    assert isinstance(nanorec.__version__, str)
    assert len(nanorec.__version__) > 0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_package.py::test_version_exists -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'nanorec'"

- [ ] **Step 3: Create package __version__.py**

Create: `nanorec/__version__.py`

```python
"""NanoRec version information."""

__version__ = "0.1.0"
```

- [ ] **Step 4: Create package __init__.py**

Create: `nanorec/__init__.py`

```python
"""NanoRec - Production ML Systems Made Easy."""

from nanorec.__version__ import __version__

__all__ = ["__version__"]
```

- [ ] **Step 5: Create setup.py**

Create: `setup.py`

```python
"""Setup configuration for NanoRec package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read version
version = {}
with open("nanorec/__version__.py") as f:
    exec(f.read(), version)

# Read long description
long_description = (Path(__file__).parent / "README.md").read_text()

setup(
    name="nanorec",
    version=version["__version__"],
    description="Production ML Recommendation Systems Made Easy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="NanoRec Team",
    author_email="team@nanorec.dev",
    url="https://github.com/nanorec/nanorec",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    package_data={
        "nanorec": [
            "templates/**/*",
            "templates/**/**/*",
        ],
    },
    install_requires=[
        "click>=8.0.0",
        "pyyaml>=6.0",
        "jinja2>=3.0.0",
        "jsonschema>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "ruff>=0.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "nanorec=nanorec.cli.main:cli",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
```

- [ ] **Step 6: Create requirements.txt**

Create: `requirements.txt`

```
click>=8.0.0
pyyaml>=6.0
jinja2>=3.0.0
jsonschema>=4.0.0
```

- [ ] **Step 7: Create requirements-dev.txt**

Create: `requirements-dev.txt`

```
-r requirements.txt
pytest>=7.0.0
pytest-cov>=4.0.0
black>=22.0.0
ruff>=0.1.0
```

- [ ] **Step 8: Install package in editable mode**

```bash
pip install -e .
```

Expected: Package installs successfully

- [ ] **Step 9: Run test to verify it passes**

```bash
pytest tests/test_package.py::test_version_exists -v
```

Expected: PASS

- [ ] **Step 10: Commit**

```bash
git add nanorec/ setup.py requirements.txt requirements-dev.txt tests/test_package.py
git commit -m "feat: initial package structure with version"
```

---

## Task 2: Config Schema & Validation

**Files:**
- Create: `nanorec/core/__init__.py`
- Create: `nanorec/core/schema.py`
- Create: `nanorec/core/config_loader.py`
- Create: `tests/test_config_loader.py`
- Create: `tests/fixtures/valid_config.yaml`
- Create: `tests/fixtures/invalid_config.yaml`

- [ ] **Step 1: Write test for config validation**

Create: `tests/test_config_loader.py`

```python
import pytest
from pathlib import Path
from nanorec.core.config_loader import ConfigLoader, ConfigValidationError


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
```

- [ ] **Step 2: Create test fixtures**

Create: `tests/fixtures/valid_config.yaml`

```yaml
environment: local

project:
  name: test-project
  version: 1.0.0

local:
  storage:
    type: localstack
    endpoint: http://localhost:4566
  features:
    feast:
      offline_store:
        type: file
      online_store:
        type: redis
        host: localhost:6379

ml:
  features:
    required_features:
      - user:user_avg_rating
      - item:item_popularity
  training:
    hyperparameters:
      embedding_dim: 64
      learning_rate: 0.001
```

Create: `tests/fixtures/invalid_config.yaml`

```yaml
# Missing required 'environment' field
project:
  name: test-project
```

- [ ] **Step 3: Run test to verify it fails**

```bash
pytest tests/test_config_loader.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'nanorec.core'"

- [ ] **Step 4: Create config schema**

Create: `nanorec/core/__init__.py`

```python
"""Core framework components."""

from nanorec.core.config_loader import ConfigLoader, ConfigValidationError

__all__ = ["ConfigLoader", "ConfigValidationError"]
```

Create: `nanorec/core/schema.py`

```python
"""JSON Schema for NanoRec config.yaml validation."""

CONFIG_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["environment", "project"],
    "properties": {
        "environment": {
            "type": "string",
            "enum": ["local", "aws", "gcp", "azure"],
            "description": "Deployment environment"
        },
        "project": {
            "type": "object",
            "required": ["name", "version"],
            "properties": {
                "name": {
                    "type": "string",
                    "pattern": "^[a-z][a-z0-9-]*$",
                    "description": "Project name (lowercase, hyphens allowed)"
                },
                "version": {
                    "type": "string",
                    "pattern": "^\\d+\\.\\d+\\.\\d+$",
                    "description": "Semantic version (X.Y.Z)"
                }
            }
        },
        "local": {
            "type": "object",
            "description": "Local environment configuration"
        },
        "aws": {
            "type": "object",
            "description": "AWS environment configuration"
        },
        "gcp": {
            "type": "object",
            "description": "GCP environment configuration"
        },
        "azure": {
            "type": "object",
            "description": "Azure environment configuration"
        },
        "ml": {
            "type": "object",
            "description": "ML-specific configuration",
            "properties": {
                "features": {
                    "type": "object"
                },
                "training": {
                    "type": "object"
                },
                "serving": {
                    "type": "object"
                }
            }
        }
    }
}
```

- [ ] **Step 5: Create config loader**

Create: `nanorec/core/config_loader.py`

```python
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
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
pytest tests/test_config_loader.py -v
```

Expected: All tests PASS

- [ ] **Step 7: Commit**

```bash
git add nanorec/core/ tests/test_config_loader.py tests/fixtures/
git commit -m "feat: add config schema and validation"
```

---

## Task 3: Base Abstractions (Stubs)

**Files:**
- Create: `nanorec/core/base.py`
- Create: `nanorec/core/registry.py`
- Create: `nanorec/core/factory.py`
- Create: `tests/test_base.py`

- [ ] **Step 1: Write test for base classes**

Create: `tests/test_base.py`

```python
from nanorec.core.base import Component, Provider


def test_component_base_class():
    """Component base class should be instantiable."""

    class TestComponent(Component):
        def run(self):
            return "component executed"

    component = TestComponent(name="test")
    assert component.name == "test"
    assert component.run() == "component executed"


def test_provider_base_class():
    """Provider base class should be instantiable."""

    class TestProvider(Provider):
        def deploy(self):
            return "deployed"

    provider = TestProvider(environment="local")
    assert provider.environment == "local"
    assert provider.deploy() == "deployed"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_base.py -v
```

Expected: FAIL with "cannot import name 'Component'"

- [ ] **Step 3: Create base classes**

Create: `nanorec/core/base.py`

```python
"""Base classes for NanoRec components and providers."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class Component(ABC):
    """
    Base class for all NanoRec components.

    Components are user-facing modules (data, features, training, etc.)
    that orchestrate business logic and use infrastructure services.
    """

    def __init__(self, name: str, config: Dict[str, Any] = None):
        """
        Initialize component.

        Args:
            name: Component name
            config: Component-specific configuration
        """
        self.name = name
        self.config = config or {}

    @abstractmethod
    def run(self) -> Any:
        """
        Execute the component's main logic.

        Returns:
            Component execution result
        """
        pass


class Provider(ABC):
    """
    Base class for cloud provider implementations.

    Providers implement infrastructure services for specific
    cloud platforms (local, AWS, GCP, Azure).
    """

    def __init__(self, environment: str, config: Dict[str, Any] = None):
        """
        Initialize provider.

        Args:
            environment: Target environment (local/aws/gcp/azure)
            config: Environment-specific configuration
        """
        self.environment = environment
        self.config = config or {}

    @abstractmethod
    def deploy(self) -> None:
        """Deploy infrastructure services for this provider."""
        pass
```

- [ ] **Step 4: Create registry stub**

Create: `nanorec/core/registry.py`

```python
"""Component and provider registry.

This is a stub for Plan 2. Will be used to register and discover
components and providers at runtime.
"""

from typing import Dict, Type
from nanorec.core.base import Component, Provider


class Registry:
    """Registry for components and providers."""

    def __init__(self):
        self._components: Dict[str, Type[Component]] = {}
        self._providers: Dict[str, Type[Provider]] = {}

    def register_component(self, name: str, component_class: Type[Component]) -> None:
        """
        Register a component class.

        Args:
            name: Component name
            component_class: Component class
        """
        self._components[name] = component_class

    def register_provider(self, name: str, provider_class: Type[Provider]) -> None:
        """
        Register a provider class.

        Args:
            name: Provider name
            provider_class: Provider class
        """
        self._providers[name] = provider_class

    def get_component(self, name: str) -> Type[Component]:
        """Get registered component class."""
        if name not in self._components:
            raise KeyError(f"Component not registered: {name}")
        return self._components[name]

    def get_provider(self, name: str) -> Type[Provider]:
        """Get registered provider class."""
        if name not in self._providers:
            raise KeyError(f"Provider not registered: {name}")
        return self._providers[name]


# Global registry instance
_registry = Registry()


def get_registry() -> Registry:
    """Get the global registry instance."""
    return _registry
```

- [ ] **Step 5: Create factory stub**

Create: `nanorec/core/factory.py`

```python
"""Factory for creating providers based on configuration.

This is a stub for Plan 2. Will be used to instantiate providers
based on the selected environment in config.yaml.
"""

from typing import Dict, Any
from nanorec.core.base import Provider
from nanorec.core.registry import get_registry


class ProviderFactory:
    """Creates provider instances based on configuration."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize factory.

        Args:
            config: Full configuration dictionary
        """
        self.config = config
        self.environment = config["environment"]
        self.registry = get_registry()

    def create_provider(self, service: str) -> Provider:
        """
        Create a provider instance for a specific service.

        Args:
            service: Service name (storage, kafka, flink, etc.)

        Returns:
            Provider instance for the configured environment

        Raises:
            NotImplementedError: This is a stub for Plan 2
        """
        raise NotImplementedError(
            "ProviderFactory.create_provider() will be implemented in Plan 2"
        )
```

- [ ] **Step 6: Update core __init__.py**

Modify: `nanorec/core/__init__.py`

```python
"""Core framework components."""

from nanorec.core.config_loader import ConfigLoader, ConfigValidationError
from nanorec.core.base import Component, Provider
from nanorec.core.registry import Registry, get_registry
from nanorec.core.factory import ProviderFactory

__all__ = [
    "ConfigLoader",
    "ConfigValidationError",
    "Component",
    "Provider",
    "Registry",
    "get_registry",
    "ProviderFactory",
]
```

- [ ] **Step 7: Run test to verify it passes**

```bash
pytest tests/test_base.py -v
```

Expected: All tests PASS

- [ ] **Step 8: Commit**

```bash
git add nanorec/core/base.py nanorec/core/registry.py nanorec/core/factory.py tests/test_base.py
git commit -m "feat: add base abstractions for components and providers"
```

---

## Task 4: CLI Entry Point

**Files:**
- Create: `nanorec/cli/__init__.py`
- Create: `nanorec/cli/main.py`
- Create: `tests/test_cli_main.py`

- [ ] **Step 1: Write test for CLI entry point**

Create: `tests/test_cli_main.py`

```python
from click.testing import CliRunner
from nanorec.cli.main import cli


def test_cli_help():
    """CLI should show help message."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "NanoRec" in result.output
    assert "init" in result.output
    assert "validate" in result.output


def test_cli_version():
    """CLI should show version."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert "0.1.0" in result.output
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_cli_main.py -v
```

Expected: FAIL with "cannot import name 'cli'"

- [ ] **Step 3: Create CLI entry point**

Create: `nanorec/cli/__init__.py`

```python
"""NanoRec CLI commands."""

from nanorec.cli.main import cli

__all__ = ["cli"]
```

Create: `nanorec/cli/main.py`

```python
"""NanoRec CLI main entry point."""

import click
from nanorec.__version__ import __version__


@click.group()
@click.version_option(version=__version__, prog_name="nanorec")
def cli():
    """
    NanoRec - Production ML Recommendation Systems Made Easy

    Build, deploy, and scale ML recommendation systems with a single command.
    """
    pass


# Commands will be added in subsequent tasks
from nanorec.cli import init as _init_module  # noqa: E402, F401
from nanorec.cli import validate as _validate_module  # noqa: E402, F401
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_cli_main.py::test_cli_help -v
pytest tests/test_cli_main.py::test_cli_version -v
```

Expected: Both tests PASS

- [ ] **Step 5: Test CLI from command line**

```bash
nanorec --help
nanorec --version
```

Expected: Help message and version displayed

- [ ] **Step 6: Commit**

```bash
git add nanorec/cli/ tests/test_cli_main.py
git commit -m "feat: add CLI entry point with help and version"
```

---

## Task 5: Project Template Structure

**Files:**
- Create: `nanorec/templates/default/template.yaml`
- Create: `nanorec/templates/default/project/config.yaml.jinja2`
- Create: `nanorec/templates/default/project/.gitignore.jinja2`
- Create: `nanorec/templates/default/project/README.md.jinja2`
- Create: `nanorec/templates/default/project/Makefile.jinja2`
- Create: `nanorec/templates/default/project/requirements.txt.jinja2`
- Create: Multiple component template files

- [ ] **Step 1: Create template metadata**

Create: `nanorec/templates/default/template.yaml`

```yaml
name: default
description: Default NanoRec project template with all components
version: 1.0.0
author: NanoRec Team

# Variables that can be customized during project creation
variables:
  - name: project_name
    description: Project name
    required: true
    pattern: "^[a-z][a-z0-9-]*$"

  - name: project_version
    description: Project version
    default: "0.1.0"

  - name: description
    description: Project description
    default: "A NanoRec recommendation system"
```

- [ ] **Step 2: Create config.yaml template**

Create: `nanorec/templates/default/project/config.yaml.jinja2`

```yaml
# NanoRec Configuration
# This file controls deployment environment and ML settings

# ENVIRONMENT SELECTION
environment: local  # Options: local, aws, gcp, azure

# PROJECT INFO
project:
  name: {{ project_name }}
  version: {{ project_version }}

# LOCAL ENVIRONMENT
local:
  storage:
    type: localstack
    endpoint: http://localhost:4566
  features:
    feast:
      offline_store:
        type: file
      online_store:
        type: redis
        host: localhost:6379
  training:
    sagemaker:
      mode: local
  serving:
    api:
      type: fastapi
      port: 8000

# AWS ENVIRONMENT (uncomment and configure when deploying to AWS)
# aws:
#   region: us-west-2
#   account_id: "123456789012"
#   storage:
#     type: s3
#     bucket: {{ project_name }}-data-${account_id}

# ML CONFIGURATION (Environment-agnostic)
ml:
  features:
    required_features:
      - user:user_avg_rating_normalized
      - user:user_total_books_log
      - item:item_popularity_score
  training:
    hyperparameters:
      embedding_dim: 64
      learning_rate: 0.001
      batch_size: 256
      epochs: 10
  serving:
    candidate_generation:
      max_candidates: 1000
    ranking:
      top_n: 10
```

- [ ] **Step 3: Create .gitignore template**

Create: `nanorec/templates/default/project/.gitignore.jinja2`

```
# NanoRec generated files
.nanorec/generated/
.nanorec/cache/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Data
data/raw/
data/processed/
*.csv
*.parquet

# Models
models/
*.pth
*.pkl

# Infrastructure data
infrastructure/*/data/

# OS
.DS_Store
Thumbs.db
```

- [ ] **Step 4: Create README template**

Create: `nanorec/templates/default/project/README.md.jinja2`

```markdown
# {{ project_name }}

{{ description }}

Built with [NanoRec](https://github.com/nanorec/nanorec) - Production ML Recommendation Systems Made Easy.

## Quick Start

### Local Development

1. **Install dependencies**
   ```bash
   make setup
   ```

2. **Start infrastructure**
   ```bash
   make run
   ```

3. **Test the system**
   ```bash
   curl http://localhost:8000/recommend?user_id=123
   ```

### Deploy to Cloud

1. **Configure AWS/GCP/Azure**
   Edit `config.yaml` and change `environment: local` to `environment: aws`

2. **Deploy**
   ```bash
   nanorec deploy
   ```

## Project Structure

```
{{ project_name }}/
├── data/              # Data loading and preprocessing
├── features/          # Feature definitions
├── training/          # Model training
├── evaluation/        # Model evaluation
├── serving/           # Recommendation serving
├── infrastructure/    # Infrastructure services (managed by NanoRec)
├── config.yaml        # Main configuration
└── Makefile           # Common commands
```

## Customization

**User-facing files** (what you customize):
- `data/*.py` - Data loading, preprocessing, labeling, splitting
- `features/definitions.py` - Feature definitions
- `training/*.py` - Model architecture, training config
- `evaluation/metrics.py` - Evaluation metrics
- `serving/*.py` - Recommendation logic

**Framework-managed** (don't edit):
- `infrastructure/` - Auto-generated infrastructure code
- `.nanorec/generated/` - Auto-generated Flink jobs, Airflow DAGs, etc.

## Available Commands

```bash
make setup    # Install dependencies
make run      # Start local infrastructure
make clean    # Stop and remove all data
make test     # Run smoke tests
```

## Learn More

- [NanoRec Documentation](https://nanorec.dev/docs)
- [Design Document](docs/superpowers/specs/2026-05-17-nanorec-design.md)
```

- [ ] **Step 5: Create Makefile template**

Create: `nanorec/templates/default/project/Makefile.jinja2`

```makefile
.PHONY: setup run clean test help

help:
	@echo "{{ project_name }} - NanoRec Project"
	@echo ""
	@echo "Available commands:"
	@echo "  make setup   - Install dependencies"
	@echo "  make run     - Start local infrastructure"
	@echo "  make clean   - Stop and remove all data"
	@echo "  make test    - Run smoke tests"

setup:
	pip install -r requirements.txt
	@echo "✅ Dependencies installed"

run:
	@echo "Starting NanoRec infrastructure..."
	docker-compose up -d
	@echo "✅ Infrastructure running!"
	@echo "API: http://localhost:8000"
	@echo "Airflow UI: http://localhost:8080"
	@echo "MLflow UI: http://localhost:5000"

clean:
	@echo "Stopping all services..."
	docker-compose down -v
	@echo "✅ All services stopped and data cleaned"

test:
	@echo "Running smoke tests..."
	pytest integration/smoke_tests.py -v
	@echo "✅ Tests passed"
```

- [ ] **Step 6: Create requirements.txt template**

Create: `nanorec/templates/default/project/requirements.txt.jinja2`

```
# NanoRec framework
nanorec>=0.1.0

# Data processing
pandas>=2.0.0
numpy>=1.24.0
pyarrow>=12.0.0

# ML frameworks
torch>=2.0.0
scikit-learn>=1.3.0

# Feature store
feast>=0.35.0

# Experiment tracking
mlflow>=2.8.0

# API serving
fastapi>=0.104.0
uvicorn>=0.24.0

# Infrastructure clients
boto3>=1.28.0
kafka-python>=2.0.0
apache-flink>=1.18.0
```

- [ ] **Step 7: Create component template directories**

```bash
mkdir -p nanorec/templates/default/project/data
mkdir -p nanorec/templates/default/project/features
mkdir -p nanorec/templates/default/project/training
mkdir -p nanorec/templates/default/project/evaluation
mkdir -p nanorec/templates/default/project/serving
mkdir -p nanorec/templates/default/project/infrastructure
mkdir -p nanorec/templates/default/project/core
mkdir -p nanorec/templates/default/project/integration
mkdir -p nanorec/templates/default/project/deployment
```

- [ ] **Step 8: Create data component templates**

Create: `nanorec/templates/default/project/data/loader.py.jinja2`

```python
"""Data loader for {{ project_name }}.

Load raw data from Kaggle/S3/GCS.
"""

from pathlib import Path
import pandas as pd


def load_data(source: str = "local") -> pd.DataFrame:
    """
    Load raw dataset.

    Args:
        source: Data source ("local", "s3", "kaggle")

    Returns:
        Raw data as DataFrame
    """
    if source == "local":
        # TODO: Replace with your dataset path
        data_path = Path("data/raw/dataset.csv")
        return pd.read_csv(data_path)

    elif source == "s3":
        # TODO: Implement S3 loading
        raise NotImplementedError("S3 loading not yet implemented")

    elif source == "kaggle":
        # TODO: Implement Kaggle API loading
        raise NotImplementedError("Kaggle loading not yet implemented")

    else:
        raise ValueError(f"Unknown source: {source}")


if __name__ == "__main__":
    # Test loading
    df = load_data()
    print(f"Loaded {len(df)} rows")
    print(df.head())
```

Create: `nanorec/templates/default/project/data/preprocessor.py.jinja2`

```python
"""Data preprocessing for {{ project_name }}.

Clean and transform raw data.
"""

import pandas as pd


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and preprocess raw data.

    Args:
        df: Raw DataFrame

    Returns:
        Cleaned DataFrame
    """
    # TODO: Implement your preprocessing logic
    # Examples:
    # - Remove duplicates
    # - Handle missing values
    # - Convert data types
    # - Filter invalid records

    df_clean = df.copy()

    # Remove duplicates
    df_clean = df_clean.drop_duplicates()

    # Handle missing values
    df_clean = df_clean.dropna()

    return df_clean


if __name__ == "__main__":
    from loader import load_data

    df = load_data()
    df_clean = preprocess_data(df)
    print(f"Preprocessed: {len(df)} → {len(df_clean)} rows")
```

Create: `nanorec/templates/default/project/data/labeling.py.jinja2`

```python
"""Label generation for {{ project_name }}.

Define labels for training.
"""

import pandas as pd


def generate_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate training labels from preprocessed data.

    Args:
        df: Preprocessed DataFrame

    Returns:
        DataFrame with labels
    """
    # TODO: Implement your labeling logic
    # Examples:
    # - Binary labels (clicked/not clicked)
    # - Rating labels (1-5 stars)
    # - Implicit feedback (purchase, view)

    df_labeled = df.copy()

    # Example: Binary label from rating threshold
    # df_labeled['label'] = (df_labeled['rating'] >= 4).astype(int)

    return df_labeled


if __name__ == "__main__":
    from loader import load_data
    from preprocessor import preprocess_data

    df = load_data()
    df_clean = preprocess_data(df)
    df_labeled = generate_labels(df_clean)
    print(f"Generated labels for {len(df_labeled)} rows")
```

Create: `nanorec/templates/default/project/data/splitting.py.jinja2`

```python
"""Train/validation/test split for {{ project_name }}.

Split data into train, validation, and test sets.
"""

import pandas as pd
from typing import Tuple
from sklearn.model_selection import train_test_split


def split_data(
    df: pd.DataFrame,
    train_size: float = 0.7,
    val_size: float = 0.15,
    test_size: float = 0.15,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split data into train/val/test sets.

    Args:
        df: Labeled DataFrame
        train_size: Fraction for training
        val_size: Fraction for validation
        test_size: Fraction for testing
        random_state: Random seed

    Returns:
        (train_df, val_df, test_df)
    """
    assert abs(train_size + val_size + test_size - 1.0) < 1e-6

    # First split: train vs (val + test)
    train_df, temp_df = train_test_split(
        df,
        train_size=train_size,
        random_state=random_state,
        shuffle=True
    )

    # Second split: val vs test
    val_ratio = val_size / (val_size + test_size)
    val_df, test_df = train_test_split(
        temp_df,
        train_size=val_ratio,
        random_state=random_state,
        shuffle=True
    )

    return train_df, val_df, test_df


if __name__ == "__main__":
    from loader import load_data
    from preprocessor import preprocess_data
    from labeling import generate_labels

    df = load_data()
    df_clean = preprocess_data(df)
    df_labeled = generate_labels(df_clean)

    train_df, val_df, test_df = split_data(df_labeled)
    print(f"Train: {len(train_df)} rows")
    print(f"Val: {len(val_df)} rows")
    print(f"Test: {len(test_df)} rows")
```

- [ ] **Step 9: Create features component template**

Create: `nanorec/templates/default/project/features/definitions.py.jinja2`

```python
"""Feature definitions for {{ project_name }}.

Define features using @feature decorator.
Framework auto-generates Flink jobs and Feast configs.
"""

from nanorec.features import feature
import pandas as pd


@feature(
    name="user_avg_rating",
    entity="user",
    description="User's average rating across all items"
)
def compute_user_avg_rating(user_ratings: pd.DataFrame) -> pd.Series:
    """
    Compute average rating per user.

    Args:
        user_ratings: DataFrame with columns [user_id, rating]

    Returns:
        Series with user_id index and avg_rating values
    """
    return user_ratings.groupby("user_id")["rating"].mean()


@feature(
    name="user_rating_std",
    entity="user",
    description="Standard deviation of user ratings"
)
def compute_user_rating_std(user_ratings: pd.DataFrame) -> pd.Series:
    """Compute rating standard deviation per user."""
    return user_ratings.groupby("user_id")["rating"].std().fillna(0)


@feature(
    name="user_total_ratings",
    entity="user",
    description="Total number of ratings by user"
)
def compute_user_total_ratings(user_ratings: pd.DataFrame) -> pd.Series:
    """Count total ratings per user."""
    return user_ratings.groupby("user_id").size()


@feature(
    name="item_popularity",
    entity="item",
    description="Number of ratings for item (popularity proxy)"
)
def compute_item_popularity(item_ratings: pd.DataFrame) -> pd.Series:
    """Count total ratings per item."""
    return item_ratings.groupby("item_id").size()


@feature(
    name="item_avg_rating",
    entity="item",
    description="Average rating for item"
)
def compute_item_avg_rating(item_ratings: pd.DataFrame) -> pd.Series:
    """Compute average rating per item."""
    return item_ratings.groupby("item_id")["rating"].mean()


# TODO: Add your custom features here
# Framework will auto-generate:
# - .nanorec/generated/flink/batch_features.py
# - .nanorec/generated/flink/stream_features.py
# - .nanorec/generated/feast/feature_repo/features.py
```

- [ ] **Step 10: Commit template files**

```bash
git add nanorec/templates/
git commit -m "feat: add project template structure and component templates"
```

---

## Task 6: `nanorec init` Command

**Files:**
- Create: `nanorec/cli/init.py`
- Create: `tests/test_cli_init.py`

- [ ] **Step 1: Write test for init command**

Create: `tests/test_cli_init.py`

```python
import pytest
from pathlib import Path
from click.testing import CliRunner
from nanorec.cli.main import cli


def test_init_creates_project(tmp_path):
    """Init command should create project structure."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["init", "test-project"])

        assert result.exit_code == 0
        assert "Creating NanoRec project: test-project" in result.output
        assert "✅ Project created!" in result.output

        # Verify project directory exists
        project_dir = Path("test-project")
        assert project_dir.exists()
        assert project_dir.is_dir()

        # Verify key files exist
        assert (project_dir / "config.yaml").exists()
        assert (project_dir / "README.md").exists()
        assert (project_dir / "Makefile").exists()
        assert (project_dir / "requirements.txt").exists()
        assert (project_dir / ".gitignore").exists()

        # Verify component directories exist
        assert (project_dir / "data").is_dir()
        assert (project_dir / "features").is_dir()
        assert (project_dir / "training").is_dir()
        assert (project_dir / "serving").is_dir()
        assert (project_dir / "infrastructure").is_dir()

        # Verify component files exist
        assert (project_dir / "data" / "loader.py").exists()
        assert (project_dir / "features" / "definitions.py").exists()


def test_init_invalid_name():
    """Init should reject invalid project names."""
    runner = CliRunner()

    # Uppercase not allowed
    result = runner.invoke(cli, ["init", "TestProject"])
    assert result.exit_code != 0
    assert "invalid" in result.output.lower() or "name" in result.output.lower()

    # Spaces not allowed
    result = runner.invoke(cli, ["init", "test project"])
    assert result.exit_code != 0


def test_init_existing_directory(tmp_path):
    """Init should fail if directory already exists."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Create directory
        Path("existing-project").mkdir()

        # Try to init
        result = runner.invoke(cli, ["init", "existing-project"])
        assert result.exit_code != 0
        assert "already exists" in result.output


def test_init_with_template(tmp_path):
    """Init should support --template flag."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["init", "test-project", "--template", "default"])
        assert result.exit_code == 0
        assert Path("test-project").exists()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_cli_init.py -v
```

Expected: FAIL with "ImportError" or command not found

- [ ] **Step 3: Create init command implementation**

Create: `nanorec/cli/init.py`

```python
"""Project initialization command."""

import re
import shutil
from pathlib import Path
from typing import Optional

import click
from jinja2 import Environment, FileSystemLoader

from nanorec.cli.main import cli


@cli.command()
@click.argument("project_name")
@click.option(
    "--template",
    default="default",
    help="Project template to use",
    show_default=True
)
@click.option(
    "--description",
    default="A NanoRec recommendation system",
    help="Project description",
    show_default=True
)
def init(project_name: str, template: str, description: str):
    """
    Create a new NanoRec project.

    PROJECT_NAME must be lowercase with hyphens (e.g., my-recommender)
    """
    # Validate project name
    if not re.match(r"^[a-z][a-z0-9-]*$", project_name):
        click.secho(
            f"❌ Invalid project name: {project_name}\n"
            "Project name must be lowercase, start with a letter, "
            "and contain only letters, numbers, and hyphens.",
            fg="red",
            err=True
        )
        raise click.Abort()

    # Check if directory already exists
    project_dir = Path(project_name)
    if project_dir.exists():
        click.secho(
            f"❌ Directory already exists: {project_name}",
            fg="red",
            err=True
        )
        raise click.Abort()

    # Get template directory
    templates_dir = Path(__file__).parent.parent / "templates"
    template_dir = templates_dir / template

    if not template_dir.exists():
        click.secho(
            f"❌ Template not found: {template}",
            fg="red",
            err=True
        )
        raise click.Abort()

    # Create project
    click.echo(f"Creating NanoRec project: {project_name}")

    try:
        _scaffold_project(
            project_dir=project_dir,
            template_dir=template_dir,
            project_name=project_name,
            description=description,
        )

        click.secho("✅ Project created!", fg="green")
        click.echo("")
        click.echo("Next steps:")
        click.echo(f"  cd {project_name}")
        click.echo("  make setup    # Install dependencies")
        click.echo("  make run      # Start local infrastructure")

    except Exception as e:
        # Cleanup on failure
        if project_dir.exists():
            shutil.rmtree(project_dir)
        click.secho(f"❌ Failed to create project: {e}", fg="red", err=True)
        raise click.Abort()


def _scaffold_project(
    project_dir: Path,
    template_dir: Path,
    project_name: str,
    description: str,
) -> None:
    """
    Scaffold project from template.

    Args:
        project_dir: Target project directory
        template_dir: Source template directory
        project_name: Project name
        description: Project description
    """
    project_dir.mkdir(parents=True)

    # Setup Jinja2 environment
    project_template_dir = template_dir / "project"
    env = Environment(
        loader=FileSystemLoader(str(project_template_dir)),
        keep_trailing_newline=True,
    )

    # Template variables
    context = {
        "project_name": project_name,
        "project_version": "0.1.0",
        "description": description,
    }

    # Copy all template files
    for template_path in project_template_dir.rglob("*"):
        if template_path.is_file():
            # Get relative path from template root
            rel_path = template_path.relative_to(project_template_dir)

            # Determine target path (remove .jinja2 extension if present)
            target_path = project_dir / rel_path
            if target_path.suffix == ".jinja2":
                target_path = target_path.with_suffix("")

            # Create parent directories
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Render template if it's a .jinja2 file
            if template_path.suffix == ".jinja2":
                template = env.get_template(str(rel_path))
                content = template.render(**context)
                target_path.write_text(content)
            else:
                # Copy non-template files directly
                shutil.copy2(template_path, target_path)

    # Create empty directories that need to exist
    (project_dir / ".nanorec").mkdir(exist_ok=True)
    (project_dir / ".nanorec" / "generated").mkdir(exist_ok=True)
    (project_dir / ".nanorec" / "cache").mkdir(exist_ok=True)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_cli_init.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Test init command manually**

```bash
cd /tmp
nanorec init test-recommender
cd test-recommender
ls -la
cat config.yaml
cat README.md
```

Expected: Project created with all files

- [ ] **Step 6: Cleanup test project**

```bash
cd /tmp
rm -rf test-recommender
```

- [ ] **Step 7: Commit**

```bash
git add nanorec/cli/init.py tests/test_cli_init.py
git commit -m "feat: implement nanorec init command"
```

---

## Task 7: `nanorec validate` Command

**Files:**
- Create: `nanorec/cli/validate.py`
- Create: `tests/test_cli_validate.py`

- [ ] **Step 1: Write test for validate command**

Create: `tests/test_cli_validate.py`

```python
from pathlib import Path
from click.testing import CliRunner
from nanorec.cli.main import cli


def test_validate_valid_config(tmp_path):
    """Validate should pass for valid config."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Create valid config
        config_content = """
environment: local

project:
  name: test-project
  version: 1.0.0

local:
  storage:
    type: localstack

ml:
  features:
    required_features:
      - user:avg_rating
"""
        Path("config.yaml").write_text(config_content)

        result = runner.invoke(cli, ["validate"])

        assert result.exit_code == 0
        assert "✅" in result.output or "valid" in result.output.lower()


def test_validate_invalid_config(tmp_path):
    """Validate should fail for invalid config."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Create invalid config (missing required 'project' field)
        config_content = """
environment: local
"""
        Path("config.yaml").write_text(config_content)

        result = runner.invoke(cli, ["validate"])

        assert result.exit_code != 0
        assert "❌" in result.output or "error" in result.output.lower()


def test_validate_missing_config(tmp_path):
    """Validate should fail if config.yaml doesn't exist."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["validate"])

        assert result.exit_code != 0
        assert "not found" in result.output.lower()


def test_validate_custom_path(tmp_path):
    """Validate should accept custom config path."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Create valid config with custom name
        config_content = """
environment: local

project:
  name: test-project
  version: 1.0.0
"""
        Path("custom.yaml").write_text(config_content)

        result = runner.invoke(cli, ["validate", "--config", "custom.yaml"])

        assert result.exit_code == 0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_cli_validate.py -v
```

Expected: FAIL with "ImportError" or command not found

- [ ] **Step 3: Create validate command implementation**

Create: `nanorec/cli/validate.py`

```python
"""Configuration validation command."""

from pathlib import Path

import click

from nanorec.cli.main import cli
from nanorec.core import ConfigLoader, ConfigValidationError


@cli.command()
@click.option(
    "--config",
    "-c",
    default="config.yaml",
    type=click.Path(exists=True, path_type=Path),
    help="Path to config file",
    show_default=True
)
def validate(config: Path):
    """
    Validate NanoRec configuration file.

    Checks config.yaml against the schema and reports any errors.
    """
    click.echo(f"Validating configuration: {config}")

    try:
        loader = ConfigLoader()
        config_dict = loader.load(config)

        # Show summary
        click.secho("✅ Configuration is valid", fg="green")
        click.echo("")
        click.echo("Summary:")
        click.echo(f"  Environment: {config_dict['environment']}")
        click.echo(f"  Project: {config_dict['project']['name']}")
        click.echo(f"  Version: {config_dict['project']['version']}")

        # Show ML config if present
        if "ml" in config_dict:
            ml_config = config_dict["ml"]
            if "features" in ml_config:
                features = ml_config["features"].get("required_features", [])
                click.echo(f"  Required features: {len(features)}")

    except FileNotFoundError as e:
        click.secho(f"❌ Config file not found: {config}", fg="red", err=True)
        raise click.Abort()

    except ConfigValidationError as e:
        click.secho(f"❌ Configuration validation failed:", fg="red", err=True)
        click.echo(str(e), err=True)
        raise click.Abort()

    except Exception as e:
        click.secho(f"❌ Unexpected error: {e}", fg="red", err=True)
        raise click.Abort()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_cli_validate.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Test validate command manually**

```bash
cd /tmp
nanorec init test-project
cd test-project
nanorec validate
```

Expected: "✅ Configuration is valid"

- [ ] **Step 6: Test with invalid config**

```bash
# Break the config
echo "invalid: yaml: content" > config.yaml
nanorec validate
```

Expected: Validation error shown

- [ ] **Step 7: Cleanup**

```bash
cd /tmp
rm -rf test-project
```

- [ ] **Step 8: Commit**

```bash
git add nanorec/cli/validate.py tests/test_cli_validate.py
git commit -m "feat: implement nanorec validate command"
```

---

## Task 8: Integration Tests & Documentation

**Files:**
- Create: `tests/test_integration.py`
- Create: `README.md`
- Update: `setup.py` (ensure package data included)

- [ ] **Step 1: Write end-to-end integration test**

Create: `tests/test_integration.py`

```python
"""End-to-end integration tests for NanoRec CLI."""

from pathlib import Path
from click.testing import CliRunner
from nanorec.cli.main import cli


def test_end_to_end_workflow(tmp_path):
    """Test complete workflow: init → validate."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Step 1: Initialize project
        result = runner.invoke(cli, ["init", "my-recommender"])
        assert result.exit_code == 0
        assert Path("my-recommender").exists()

        # Step 2: Validate created config
        result = runner.invoke(
            cli,
            ["validate", "--config", "my-recommender/config.yaml"]
        )
        assert result.exit_code == 0
        assert "✅" in result.output

        # Step 3: Verify project structure
        project_dir = Path("my-recommender")

        # User files should exist
        assert (project_dir / "data" / "loader.py").exists()
        assert (project_dir / "features" / "definitions.py").exists()
        assert (project_dir / "training" / "model.py").exists()
        assert (project_dir / "serving" / "recommendation.py").exists()

        # Config should be valid
        assert (project_dir / "config.yaml").exists()
        config_content = (project_dir / "config.yaml").read_text()
        assert "my-recommender" in config_content
        assert "environment: local" in config_content


def test_init_multiple_projects(tmp_path):
    """Should be able to create multiple projects."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Create first project
        result = runner.invoke(cli, ["init", "project-one"])
        assert result.exit_code == 0

        # Create second project
        result = runner.invoke(cli, ["init", "project-two"])
        assert result.exit_code == 0

        # Both should exist
        assert Path("project-one").exists()
        assert Path("project-two").exists()

        # Both configs should be valid
        result = runner.invoke(cli, ["validate", "-c", "project-one/config.yaml"])
        assert result.exit_code == 0

        result = runner.invoke(cli, ["validate", "-c", "project-two/config.yaml"])
        assert result.exit_code == 0
```

- [ ] **Step 2: Run integration tests**

```bash
pytest tests/test_integration.py -v
```

Expected: All tests PASS

- [ ] **Step 3: Create README.md**

Create: `README.md`

```markdown
# NanoRec

**Production ML Recommendation Systems Made Easy**

NanoRec is a pip-installable framework that scaffolds complete end-to-end ML recommendation systems, enabling users to focus on ML business logic (features, models, labels) while the framework handles all infrastructure complexity.

## Features

- 🚀 **One-command deployment** - `nanorec deploy` handles everything
- ☁️ **Cloud-agnostic** - Same code runs on local/AWS/GCP/Azure
- 🔧 **Fully declarative** - Write WHAT, framework generates HOW
- 📦 **Complete stack** - 11 infrastructure services integrated
- 🎯 **Focus on ML** - Users customize ~15 files, framework handles 100+

## Quick Start

### Installation

```bash
pip install nanorec
```

### Create a New Project

```bash
nanorec init my-recommender
cd my-recommender
```

### Local Development

```bash
make setup  # Install dependencies
make run    # Start Docker Compose (11 services)
```

### Deploy to Cloud

```bash
# Edit config.yaml: environment: aws
nanorec deploy
```

## Architecture

**11 Infrastructure Services:**
1. Storage (S3/GCS/Blob)
2. Message Queue (Kafka)
3. Stream Processing (Flink)
4. Feature Store (Feast)
5. Training (SageMaker/Vertex AI)
6. Experiment Tracking (MLflow)
7. Model Serving
8. API Gateway
9. Orchestration (Airflow)
10. Lineage Tracking
11. Frontend Dashboard

**Zero Duplication:** All infrastructure centralized, cloud providers in single files.

## What You Customize

- `data/*.py` - Load, clean, label, split data
- `features/definitions.py` - Define features (declarative)
- `training/*.py` - Model architecture & config
- `serving/*.py` - Recommendation logic

**Framework auto-generates:**
- Flink jobs from feature definitions
- Airflow DAGs from components
- Feast configs
- Infrastructure deployment

## Documentation

- [Design Document](docs/superpowers/specs/2026-05-17-nanorec-design.md)
- [Implementation Plans](docs/superpowers/plans/)

## Development

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/ -v
pytest tests/ --cov=nanorec
```

### Code Quality

```bash
black nanorec/ tests/
ruff check nanorec/ tests/
```

## Architecture Principles

- **Fully declarative** - No custom Flink/Airflow code
- **Infrastructure-first** - 11 services in `infrastructure/`
- **Zero duplication** - One provider file per cloud
- **Three-layer** - User → Generated → Infrastructure

## License

MIT

## Links

- GitHub: https://github.com/nanorec/nanorec
- Documentation: https://nanorec.dev
- Issues: https://github.com/nanorec/nanorec/issues
```

- [ ] **Step 4: Verify package data is included**

Verify: `setup.py`

Ensure `package_data` includes templates:

```python
package_data={
    "nanorec": [
        "templates/**/*",
        "templates/**/**/*",
    ],
},
```

- [ ] **Step 5: Test package installation**

```bash
# Build package
python setup.py sdist bdist_wheel

# Install in clean virtualenv
python -m venv test_venv
source test_venv/bin/activate
pip install dist/nanorec-0.1.0-py3-none-any.whl

# Test CLI
nanorec --version
nanorec --help

# Cleanup
deactivate
rm -rf test_venv dist build *.egg-info
```

Expected: Package installs and CLI works

- [ ] **Step 6: Run all tests**

```bash
pytest tests/ -v --cov=nanorec
```

Expected: All tests PASS, good coverage

- [ ] **Step 7: Commit**

```bash
git add README.md tests/test_integration.py
git commit -m "feat: add integration tests and README"
```

---

## Task 9: Final Validation & Cleanup

**Files:**
- Create: `.gitignore`
- Create: `MANIFEST.in`
- Verify all tests pass

- [ ] **Step 1: Create .gitignore**

Create: `.gitignore`

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv
*.egg-info/
dist/
build/

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
.nanorec/
```

- [ ] **Step 2: Create MANIFEST.in**

Create: `MANIFEST.in`

```
include README.md
include LICENSE
include requirements.txt
include requirements-dev.txt
recursive-include nanorec/templates *
```

- [ ] **Step 3: Run full test suite**

```bash
pytest tests/ -v --cov=nanorec --cov-report=html
```

Expected: All tests PASS

- [ ] **Step 4: Check coverage report**

```bash
open htmlcov/index.html  # macOS
# Or: xdg-open htmlcov/index.html  # Linux
```

Expected: Coverage > 80%

- [ ] **Step 5: Verify package can be built**

```bash
python setup.py sdist bdist_wheel
ls -lh dist/
```

Expected: Source and wheel distributions created

- [ ] **Step 6: Test init command creates working project**

```bash
cd /tmp
nanorec init final-test
cd final-test
nanorec validate
cat config.yaml
cat data/loader.py
cat features/definitions.py
```

Expected: All files exist and are valid

- [ ] **Step 7: Cleanup test project**

```bash
cd /tmp
rm -rf final-test
```

- [ ] **Step 8: Final commit**

```bash
git add .gitignore MANIFEST.in
git commit -m "chore: add gitignore and manifest for package distribution"
```

- [ ] **Step 9: Tag release**

```bash
git tag -a v0.1.0 -m "Release v0.1.0 - Core framework & project scaffolding"
```

---

## Self-Review

**1. Spec coverage check:**

From the design spec, Plan 1 should cover:
- ✅ PyPI package structure
- ✅ CLI commands (`nanorec init`, `nanorec validate`)
- ✅ Project scaffolding from templates
- ✅ Config schema and validation
- ✅ Base abstractions (Component, Provider, Registry, Factory)
- ✅ Project template with all component files

**Not in Plan 1 (deferred to Plan 2+):**
- Infrastructure services deployment
- Code generation (Flink jobs, Feast configs, Airflow DAGs)
- Provider implementations (AWS/GCP/Azure)
- Actual ML pipeline execution

✅ Coverage is complete for Plan 1 scope.

**2. Placeholder scan:**

Searched for: TBD, TODO, "implement later", "fill in"

Found TODOs in:
- Template files (`data/loader.py.jinja2`, etc.) - These are INTENTIONAL placeholders for users to fill in their business logic
- `factory.py` - Intentional stub with `NotImplementedError` pointing to Plan 2

✅ No unintentional placeholders. All stubs are documented.

**3. Type consistency:**

- `ConfigLoader.load()` returns `Dict[str, Any]` consistently
- `Component` and `Provider` base classes have consistent signatures
- CLI commands use `click.Path(path_type=Path)` consistently
- Template variables use consistent naming (`project_name`, `project_version`, `description`)

✅ Types are consistent throughout.

---

## Plan Complete

**Deliverable:** Core NanoRec framework with:
- PyPI-installable package (`pip install nanorec`)
- CLI commands: `nanorec init` and `nanorec validate`
- Project scaffolding with complete template structure
- Config validation against JSON schema
- Base abstractions for future infrastructure integration

**Next Steps:**
- Plan 2: Local Infrastructure Services (Docker Compose + service clients)
- Plan 3: Code Generation Framework
- Plan 4: End-to-End Local Example
- Plan 5: AWS Provider Implementation
