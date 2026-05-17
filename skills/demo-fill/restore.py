#!/usr/bin/env python3
"""Restore skeleton code from backups."""

import shutil
from pathlib import Path


def main():
    """Restore skeleton code from backups."""
    project_root = Path(__file__).parent.parent.parent
    example_dir = project_root / "examples" / "movie_recommendations"
    components_dir = example_dir / "components"
    backup_dir = example_dir / ".backup"
    data_dir = example_dir / "data"

    if not backup_dir.exists():
        print("❌ No backups found. Skeleton code may already be restored.")
        return

    print("=" * 60)
    print("Restoring Skeleton Code")
    print("=" * 60)
    print()

    # Restore original files
    print("🔄 Restoring Python files from backups...")
    for file in ["features.py", "training.py", "evaluation.py", "serving.py"]:
        src = backup_dir / file
        dst = components_dir / file
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  ✓ Restored {file}")

    print()

    # Clean up generated data artifacts
    print("🧹 Cleaning up generated artifacts...")
    artifacts = [
        data_dir / "ratings.csv",          # Downloaded dataset
        data_dir / "movies.csv",           # Downloaded dataset
        data_dir / "user_features.csv",    # Computed features
        data_dir / "model.pkl",            # Trained model
        data_dir / "test_data.csv",        # Test split
    ]

    for artifact in artifacts:
        if artifact.exists():
            artifact.unlink()
            print(f"  ✓ Removed {artifact.name}")

    # Remove backup directory
    print()
    print("🗑️  Removing backup directory...")
    shutil.rmtree(backup_dir)
    print("  ✓ Removed .backup/")

    print()
    print("=" * 60)
    print("✅ Skeleton code and artifacts restored!")
    print("=" * 60)
    print()
    print("The example is back to its pristine state:")
    print("  • Python code restored to skeleton")
    print("  • All generated data files removed")
    print("  • Backup directory cleaned up")
    print()
    print("To activate demo again:  make demo")
    print()


if __name__ == "__main__":
    main()
