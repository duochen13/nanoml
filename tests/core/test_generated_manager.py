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
