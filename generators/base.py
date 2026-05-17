from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseGenerator(ABC):
    """Abstract base class for all code generators.

    Implements template method pattern:
    1. parse_source() - Read and parse input files
    2. generate_code() - Apply templates to generate code
    3. get_output_path() - Determine where to write output
    4. run() - Orchestrate the process
    """

    @abstractmethod
    def parse_source(self, source_path: Path) -> dict[str, Any]:
        """Parse source file into structured data.

        Args:
            source_path: Path to source file to parse

        Returns:
            Parsed data as dictionary
        """
        pass

    @abstractmethod
    def generate_code(self, parsed_data: dict[str, Any]) -> str:
        """Generate code from parsed data.

        Args:
            parsed_data: Structured data from parse_source()

        Returns:
            Generated code as string
        """
        pass

    @abstractmethod
    def get_output_path(self, project_root: Path) -> Path:
        """Determine output file path.

        Args:
            project_root: Root directory of NanoRec project

        Returns:
            Path where generated code should be written
        """
        pass

    def run(self, source_path: Path, project_root: Path) -> Path:
        """Run the full generation process.

        Template method that orchestrates:
        1. Parse source
        2. Generate code
        3. Ensure output directory exists
        4. Write generated code

        Args:
            source_path: Path to source file
            project_root: Root directory of NanoRec project

        Returns:
            Path to generated file
        """
        # Parse
        parsed_data = self.parse_source(source_path)

        # Generate
        code = self.generate_code(parsed_data)

        # Determine output location
        output_path = self.get_output_path(project_root)

        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write
        output_path.write_text(code)

        return output_path
