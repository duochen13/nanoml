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
