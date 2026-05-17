import nanoml


def test_version_exists():
    """Package should have a __version__ attribute."""
    assert hasattr(nanoml, "__version__")
    assert isinstance(nanoml.__version__, str)
    assert len(nanoml.__version__) > 0
