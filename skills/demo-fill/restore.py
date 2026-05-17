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

    if not backup_dir.exists():
        print("❌ No backups found. Skeleton code may already be restored.")
        return

    print("=" * 60)
    print("Restoring Skeleton Code")
    print("=" * 60)
    print()

    # Restore original files
    print("🔄 Restoring from backups...")
    for file in ["features.py", "training.py", "evaluation.py", "serving.py"]:
        src = backup_dir / file
        dst = components_dir / file
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  ✓ Restored {file}")

    print()
    print("=" * 60)
    print("✅ Skeleton code restored!")
    print("=" * 60)
    print()
    print("The example code is back to its placeholder state.")
    print("To activate demo again:  make demo")
    print()


if __name__ == "__main__":
    main()
