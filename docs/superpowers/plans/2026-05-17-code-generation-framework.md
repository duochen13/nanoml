# Code Generation Framework Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the code generation engine that transforms user definitions into executable Flink jobs, Feast configs, and Airflow DAGs.

**Architecture:** Template-based code generation with AST parsing for feature definitions. Generators read user code/config, apply Jinja2 templates, write to `.nanoml/generated/`.

**Tech Stack:** Python 3.9+, Jinja2 (templates), ast (Python AST parsing), PyYAML (config), pytest

---

## File Structure

**Code to create:**
- `generators/base.py` - Abstract base generator class
- `generators/flink_job.py` - Flink streaming job generator
- `generators/feast_config.py` - Feast feature store config generator
- `generators/airflow_dag.py` - Airflow DAG generator
- `generators/templates/flink_job.py.j2` - Flink job template
- `generators/templates/feast_store.yaml.j2` - Feast store template
- `generators/templates/feast_features.py.j2` - Feast feature definitions template
- `generators/templates/airflow_dag.py.j2` - Airflow DAG template
- `cli/generate.py` - `nanoml generate` command
- `core/generated_manager.py` - Manages `.nanoml/generated/` folder
- `tests/generators/test_base.py` - Base generator tests
- `tests/generators/test_flink_job.py` - Flink generator tests
- `tests/generators/test_feast_config.py` - Feast generator tests
- `tests/generators/test_airflow_dag.py` - Airflow DAG generator tests
- `tests/cli/test_generate.py` - CLI command tests
- `tests/integration/test_full_generation.py` - End-to-end generation test

**Code to modify:**
- `cli/main.py` - Add `generate` command

---

## Task 1: Base Generator Classes

**Files:**
- Create: `generators/__init__.py`
- Create: `generators/base.py`
- Test: `tests/generators/test_base.py`

- [ ] **Step 1: Write failing test for base generator interface**

```python
# tests/generators/test_base.py
import pytest
from pathlib import Path
from generators.base import BaseGenerator


class MockGenerator(BaseGenerator):
    """Concrete generator for testing."""

    def parse_source(self, source_path: Path) -> dict:
        return {"test": "data"}

    def generate_code(self, parsed_data: dict) -> str:
        return f"# Generated: {parsed_data}"

    def get_output_path(self, project_root: Path) -> Path:
        return project_root / ".nanoml" / "generated" / "mock.py"


def test_base_generator_interface():
    """BaseGenerator provides template method pattern."""
    gen = MockGenerator()

    # Should have abstract methods
    assert hasattr(gen, 'parse_source')
    assert hasattr(gen, 'generate_code')
    assert hasattr(gen, 'get_output_path')


def test_base_generator_run(tmp_path):
    """run() orchestrates parse -> generate -> write."""
    source = tmp_path / "source.py"
    source.write_text("# source")

    gen = MockGenerator()
    output_path = gen.run(source, tmp_path)

    assert output_path.exists()
    assert "# Generated:" in output_path.read_text()
    assert output_path == tmp_path / ".nanoml" / "generated" / "mock.py"


def test_base_generator_ensures_output_dir(tmp_path):
    """run() creates output directory if missing."""
    source = tmp_path / "source.py"
    source.write_text("# source")

    gen = MockGenerator()
    output_path = gen.run(source, tmp_path)

    assert output_path.parent.exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/generators/test_base.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'generators.base'"

- [ ] **Step 3: Implement base generator**

```python
# generators/__init__.py
"""Code generators for NanoML components."""

# generators/base.py
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseGenerator(ABC):
    """Abstract base class for all code generators.

    Implements template method pattern:
    1. parse_source() - Read and parse input files
    2. generate_code() - Apply templates to generate code
    3. get_output_path() - Determine where to write output
    4. run() - Orchestrate the process
    """

    @abstractmethod
    def parse_source(self, source_path: Path) -> dict[str, Any]:
        """Parse source file into structured data.

        Args:
            source_path: Path to source file to parse

        Returns:
            Parsed data as dictionary
        """
        pass

    @abstractmethod
    def generate_code(self, parsed_data: dict[str, Any]) -> str:
        """Generate code from parsed data.

        Args:
            parsed_data: Structured data from parse_source()

        Returns:
            Generated code as string
        """
        pass

    @abstractmethod
    def get_output_path(self, project_root: Path) -> Path:
        """Determine output file path.

        Args:
            project_root: Root directory of NanoML project

        Returns:
            Path where generated code should be written
        """
        pass

    def run(self, source_path: Path, project_root: Path) -> Path:
        """Run the full generation process.

        Template method that orchestrates:
        1. Parse source
        2. Generate code
        3. Ensure output directory exists
        4. Write generated code

        Args:
            source_path: Path to source file
            project_root: Root directory of NanoML project

        Returns:
            Path to generated file
        """
        # Parse
        parsed_data = self.parse_source(source_path)

        # Generate
        code = self.generate_code(parsed_data)

        # Determine output location
        output_path = self.get_output_path(project_root)

        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write
        output_path.write_text(code)

        return output_path
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/generators/test_base.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add generators/ tests/generators/test_base.py
git commit -m "$(cat <<'EOF'
feat(generators): add base generator class

Implements template method pattern for all code generators:
- parse_source() - read and parse input
- generate_code() - apply templates
- get_output_path() - determine output location
- run() - orchestrate full process

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Generated Code Manager

**Files:**
- Create: `core/generated_manager.py`
- Test: `tests/core/test_generated_manager.py`

- [ ] **Step 1: Write failing test for generated code manager**

