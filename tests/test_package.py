import nanorec


def test_version_exists():
    """Package should have a __version__ attribute."""
    assert hasattr(nanorec, "__version__")
    assert isinstance(nanorec.__version__, str)
    assert len(nanorec.__version__) > 0
