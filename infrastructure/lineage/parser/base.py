"""Base parser interface for extracting lineage from code."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class LineageRelationType(str, Enum):
    """Types of lineage relationships."""
    READS = "reads"  # Component reads from source
    WRITES = "writes"  # Component writes to target
    DEPENDS_ON = "depends_on"  # Component depends on another component
    PRODUCES = "produces"  # Component produces an artifact
    CONSUMES = "consumes"  # Component consumes an artifact


@dataclass
class LineageEdge:
    """A lineage relationship between two components."""
    source_id: str
    target_id: str
    relation_type: LineageRelationType
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source": self.source_id,
            "target": self.target_id,
            "type": self.relation_type.value,
            "metadata": self.metadata
        }


@dataclass
class LineageNode:
    """A node in the lineage graph."""
    id: str
    name: str
    type: str  # e.g., "airflow_task", "spark_job", "s3_path", "mlflow_model"
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "metadata": self.metadata
        }


class BaseParser(ABC):
    """Abstract base class for lineage parsers."""

    @abstractmethod
    def parse_file(self, file_path: str) -> tuple[List[LineageNode], List[LineageEdge]]:
        """Parse a file and extract lineage information.

        Args:
            file_path: Path to the file to parse

        Returns:
            Tuple of (nodes, edges) representing the lineage graph
        """
        pass

    @abstractmethod
    def can_parse(self, file_path: str) -> bool:
        """Check if this parser can handle the given file.

        Args:
            file_path: Path to the file

        Returns:
            True if this parser can handle the file
        """
        pass