```python
# tests/core/test_generated_manager.py
import pytest
from pathlib import Path
from core.generated_manager import GeneratedManager


def test_init_generated_directory(tmp_path):
    """init() creates .nanoml/generated/ structure."""
    manager = GeneratedManager(tmp_path)
    manager.init()

    generated_dir = tmp_path / ".nanoml" / "generated"
    assert generated_dir.exists()
    assert (generated_dir / "__init__.py").exists()
    assert (generated_dir / "flink").exists()
    assert (generated_dir / "feast").exists()
    assert (generated_dir / "airflow").exists()

    # Should have .gitignore
    gitignore = generated_dir / ".gitignore"
    assert gitignore.exists()
    assert "# Auto-generated" in gitignore.read_text()


def test_get_flink_dir(tmp_path):
    """get_flink_dir() returns Flink jobs directory."""
    manager = GeneratedManager(tmp_path)
    manager.init()

    flink_dir = manager.get_flink_dir()
    assert flink_dir == tmp_path / ".nanoml" / "generated" / "flink"
    assert flink_dir.exists()


def test_get_feast_dir(tmp_path):
    """get_feast_dir() returns Feast config directory."""
    manager = GeneratedManager(tmp_path)
    manager.init()

    feast_dir = manager.get_feast_dir()
    assert feast_dir == tmp_path / ".nanoml" / "generated" / "feast"
    assert feast_dir.exists()


def test_get_airflow_dir(tmp_path):
    """get_airflow_dir() returns Airflow DAGs directory."""
    manager = GeneratedManager(tmp_path)
    manager.init()

    airflow_dir = manager.get_airflow_dir()
    assert airflow_dir == tmp_path / ".nanoml" / "generated" / "airflow"
    assert airflow_dir.exists()


def test_clean_regenerates_structure(tmp_path):
    """clean() removes and recreates generated directory."""
    manager = GeneratedManager(tmp_path)
    manager.init()

    # Add some files
    flink_dir = manager.get_flink_dir()
    (flink_dir / "test.py").write_text("# test")

    # Clean
    manager.clean()

    # Directory structure recreated but files removed
    assert manager.get_flink_dir().exists()
    assert not (manager.get_flink_dir() / "test.py").exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/core/test_generated_manager.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'core.generated_manager'"

- [ ] **Step 3: Implement generated manager**

```python
# core/generated_manager.py
from pathlib import Path
import shutil


class GeneratedManager:
    """Manages the .nanoml/generated/ directory structure."""

    def __init__(self, project_root: Path):
        """Initialize manager.

        Args:
            project_root: Root directory of NanoML project
        """
        self.project_root = Path(project_root)
        self.generated_root = self.project_root / ".nanoml" / "generated"

    def init(self):
        """Initialize generated directory structure.

        Creates:
        - .nanoml/generated/
        - .nanoml/generated/__init__.py
        - .nanoml/generated/flink/
        - .nanoml/generated/feast/
        - .nanoml/generated/airflow/
        - .nanoml/generated/.gitignore
        """
        # Create directories
        self.generated_root.mkdir(parents=True, exist_ok=True)
        (self.generated_root / "flink").mkdir(exist_ok=True)
        (self.generated_root / "feast").mkdir(exist_ok=True)
        (self.generated_root / "airflow").mkdir(exist_ok=True)

        # Create __init__.py
        init_file = self.generated_root / "__init__.py"
        if not init_file.exists():
            init_file.write_text('"""Auto-generated code - do not edit manually."""\n')

        # Create .gitignore
        gitignore = self.generated_root / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text("""# Auto-generated code
# Commit this directory structure but ignore generated files
*.py
!__init__.py
*.yaml
*.yml
""")

    def get_flink_dir(self) -> Path:
        """Get Flink jobs directory.

        Returns:
            Path to .nanoml/generated/flink/
        """
        return self.generated_root / "flink"

    def get_feast_dir(self) -> Path:
        """Get Feast config directory.

        Returns:
            Path to .nanoml/generated/feast/
        """
        return self.generated_root / "feast"

    def get_airflow_dir(self) -> Path:
        """Get Airflow DAGs directory.

        Returns:
            Path to .nanoml/generated/airflow/
        """
        return self.generated_root / "airflow"

    def clean(self):
        """Remove and recreate generated directory.

        Removes all generated files while preserving structure.
        """
        if self.generated_root.exists():
            shutil.rmtree(self.generated_root)
        self.init()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/core/test_generated_manager.py -v`
Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add core/generated_manager.py tests/core/test_generated_manager.py
git commit -m "$(cat <<'EOF'
feat(core): add generated code directory manager

Manages .nanoml/generated/ structure:
- init() - create directory structure
- get_flink_dir/get_feast_dir/get_airflow_dir - access subdirectories
- clean() - remove and recreate

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Flink Job Generator

**Files:**
- Create: `generators/flink_job.py`
- Create: `generators/templates/flink_job.py.j2`
- Test: `tests/generators/test_flink_job.py`

- [ ] **Step 1: Write failing test for Flink job generator**

```python
# tests/generators/test_flink_job.py
import pytest
from pathlib import Path
from generators.flink_job import FlinkJobGenerator


SAMPLE_FEATURES = '''
from nanoml.features import Feature, FeatureGroup

user_features = FeatureGroup(
    name="user_features",
    entity="user_id",
    features=[
        Feature("age", "int"),
        Feature("country", "string"),
    ],
    source="kafka://user_events"
)

item_features = FeatureGroup(
    name="item_features",
    entity="item_id",
    features=[
        Feature("category", "string"),
        Feature("price", "float"),
    ],
    source="kafka://item_events"
)
'''


def test_parse_feature_definitions(tmp_path):
    """parse_source() extracts FeatureGroup definitions."""
    features_file = tmp_path / "definitions.py"
    features_file.write_text(SAMPLE_FEATURES)

    gen = FlinkJobGenerator()
    parsed = gen.parse_source(features_file)

    assert len(parsed["feature_groups"]) == 2

    # Check user_features
    user_fg = parsed["feature_groups"][0]
    assert user_fg["name"] == "user_features"
    assert user_fg["entity"] == "user_id"
    assert user_fg["source"] == "kafka://user_events"
    assert len(user_fg["features"]) == 2
    assert user_fg["features"][0]["name"] == "age"
    assert user_fg["features"][0]["type"] == "int"

    # Check item_features
    item_fg = parsed["feature_groups"][1]
    assert item_fg["name"] == "item_features"
    assert item_fg["entity"] == "item_id"


def test_generate_flink_job_code(tmp_path):
    """generate_code() produces valid Flink job Python code."""
    features_file = tmp_path / "definitions.py"
    features_file.write_text(SAMPLE_FEATURES)

    gen = FlinkJobGenerator()
    parsed = gen.parse_source(features_file)
    code = gen.generate_code(parsed)

    # Should be valid Python
    compile(code, "<string>", "exec")

    # Should import Flink
    assert "from pyflink" in code

    # Should have Kafka source for each feature group
    assert "kafka://user_events" in code
    assert "kafka://item_events" in code

    # Should write to Feast
    assert "feast" in code.lower()


