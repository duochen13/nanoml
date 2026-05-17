import pytest
import sys
from pathlib import Path

# Add infrastructure to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from components.data import DataComponent


@pytest.fixture
def data_dir(tmp_path):
    """Create sample data files."""
    data = tmp_path / "data"
    data.mkdir()

    (data / "movies.csv").write_text("""movieId,title,genres
1,Toy Story (1995),Adventure|Animation|Children
2,Jumanji (1995),Adventure|Children|Fantasy
""")

    (data / "ratings.csv").write_text("""userId,movieId,rating,timestamp
1,1,4.0,964982703
1,2,3.5,964982226
2,1,5.0,964982224
""")

    return data


def test_data_component_instantiation():
    """DataComponent can be instantiated."""
    component = DataComponent(name="data_ingestion")
    assert component.name == "data_ingestion"
    assert component.schedule == "@once"


def test_data_component_has_run_method():
    """DataComponent has run method."""
    component = DataComponent(name="data_ingestion")
    assert hasattr(component, "run")
    assert callable(component.run)


def test_data_component_validates_input(tmp_path):
    """DataComponent validates input directory."""
    component = DataComponent(name="data_ingestion")

    # Should raise error if directory missing
    with pytest.raises(FileNotFoundError):
        component.run(tmp_path / "nonexistent")
