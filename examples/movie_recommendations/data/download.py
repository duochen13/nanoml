import urllib.request
import zipfile
from pathlib import Path


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


if __name__ == "__main__":
    # Allow running as script
    from pathlib import Path
    download_movielens(Path(__file__).parent)