def test_get_output_path(tmp_path):
    """get_output_path() returns .nanoml/generated/flink/streaming_features.py."""
    gen = FlinkJobGenerator()
    output = gen.get_output_path(tmp_path)

    assert output == tmp_path / ".nanoml" / "generated" / "flink" / "streaming_features.py"


def test_full_flink_generation(tmp_path):
    """run() generates complete Flink job."""
    features_file = tmp_path / "definitions.py"
    features_file.write_text(SAMPLE_FEATURES)

    gen = FlinkJobGenerator()
    output_path = gen.run(features_file, tmp_path)

    assert output_path.exists()
    code = output_path.read_text()

    # Verify generated code structure
    assert "def main():" in code
    assert "kafka://user_events" in code
    assert "kafka://item_events" in code
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/generators/test_flink_job.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'generators.flink_job'"

- [ ] **Step 3: Create Flink job template**

```python
# generators/templates/flink_job.py.j2
"""
Auto-generated Flink streaming feature computation job.

DO NOT EDIT - Generated from features/definitions.py
Run `nanoml generate` to regenerate.
"""
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.common.serialization import SimpleStringSchema
import json


def main():
    """Run Flink streaming job for feature computation."""
    env = StreamExecutionEnvironment.get_execution_environment()

    {% for fg in feature_groups %}
    # Feature Group: {{ fg.name }}
    # Entity: {{ fg.entity }}
    # Source: {{ fg.source }}

    {{ fg.name }}_consumer = FlinkKafkaConsumer(
        topics="{{ fg.source.replace('kafka://', '') }}",
        deserialization_schema=SimpleStringSchema(),
        properties={
            "bootstrap.servers": "kafka:9092",
            "group.id": "nanoml_{{ fg.name }}"
        }
    )

    {{ fg.name }}_stream = env.add_source({{ fg.name }}_consumer)

    def process_{{ fg.name }}(event: str) -> str:
        """Extract features from {{ fg.name }} events."""
        data = json.loads(event)

        features = {
            "entity_id": data.get("{{ fg.entity }}"),
            {% for feature in fg.features %}
            "{{ feature.name }}": data.get("{{ feature.name }}"),
            {% endfor %}
            "event_timestamp": data.get("timestamp")
        }

        return json.dumps(features)

    {{ fg.name }}_features = {{ fg.name }}_stream.map(process_{{ fg.name }})

    # Write to Feast via Kafka
    {{ fg.name }}_producer = FlinkKafkaProducer(
        topic="feast_{{ fg.name }}",
        serialization_schema=SimpleStringSchema(),
        producer_config={
            "bootstrap.servers": "kafka:9092"
        }
    )

    {{ fg.name }}_features.add_sink({{ fg.name }}_producer)

    {% endfor %}

    # Execute
    env.execute("NanoML Streaming Features")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Implement Flink job generator**

```python
# generators/flink_job.py
import ast
from pathlib import Path
from typing import Any
from jinja2 import Environment, FileSystemLoader
from .base import BaseGenerator


class FlinkJobGenerator(BaseGenerator):
    """Generates Flink streaming jobs from feature definitions."""

    def __init__(self):
        """Initialize generator with Jinja2 environment."""
        template_dir = Path(__file__).parent / "templates"
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))

    def parse_source(self, source_path: Path) -> dict[str, Any]:
        """Parse features/definitions.py to extract FeatureGroups.

        Args:
            source_path: Path to features/definitions.py

        Returns:
            {
                "feature_groups": [
                    {
                        "name": "user_features",
                        "entity": "user_id",
                        "source": "kafka://user_events",
                        "features": [
                            {"name": "age", "type": "int"},
                            {"name": "country", "type": "string"}
                        ]
                    }
                ]
            }
        """
        code = source_path.read_text()
        tree = ast.parse(code)

        feature_groups = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                # Look for: var_name = FeatureGroup(...)
                if len(node.targets) == 1 and isinstance(node.value, ast.Call):
                    call = node.value
                    if (isinstance(call.func, ast.Name) and
                        call.func.id == "FeatureGroup"):

                        fg_data = self._parse_feature_group(node.targets[0].id, call)
                        feature_groups.append(fg_data)

        return {"feature_groups": feature_groups}

    def _parse_feature_group(self, var_name: str, call: ast.Call) -> dict[str, Any]:
        """Parse a FeatureGroup(...) call node."""
        fg = {"name": var_name, "features": []}

        for keyword in call.keywords:
            if keyword.arg == "name":
                fg["name"] = ast.literal_eval(keyword.value)
            elif keyword.arg == "entity":
                fg["entity"] = ast.literal_eval(keyword.value)
            elif keyword.arg == "source":
                fg["source"] = ast.literal_eval(keyword.value)
            elif keyword.arg == "features":
                # List of Feature(...) calls
                if isinstance(keyword.value, ast.List):
                    for feat_call in keyword.value.elts:
                        if isinstance(feat_call, ast.Call):
                            feat_name = ast.literal_eval(feat_call.args[0])
                            feat_type = ast.literal_eval(feat_call.args[1])
                            fg["features"].append({
                                "name": feat_name,
                                "type": feat_type
                            })

        return fg

    def generate_code(self, parsed_data: dict[str, Any]) -> str:
        """Generate Flink job code from parsed feature groups.

        Args:
            parsed_data: Output from parse_source()

        Returns:
            Generated Python code as string
        """
        template = self.jinja_env.get_template("flink_job.py.j2")
        return template.render(**parsed_data)

    def get_output_path(self, project_root: Path) -> Path:
        """Get output path for Flink job.

        Args:
            project_root: Root directory of NanoML project

        Returns:
            .nanoml/generated/flink/streaming_features.py
        """
        return project_root / ".nanoml" / "generated" / "flink" / "streaming_features.py"
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/generators/test_flink_job.py -v`
Expected: PASS (5 tests)

- [ ] **Step 6: Commit**

```bash
git add generators/flink_job.py generators/templates/flink_job.py.j2 tests/generators/test_flink_job.py
git commit -m "$(cat <<'EOF'
feat(generators): add Flink job generator

