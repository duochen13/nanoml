import os
import urllib.request
import zipfile
from pathlib import Path
from typing import Union


MOVIELENS_URL = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"


def download_movielens(output_dir: Path):
    """Download and extract MovieLens dataset.

    Downloads ml-latest-small (~1MB) which contains:
    - movies.csv: ~9000 movies
    - ratings.csv: ~100000 ratings

    Args:
        output_dir: Directory to extract data files
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    zip_path = output_dir / "movielens.zip"

    # Download
    print(f"Downloading MovieLens from {MOVIELENS_URL}...")
    urllib.request.urlretrieve(MOVIELENS_URL, zip_path)

    # Extract
    print(f"Extracting to {output_dir}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Extract specific files
        for file_name in ["movies.csv", "ratings.csv"]:
            # Files are in ml-latest-small/ subdirectory
            source_name = f"ml-latest-small/{file_name}"
            target_path = output_dir / file_name

            with zip_ref.open(source_name) as source:
                target_path.write_bytes(source.read())

    # Clean up zip
    zip_path.unlink()

    print(f"✓ Dataset ready at {output_dir}")


def download_kaggle_dataset(
    dataset: str,
    output_dir: Union[str, Path],
    unzip: bool = True
) -> Path:
    """Download dataset from Kaggle.

    Requires Kaggle API credentials to be configured:
    1. Create API token at https://www.kaggle.com/account
    2. Place kaggle.json in ~/.kaggle/ (Unix) or %USERPROFILE%/.kaggle/ (Windows)

    Or set environment variables:
    - KAGGLE_USERNAME
    - KAGGLE_KEY

    Args:
        dataset: Kaggle dataset identifier (e.g., "username/dataset-name")
        output_dir: Directory to download dataset to
        unzip: Whether to unzip downloaded files

    Returns:
        Path to downloaded dataset directory

    Raises:
        ImportError: If kaggle package not installed
        OSError: If Kaggle credentials not found

    Examples:
        download_kaggle_dataset("grouplens/movielens-20m-dataset", "data/")
        download_kaggle_dataset("netflix-inc/netflix-prize-data", "data/netflix")
    """
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except ImportError:
        raise ImportError(
            "Kaggle package not installed. Install with: pip install kaggle"
        )

    # Verify credentials exist
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    has_env = os.getenv("KAGGLE_USERNAME") and os.getenv("KAGGLE_KEY")

    if not kaggle_json.exists() and not has_env:
        raise OSError(
            "Kaggle credentials not found. Please:\n"
            "1. Go to https://www.kaggle.com/account\n"
            "2. Click 'Create New API Token'\n"
            "3. Place kaggle.json in ~/.kaggle/ directory\n"
            "OR set KAGGLE_USERNAME and KAGGLE_KEY environment variables"
        )

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize Kaggle API
    api = KaggleApi()
    api.authenticate()

    print(f"Downloading Kaggle dataset: {dataset}")
    print(f"Destination: {output_dir}")

    # Download dataset
    api.dataset_download_files(
        dataset,
        path=str(output_dir),
        unzip=unzip
    )

    print(f"✓ Downloaded Kaggle dataset to {output_dir}")
    return output_dir


if __name__ == "__main__":
    # Allow running as script
    from pathlib import Path
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--kaggle":
        # Download from Kaggle
        dataset = sys.argv[2] if len(sys.argv) > 2 else "grouplens/movielens-20m-dataset"
        print(f"Downloading from Kaggle: {dataset}")
        download_kaggle_dataset(dataset, Path(__file__).parent)
    else:
        # Default: download from URL
        download_movielens(Path(__file__).parent)
