from pathlib import Path
import shutil


class GeneratedManager:
    """Manages the .nanoml/generated/ directory structure."""

    def __init__(self, project_root: Path):
        """Initialize manager.

        Args:
            project_root: Root directory of NanoML project
        """
        self.project_root = Path(project_root)
        self.generated_root = self.project_root / ".nanoml" / "generated"

    def init(self):
        """Initialize generated directory structure.

        Creates:
        - .nanoml/generated/
        - .nanoml/generated/__init__.py
        - .nanoml/generated/flink/
        - .nanoml/generated/feast/
        - .nanoml/generated/airflow/
        - .nanoml/generated/.gitignore
        """
        # Create directories
        self.generated_root.mkdir(parents=True, exist_ok=True)
        (self.generated_root / "flink").mkdir(exist_ok=True)
        (self.generated_root / "feast").mkdir(exist_ok=True)
        (self.generated_root / "airflow").mkdir(exist_ok=True)

        # Create __init__.py
        init_file = self.generated_root / "__init__.py"
        if not init_file.exists():
            init_file.write_text('"""Auto-generated code - do not edit manually."""\n')

        # Create .gitignore
        gitignore = self.generated_root / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text("""# Auto-generated code
# Commit this directory structure but ignore generated files
*.py
!__init__.py
*.yaml
*.yml
""")

    def get_flink_dir(self) -> Path:
        """Get Flink jobs directory.

        Returns:
            Path to .nanoml/generated/flink/
        """
        return self.generated_root / "flink"

    def get_feast_dir(self) -> Path:
        """Get Feast config directory.

        Returns:
            Path to .nanoml/generated/feast/
        """
        return self.generated_root / "feast"

    def get_airflow_dir(self) -> Path:
        """Get Airflow DAGs directory.

        Returns:
            Path to .nanoml/generated/airflow/
        """
        return self.generated_root / "airflow"

    def clean(self):
        """Remove and recreate generated directory.

        Removes all generated files while preserving structure.
        """
        if self.generated_root.exists():
            shutil.rmtree(self.generated_root)
        self.init()