Parses features/definitions.py (FeatureGroup AST) and generates
Flink streaming job that:
- Reads from Kafka sources
- Extracts features per FeatureGroup
- Writes to Feast via Kafka topics

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Feast Config Generator

**Files:**
- Create: `generators/feast_config.py`
- Create: `generators/templates/feast_store.yaml.j2`
- Create: `generators/templates/feast_features.py.j2`
- Test: `tests/generators/test_feast_config.py`

- [ ] **Step 1: Write failing test for Feast config generator**

```python
# tests/generators/test_feast_config.py
import pytest
import yaml
from pathlib import Path
from generators.feast_config import FeastConfigGenerator


SAMPLE_FEATURES = '''
from nanoml.features import Feature, FeatureGroup

user_features = FeatureGroup(
    name="user_features",
    entity="user_id",
    features=[
        Feature("age", "int"),
        Feature("country", "string"),
    ],
    source="kafka://user_events"
)
'''


def test_parse_generates_feast_entities_and_features(tmp_path):
    """parse_source() extracts entities and features for Feast."""
    features_file = tmp_path / "definitions.py"
    features_file.write_text(SAMPLE_FEATURES)

    gen = FeastConfigGenerator()
    parsed = gen.parse_source(features_file)

    assert "entities" in parsed
    assert "feature_views" in parsed

    # Should extract user_id entity
    assert len(parsed["entities"]) == 1
    assert parsed["entities"][0]["name"] == "user_id"

    # Should extract user_features view
    assert len(parsed["feature_views"]) == 1
    view = parsed["feature_views"][0]
    assert view["name"] == "user_features"
    assert view["entity"] == "user_id"
    assert len(view["features"]) == 2


def test_generate_feast_store_yaml(tmp_path):
    """generate_code() produces feature_store.yaml."""
    features_file = tmp_path / "definitions.py"
    features_file.write_text(SAMPLE_FEATURES)

    gen = FeastConfigGenerator(output_type="store")
    parsed = gen.parse_source(features_file)
    code = gen.generate_code(parsed)

    # Should be valid YAML
    config = yaml.safe_load(code)

    assert config["project"] == "nanoml"
    assert config["provider"] == "local"
    assert "online_store" in config
    assert "offline_store" in config


def test_generate_feast_features_py(tmp_path):
    """generate_code() produces features.py with Entity and FeatureView."""
    features_file = tmp_path / "definitions.py"
    features_file.write_text(SAMPLE_FEATURES)

    gen = FeastConfigGenerator(output_type="features")
    parsed = gen.parse_source(features_file)
    code = gen.generate_code(parsed)

    # Should be valid Python
    compile(code, "<string>", "exec")

    # Should define entities
    assert "Entity(" in code
    assert 'name="user_id"' in code

    # Should define feature views
    assert "FeatureView(" in code
    assert 'name="user_features"' in code


def test_get_output_paths(tmp_path):
    """get_output_path() returns correct paths for store vs features."""
    gen_store = FeastConfigGenerator(output_type="store")
    assert gen_store.get_output_path(tmp_path) == \
        tmp_path / ".nanoml" / "generated" / "feast" / "feature_store.yaml"

    gen_features = FeastConfigGenerator(output_type="features")
    assert gen_features.get_output_path(tmp_path) == \
        tmp_path / ".nanoml" / "generated" / "feast" / "features.py"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/generators/test_feast_config.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'generators.feast_config'"

- [ ] **Step 3: Create Feast templates**

```yaml
# generators/templates/feast_store.yaml.j2
# Auto-generated Feast feature store configuration
# DO NOT EDIT - Generated from features/definitions.py
# Run `nanoml generate` to regenerate

project: nanoml
provider: local

registry:
  path: /data/feast/registry.db
  cache_ttl_seconds: 60

online_store:
  type: redis
  connection_string: redis:6379

offline_store:
  type: file
  path: /data/feast/offline_store

entity_key_serialization_version: 2
```

```python
# generators/templates/feast_features.py.j2
"""
Auto-generated Feast feature definitions.

DO NOT EDIT - Generated from features/definitions.py
Run `nanoml generate` to regenerate.
"""
from feast import Entity, FeatureView, Field
from feast.types import Int64, String, Float32
from datetime import timedelta


# Type mapping
TYPE_MAP = {
    "int": Int64,
    "string": String,
    "float": Float32
}


{% for entity in entities %}
# Entity: {{ entity.name }}
{{ entity.name }} = Entity(
    name="{{ entity.name }}",
    description="Auto-generated entity for {{ entity.name }}"
)

{% endfor %}

{% for view in feature_views %}
# Feature View: {{ view.name }}
{{ view.name }} = FeatureView(
    name="{{ view.name }}",
    entities=[{{ view.entity }}],
    ttl=timedelta(days=1),
    schema=[
        {% for feature in view.features %}
        Field(name="{{ feature.name }}", dtype=TYPE_MAP["{{ feature.type }}"]),
        {% endfor %}
    ],
    online=True,
    source=None  # Populated by Flink streaming job
)

{% endfor %}
```

- [ ] **Step 4: Implement Feast config generator**

```python
# generators/feast_config.py
import ast
from pathlib import Path
from typing import Any, Literal
from jinja2 import Environment, FileSystemLoader
from .base import BaseGenerator


