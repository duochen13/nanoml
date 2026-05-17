import pytest
from pathlib import Path
from data.download import download_movielens


def test_download_movielens(tmp_path):
    """download_movielens() fetches and extracts MovieLens 100K."""
    download_movielens(tmp_path)

    # Should have movies and ratings
    assert (tmp_path / "movies.csv").exists()
    assert (tmp_path / "ratings.csv").exists()

    # Verify format
    movies = (tmp_path / "movies.csv").read_text()
    assert "movieId,title,genres" in movies

    ratings = (tmp_path / "ratings.csv").read_text()
    assert "userId,movieId,rating,timestamp" in ratings


def test_movies_csv_format(tmp_path):
    """movies.csv has expected columns and data."""
    download_movielens(tmp_path)

    movies_file = tmp_path / "movies.csv"
    lines = movies_file.read_text().strip().split('\n')

    # Header
    assert lines[0] == "movieId,title,genres"

    # Sample row
    assert len(lines) > 100  # At least 100 movies


def test_ratings_csv_format(tmp_path):
    """ratings.csv has expected columns and data."""
    download_movielens(tmp_path)

    ratings_file = tmp_path / "ratings.csv"
    lines = ratings_file.read_text().strip().split('\n')

    # Header
    assert lines[0] == "userId,movieId,rating,timestamp"

    # Sample row
    assert len(lines) > 1000  # At least 1000 ratings