class FeastConfigGenerator(BaseGenerator):
    """Generates Feast configuration from feature definitions."""

    def __init__(self, output_type: Literal["store", "features"] = "store"):
        """Initialize generator.

        Args:
            output_type: "store" for feature_store.yaml, "features" for features.py
        """
        self.output_type = output_type
        template_dir = Path(__file__).parent / "templates"
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))

    def parse_source(self, source_path: Path) -> dict[str, Any]:
        """Parse features/definitions.py to extract entities and feature views.

        Args:
            source_path: Path to features/definitions.py

        Returns:
            {
                "entities": [{"name": "user_id"}, {"name": "item_id"}],
                "feature_views": [
                    {
                        "name": "user_features",
                        "entity": "user_id",
                        "features": [{"name": "age", "type": "int"}]
                    }
                ]
            }
        """
        code = source_path.read_text()
        tree = ast.parse(code)

        entities_set = set()
        feature_views = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                if len(node.targets) == 1 and isinstance(node.value, ast.Call):
                    call = node.value
                    if (isinstance(call.func, ast.Name) and
                        call.func.id == "FeatureGroup"):

                        view = self._parse_feature_view(node.targets[0].id, call)
                        feature_views.append(view)
                        entities_set.add(view["entity"])

        entities = [{"name": e} for e in sorted(entities_set)]

        return {
            "entities": entities,
            "feature_views": feature_views
        }

    def _parse_feature_view(self, var_name: str, call: ast.Call) -> dict[str, Any]:
        """Parse a FeatureGroup(...) call into Feast FeatureView."""
        view = {"name": var_name, "features": []}

        for keyword in call.keywords:
            if keyword.arg == "name":
                view["name"] = ast.literal_eval(keyword.value)
            elif keyword.arg == "entity":
                view["entity"] = ast.literal_eval(keyword.value)
            elif keyword.arg == "features":
                if isinstance(keyword.value, ast.List):
                    for feat_call in keyword.value.elts:
                        if isinstance(feat_call, ast.Call):
                            feat_name = ast.literal_eval(feat_call.args[0])
                            feat_type = ast.literal_eval(feat_call.args[1])
                            view["features"].append({
                                "name": feat_name,
                                "type": feat_type
                            })

        return view

    def generate_code(self, parsed_data: dict[str, Any]) -> str:
        """Generate Feast config from parsed data.

        Args:
            parsed_data: Output from parse_source()

        Returns:
            Generated YAML or Python code as string
        """
        if self.output_type == "store":
            template = self.jinja_env.get_template("feast_store.yaml.j2")
        else:
            template = self.jinja_env.get_template("feast_features.py.j2")

        return template.render(**parsed_data)

    def get_output_path(self, project_root: Path) -> Path:
        """Get output path for Feast config.

        Args:
            project_root: Root directory of NanoML project

        Returns:
            Path to feature_store.yaml or features.py
        """
        feast_dir = project_root / ".nanoml" / "generated" / "feast"

        if self.output_type == "store":
            return feast_dir / "feature_store.yaml"
        else:
            return feast_dir / "features.py"
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/generators/test_feast_config.py -v`
Expected: PASS (4 tests)

- [ ] **Step 6: Commit**

```bash
git add generators/feast_config.py generators/templates/feast_*.j2 tests/generators/test_feast_config.py
git commit -m "$(cat <<'EOF'
feat(generators): add Feast config generator

Generates both feature_store.yaml and features.py from
feature definitions. Extracts:
- Entities (from FeatureGroup entity field)
- FeatureViews (from FeatureGroup with schema)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Airflow DAG Generator

**Files:**
- Create: `generators/airflow_dag.py`
- Create: `generators/templates/airflow_dag.py.j2`
- Test: `tests/generators/test_airflow_dag.py`

- [ ] **Step 1: Write failing test for Airflow DAG generator**

```python
# tests/generators/test_airflow_dag.py
import pytest
from pathlib import Path
from generators.airflow_dag import AirflowDAGGenerator


SAMPLE_COMPONENTS = '''
from nanoml.components import DataComponent, FeaturesComponent

data = DataComponent(
    name="data_ingestion",
    schedule="@daily"
)

features = FeaturesComponent(
    name="feature_generation",
    depends_on=[data],
    schedule="@daily"
)
'''


def test_parse_component_dag(tmp_path):
    """parse_source() extracts component DAG structure."""
    components_file = tmp_path / "pipeline.py"
    components_file.write_text(SAMPLE_COMPONENTS)

    gen = AirflowDAGGenerator()
    parsed = gen.parse_source(components_file)

    assert len(parsed["components"]) == 2

    # Check data component
    data = parsed["components"][0]
    assert data["name"] == "data_ingestion"
    assert data["type"] == "DataComponent"
    assert data["schedule"] == "@daily"
    assert data["depends_on"] == []

    # Check features component
    features = parsed["components"][1]
    assert features["name"] == "feature_generation"
    assert features["type"] == "FeaturesComponent"
    assert features["depends_on"] == ["data"]


def test_generate_airflow_dag_code(tmp_path):
    """generate_code() produces valid Airflow DAG."""
    components_file = tmp_path / "pipeline.py"
    components_file.write_text(SAMPLE_COMPONENTS)

    gen = AirflowDAGGenerator()
    parsed = gen.parse_source(components_file)
    code = gen.generate_code(parsed)

    # Should be valid Python
    compile(code, "<string>", "exec")

    # Should import Airflow
    assert "from airflow import DAG" in code

    # Should create tasks
    assert "data_ingestion" in code
    assert "feature_generation" in code

    # Should set dependencies
    assert ">>" in code or "set_downstream" in code


def test_get_output_path(tmp_path):
    """get_output_path() returns .nanoml/generated/airflow/pipeline_dag.py."""
    gen = AirflowDAGGenerator()
    output = gen.get_output_path(tmp_path)

    assert output == tmp_path / ".nanoml" / "generated" / "airflow" / "pipeline_dag.py"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/generators/test_airflow_dag.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'generators.airflow_dag'"

- [ ] **Step 3: Create Airflow DAG template**

```python
# generators/templates/airflow_dag.py.j2
"""
Auto-generated Airflow DAG for NanoML pipeline.

DO NOT EDIT - Generated from components
Run `nanoml generate` to regenerate.
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta


default_args = {
    "owner": "nanoml",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

dag = DAG(
    "nanoml_pipeline",
    default_args=default_args,
    description="Auto-generated NanoML ML pipeline",
    schedule_interval="{{ components[0].schedule if components else '@daily' }}",
    catchup=False
)


{% for component in components %}
def {{ component.name }}_task():
    """Execute {{ component.type }} component."""
    # Import component
    from components.{{ component.type.replace('Component', '').lower() }} import {{ component.type }}

    # Run component
    component = {{ component.type }}(name="{{ component.name }}")
    component.run()


{{ component.name }} = PythonOperator(
    task_id="{{ component.name }}",
    python_callable={{ component.name }}_task,
    dag=dag
)

{% endfor %}

# Set dependencies
{% for component in components %}
{% if component.depends_on %}
{% for dep in component.depends_on %}
{{ dep }} >> {{ component.name }}
{% endfor %}
{% endif %}
{% endfor %}
```

- [ ] **Step 4: Implement Airflow DAG generator**

```python
# generators/airflow_dag.py
import ast
from pathlib import Path
from typing import Any
from jinja2 import Environment, FileSystemLoader
from .base import BaseGenerator


class AirflowDAGGenerator(BaseGenerator):
    """Generates Airflow DAG from NanoML components."""

    def __init__(self):
        """Initialize generator with Jinja2 environment."""
        template_dir = Path(__file__).parent / "templates"
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))

    def parse_source(self, source_path: Path) -> dict[str, Any]:
        """Parse component definitions to extract DAG structure.

        Args:
            source_path: Path to components file (e.g., pipeline.py)

        Returns:
            {
                "components": [
                    {
                        "name": "data_ingestion",
                        "type": "DataComponent",
                        "schedule": "@daily",
                        "depends_on": []
                    }
                ]
            }
        """
        code = source_path.read_text()
        tree = ast.parse(code)

        components = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                if len(node.targets) == 1 and isinstance(node.value, ast.Call):
                    call = node.value
                    if (isinstance(call.func, ast.Name) and
                        "Component" in call.func.id):

                        comp = self._parse_component(node.targets[0].id, call)
                        components.append(comp)

        return {"components": components}

    def _parse_component(self, var_name: str, call: ast.Call) -> dict[str, Any]:
        """Parse a Component(...) call node."""
        comp = {
            "name": var_name,
            "type": call.func.id,
            "schedule": "@daily",
            "depends_on": []
        }

        for keyword in call.keywords:
            if keyword.arg == "name":
                comp["name"] = ast.literal_eval(keyword.value)
            elif keyword.arg == "schedule":
                comp["schedule"] = ast.literal_eval(keyword.value)
            elif keyword.arg == "depends_on":
                # List of variable references
                if isinstance(keyword.value, ast.List):
                    for dep_node in keyword.value.elts:
                        if isinstance(dep_node, ast.Name):
                            comp["depends_on"].append(dep_node.id)

        return comp

    def generate_code(self, parsed_data: dict[str, Any]) -> str:
        """Generate Airflow DAG from parsed components.

        Args:
            parsed_data: Output from parse_source()

        Returns:
            Generated Python code as string
        """
        template = self.jinja_env.get_template("airflow_dag.py.j2")
        return template.render(**parsed_data)

    def get_output_path(self, project_root: Path) -> Path:
        """Get output path for Airflow DAG.

        Args:
            project_root: Root directory of NanoML project

        Returns:
            .nanoml/generated/airflow/pipeline_dag.py
        """
        return project_root / ".nanoml" / "generated" / "airflow" / "pipeline_dag.py"
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/generators/test_airflow_dag.py -v`
Expected: PASS (3 tests)

- [ ] **Step 6: Commit**

```bash
git add generators/airflow_dag.py generators/templates/airflow_dag.py.j2 tests/generators/test_airflow_dag.py
git commit -m "$(cat <<'EOF'
feat(generators): add Airflow DAG generator

Parses component definitions and generates Airflow DAG with:
- PythonOperator per component
- Task dependencies from depends_on
- Component execution via run() method

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: CLI Generate Command

**Files:**
- Create: `cli/generate.py`
- Modify: `cli/main.py` - Add generate command
- Test: `tests/cli/test_generate.py`

- [ ] **Step 1: Write failing test for generate command**

```python
# tests/cli/test_generate.py
import pytest
from pathlib import Path
from click.testing import CliRunner
from cli.main import cli


@pytest.fixture
def sample_project(tmp_path):
    """Create a sample NanoML project."""
    # Create project structure
    (tmp_path / "nanoml.yaml").write_text("name: test_project\nversion: 0.1.0")
    (tmp_path / "features").mkdir()
    (tmp_path / "components").mkdir()

    # Create sample features
    (tmp_path / "features" / "definitions.py").write_text('''
from nanoml.features import Feature, FeatureGroup

user_features = FeatureGroup(
    name="user_features",
    entity="user_id",
    features=[Feature("age", "int")],
    source="kafka://users"
)
''')

    return tmp_path


def test_generate_creates_all_artifacts(sample_project):
    """nanoml generate creates Flink, Feast, and Airflow code."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=sample_project):
        result = runner.invoke(cli, ["generate"])

        assert result.exit_code == 0
        assert "Generated Flink job" in result.output
        assert "Generated Feast config" in result.output

        # Check files created
        generated_dir = sample_project / ".nanoml" / "generated"
        assert (generated_dir / "flink" / "streaming_features.py").exists()
        assert (generated_dir / "feast" / "feature_store.yaml").exists()
        assert (generated_dir / "feast" / "features.py").exists()


def test_generate_clean_flag(sample_project):
    """nanoml generate --clean removes existing generated code first."""
    # Create some existing generated files
    gen_dir = sample_project / ".nanoml" / "generated"
    gen_dir.mkdir(parents=True, exist_ok=True)
    (gen_dir / "old_file.py").write_text("# old")

    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=sample_project):
        result = runner.invoke(cli, ["generate", "--clean"])

        assert result.exit_code == 0
        assert not (gen_dir / "old_file.py").exists()


def test_generate_fails_without_nanoml_yaml(tmp_path):
    """nanoml generate fails if not in NanoML project."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["generate"])

        assert result.exit_code != 0
        assert "No nanoml.yaml found" in result.output
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/cli/test_generate.py -v`
Expected: FAIL with "No such command 'generate'"

- [ ] **Step 3: Implement generate command**

```python
# cli/generate.py
import click
from pathlib import Path
from core.config import load_config
from core.generated_manager import GeneratedManager
from generators.flink_job import FlinkJobGenerator
from generators.feast_config import FeastConfigGenerator
from generators.airflow_dag import AirflowDAGGenerator


@click.command()
@click.option(
    "--clean",
    is_flag=True,
    help="Clean generated directory before generating"
)
def generate(clean: bool):
    """Generate Flink jobs, Feast configs, and Airflow DAGs from definitions.

    Reads:
    - features/definitions.py -> Flink jobs + Feast configs
    - components/*.py -> Airflow DAGs

    Writes to:
    - .nanoml/generated/flink/
    - .nanoml/generated/feast/
    - .nanoml/generated/airflow/
    """
    # Find project root
    project_root = Path.cwd()
    config_path = project_root / "nanoml.yaml"

    if not config_path.exists():
        click.echo("❌ No nanoml.yaml found in current directory", err=True)
        click.echo("Run this command from a NanoML project root", err=True)
        raise click.Abort()

    # Load config
    config = load_config(config_path)
    click.echo(f"Generating code for project: {config.name}")

    # Initialize generated directory
    manager = GeneratedManager(project_root)

    if clean:
        click.echo("Cleaning generated directory...")
        manager.clean()
    else:
        manager.init()

    # Generate Flink jobs
    features_file = project_root / "features" / "definitions.py"
    if features_file.exists():
        click.echo("Generating Flink streaming job...")
        flink_gen = FlinkJobGenerator()
        flink_output = flink_gen.run(features_file, project_root)
        click.echo(f"  ✓ Generated {flink_output.relative_to(project_root)}")

        # Generate Feast configs
        click.echo("Generating Feast configuration...")

        feast_store_gen = FeastConfigGenerator(output_type="store")
        store_output = feast_store_gen.run(features_file, project_root)
        click.echo(f"  ✓ Generated {store_output.relative_to(project_root)}")

        feast_features_gen = FeastConfigGenerator(output_type="features")
        features_output = feast_features_gen.run(features_file, project_root)
        click.echo(f"  ✓ Generated {features_output.relative_to(project_root)}")
    else:
        click.echo("⚠️  No features/definitions.py found, skipping Flink/Feast generation")

    # Generate Airflow DAGs (look for pipeline.py or similar)
    components_files = list((project_root / "components").glob("*.py"))
    if components_files:
        click.echo("Generating Airflow DAG...")
        for comp_file in components_files:
            if comp_file.name == "__init__.py":
                continue

            airflow_gen = AirflowDAGGenerator()
            dag_output = airflow_gen.run(comp_file, project_root)
            click.echo(f"  ✓ Generated {dag_output.relative_to(project_root)}")
    else:
        click.echo("⚠️  No component files found, skipping Airflow generation")

    click.echo("\n✨ Code generation complete!")
    click.echo(f"Generated code location: {manager.generated_root.relative_to(project_root)}")
```

- [ ] **Step 4: Add generate command to CLI**

```python
# cli/main.py (modify)
from cli.generate import generate

@click.group()
def cli():
    """NanoML - Declarative ML recommendation framework."""
    pass

cli.add_command(init)
cli.add_command(validate)
cli.add_command(generate)  # Add this line
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/cli/test_generate.py -v`
Expected: PASS (3 tests)

- [ ] **Step 6: Commit**

```bash
git add cli/generate.py cli/main.py tests/cli/test_generate.py
git commit -m "$(cat <<'EOF'
feat(cli): add nanoml generate command

Generates all code from user definitions:
- Flink streaming jobs from features/definitions.py
- Feast configs (feature_store.yaml, features.py)
- Airflow DAGs from components/*.py

Supports --clean flag to regenerate from scratch.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: Integration Tests & Documentation

**Files:**
- Create: `tests/integration/test_full_generation.py`
- Create: `docs/code-generation.md`

- [ ] **Step 1: Write end-to-end generation test**

```python
# tests/integration/test_full_generation.py
import pytest
from pathlib import Path
from click.testing import CliRunner
from cli.main import cli


@pytest.fixture
def full_project(tmp_path):
    """Create a complete NanoML project for testing."""
    # nanoml.yaml
    (tmp_path / "nanoml.yaml").write_text("""
name: movie_recommendations
version: 0.1.0
description: Movie recommendation system
""")

    # features/definitions.py
    features_dir = tmp_path / "features"
    features_dir.mkdir()
    (features_dir / "definitions.py").write_text('''
from nanoml.features import Feature, FeatureGroup

user_features = FeatureGroup(
    name="user_features",
    entity="user_id",
    features=[
        Feature("age", "int"),
        Feature("country", "string"),
        Feature("total_watches", "int")
    ],
    source="kafka://user_events"
)

movie_features = FeatureGroup(
    name="movie_features",
    entity="movie_id",
    features=[
        Feature("genre", "string"),
        Feature("release_year", "int"),
        Feature("avg_rating", "float")
    ],
    source="kafka://movie_events"
)
''')

    # components/pipeline.py
    components_dir = tmp_path / "components"
    components_dir.mkdir()
    (components_dir / "pipeline.py").write_text('''
from nanoml.components import DataComponent, FeaturesComponent, TrainingComponent

data = DataComponent(
    name="data_ingestion",
    schedule="@daily"
)

features = FeaturesComponent(
    name="feature_generation",
    depends_on=[data],
    schedule="@daily"
)

training = TrainingComponent(
    name="model_training",
    depends_on=[features],
    schedule="@daily"
)
''')

    return tmp_path


def test_full_code_generation_workflow(full_project):
    """End-to-end test: init -> generate -> validate artifacts."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=full_project):
        # Run generate
        result = runner.invoke(cli, ["generate", "--clean"])
        assert result.exit_code == 0

        # Verify Flink job
        flink_job = full_project / ".nanoml" / "generated" / "flink" / "streaming_features.py"
        assert flink_job.exists()

        code = flink_job.read_text()
        assert "user_features" in code
        assert "movie_features" in code
        assert "kafka://user_events" in code
        assert "kafka://movie_events" in code
        assert "def main():" in code

        # Verify Feast config
        feast_store = full_project / ".nanoml" / "generated" / "feast" / "feature_store.yaml"
        assert feast_store.exists()

        feast_features = full_project / ".nanoml" / "generated" / "feast" / "features.py"
        assert feast_features.exists()

        features_code = feast_features.read_text()
        assert "user_id = Entity" in features_code
        assert "movie_id = Entity" in features_code
        assert "user_features = FeatureView" in features_code
        assert "movie_features = FeatureView" in features_code

        # Verify Airflow DAG
        airflow_dag = full_project / ".nanoml" / "generated" / "airflow" / "pipeline_dag.py"
        assert airflow_dag.exists()

        dag_code = airflow_dag.read_text()
        assert "data_ingestion" in dag_code
        assert "feature_generation" in dag_code
        assert "model_training" in dag_code
        assert "data_ingestion >> feature_generation" in dag_code
        assert "feature_generation >> model_training" in dag_code


def test_regeneration_idempotent(full_project):
    """Running generate multiple times produces same output."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=full_project):
        # First generation
        result1 = runner.invoke(cli, ["generate"])
        assert result1.exit_code == 0

        flink_job = full_project / ".nanoml" / "generated" / "flink" / "streaming_features.py"
        content1 = flink_job.read_text()

        # Second generation
        result2 = runner.invoke(cli, ["generate"])
        assert result2.exit_code == 0

        content2 = flink_job.read_text()

        # Should be identical
        assert content1 == content2
```

- [ ] **Step 2: Run integration tests**

Run: `pytest tests/integration/test_full_generation.py -v`
Expected: PASS (2 tests)

- [ ] **Step 3: Write code generation documentation**

```markdown
# docs/code-generation.md
# Code Generation in NanoML

NanoML automatically generates infrastructure code from your high-level definitions. This document explains what gets generated and how.

## Overview

When you run `nanoml generate`, NanoML reads your user code and generates:

1. **Flink Streaming Jobs** - From `features/definitions.py`
2. **Feast Configuration** - From `features/definitions.py`
3. **Airflow DAGs** - From `components/*.py`

All generated code is written to `.nanoml/generated/` and should not be edited manually.

## Directory Structure

```
.nanoml/generated/
├── flink/
│   └── streaming_features.py    # Flink job for feature computation
├── feast/
│   ├── feature_store.yaml        # Feast configuration
│   └── features.py               # Entity and FeatureView definitions
└── airflow/
    └── pipeline_dag.py           # Orchestration DAG
```

## Flink Job Generation

**Input:** `features/definitions.py`

**Output:** `.nanoml/generated/flink/streaming_features.py`

The generator:
1. Parses `FeatureGroup` definitions using AST
2. Creates a Kafka consumer per feature group
3. Generates feature extraction logic
4. Writes results to Feast via Kafka topics

**Example:**

```python
# features/definitions.py
user_features = FeatureGroup(
    name="user_features",
    entity="user_id",
    features=[Feature("age", "int")],
    source="kafka://user_events"
)
```

Generates a Flink job that:
- Consumes from `user_events` Kafka topic
- Extracts `age` field and `user_id` entity
- Publishes to `feast_user_features` Kafka topic

## Feast Configuration Generation

**Input:** `features/definitions.py`

**Outputs:**
- `.nanoml/generated/feast/feature_store.yaml`
- `.nanoml/generated/feast/features.py`

The generator:
1. Extracts unique entities from all `FeatureGroup` definitions
2. Creates Feast `Entity` definitions
3. Creates Feast `FeatureView` definitions with schema

**Example:**

```python
# Generated features.py
user_id = Entity(
    name="user_id",
    description="Auto-generated entity for user_id"
)

user_features = FeatureView(
    name="user_features",
    entities=[user_id],
    schema=[
        Field(name="age", dtype=Int64)
    ],
    ...
)
```

## Airflow DAG Generation

**Input:** `components/*.py`

**Output:** `.nanoml/generated/airflow/pipeline_dag.py`

The generator:
1. Parses component definitions (DataComponent, FeaturesComponent, etc.)
2. Creates PythonOperator per component
3. Sets task dependencies from `depends_on` field

**Example:**

```python
# components/pipeline.py
data = DataComponent(name="ingest")
features = FeaturesComponent(name="compute", depends_on=[data])
```

Generates:
```python
ingest >> compute
```

## Usage

### Generate All Code

```bash
nanoml generate
```

### Clean and Regenerate

```bash
nanoml generate --clean
```

This removes all existing generated code before regenerating.

## When to Regenerate

Run `nanoml generate` whenever you:
- Add/modify feature definitions
- Add/modify components
- Change dependencies between components

## Generated Code Guarantees

1. **Idempotent** - Running generate multiple times produces identical output
2. **Complete** - All information from user definitions is preserved
3. **Valid** - Generated code passes syntax checks (compile for Python, parse for YAML)
4. **Deterministic** - Same input always produces same output

## Debugging Generated Code

If generated code doesn't work:

1. Check the source definitions for errors
2. Run `nanoml validate` to catch config issues
3. Examine generated files in `.nanoml/generated/`
4. File an issue if generation is incorrect

Generated code includes comments showing:
- Source file it was generated from
- Warning not to edit manually
- Regeneration command

## Customization

Generated code is intentionally not customizable. If you need different behavior:

1. Modify your source definitions
2. File a feature request for new generation patterns
3. For one-off needs, implement manually in `components/` instead of relying on generation
```

- [ ] **Step 4: Run integration tests again**

Run: `pytest tests/integration/test_full_generation.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add tests/integration/test_full_generation.py docs/code-generation.md
git commit -m "$(cat <<'EOF'
test: add end-to-end code generation tests

Validates full workflow:
- Features -> Flink + Feast
- Components -> Airflow DAG
- Idempotent regeneration

Also adds code generation documentation.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Final Validation

- [ ] **Step 1: Run full test suite**

Run: `pytest -v`
Expected: All tests pass

- [ ] **Step 2: Test CLI help**

Run: `nanoml generate --help`
Expected: Shows command help with --clean option

- [ ] **Step 3: Verify all files created**

Check that these exist:
- `generators/base.py`
- `generators/flink_job.py`
- `generators/feast_config.py`
- `generators/airflow_dag.py`
- `generators/templates/*.j2`
- `cli/generate.py`
- `core/generated_manager.py`
- All test files

- [ ] **Step 4: Review code coverage**

Run: `pytest --cov=generators --cov=core --cov-report=term-missing`
Expected: >90% coverage for generators and core modules

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "$(cat <<'EOF'
feat: complete code generation framework

All generators implemented:
- BaseGenerator (template method pattern)
- FlinkJobGenerator (features -> Flink streaming jobs)
- FeastConfigGenerator (features -> Feast entities + views)
- AirflowDAGGenerator (components -> Airflow DAG)

CLI command: nanoml generate [--clean]

Generated code location: .nanoml/generated/

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Summary

This plan implements the code generation framework that transforms user definitions into executable infrastructure code.

**Key deliverables:**
1. Base generator class with template method pattern
2. Three specialized generators (Flink, Feast, Airflow)
3. Jinja2 templates for each code type
4. CLI command for generation
5. Generated directory manager
6. Comprehensive tests and documentation

**After this plan:**
- Users can write high-level definitions
- `nanoml generate` produces all infrastructure code
- Ready for Plan 4: End-to-End Local Example
