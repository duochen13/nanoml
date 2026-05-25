"""Parser for extracting lineage from Spark code."""

import ast
import re
from pathlib import Path
from typing import List, Optional
from .base import BaseParser, LineageNode, LineageEdge, LineageRelationType


class SparkParser(BaseParser):
    """Extract lineage from Spark job code."""

    def can_parse(self, file_path: str) -> bool:
        """Check if this is a Spark file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                # Look for Spark imports
                return any(pattern in content for pattern in [
                    'from pyspark',
                    'import pyspark',
                    'SparkSession',
                    'spark.read',
                    'spark.write'
                ])
        except:
            return False

    def parse_file(self, file_path: str) -> tuple[List[LineageNode], List[LineageEdge]]:
        """Parse Spark file and extract data lineage."""
        nodes = []
        edges = []

        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Create node for the job itself
            job_name = Path(file_path).stem
            job_id = f"spark_job_{job_name}"
            job_node = LineageNode(
                id=job_id,
                name=job_name,
                type="spark_job",
                metadata={"file_path": file_path}
            )
            nodes.append(job_node)

            # Parse read operations
            read_nodes = self._extract_reads(content, file_path)
            nodes.extend(read_nodes)
            for read_node in read_nodes:
                edges.append(LineageEdge(
                    source_id=read_node.id,
                    target_id=job_id,
                    relation_type=LineageRelationType.READS,
                    metadata={"operation": "read"}
                ))

            # Parse write operations
            write_nodes = self._extract_writes(content, file_path)
            nodes.extend(write_nodes)
            for write_node in write_nodes:
                edges.append(LineageEdge(
                    source_id=job_id,
                    target_id=write_node.id,
                    relation_type=LineageRelationType.WRITES,
                    metadata={"operation": "write"}
                ))

        except Exception as e:
            print(f"Error parsing Spark file {file_path}: {e}")

        return nodes, edges

    def _extract_reads(self, content: str, file_path: str) -> List[LineageNode]:
        """Extract data sources from spark.read operations."""
        nodes = []

        # Pattern 1: spark.read.parquet("path")
        parquet_pattern = r'spark\.read\.parquet\(["\']([^"\']+)["\']\)'
        for match in re.finditer(parquet_pattern, content):
            path = match.group(1)
            node_id = self._path_to_id(path)
            nodes.append(LineageNode(
                id=node_id,
                name=path,
                type="data_source",
                metadata={"path": path, "format": "parquet", "source_file": file_path}
            ))

        # Pattern 2: spark.read.csv("path")
        csv_pattern = r'spark\.read\.csv\(["\']([^"\']+)["\']\)'
        for match in re.finditer(csv_pattern, content):
            path = match.group(1)
            node_id = self._path_to_id(path)
            nodes.append(LineageNode(
                id=node_id,
                name=path,
                type="data_source",
                metadata={"path": path, "format": "csv", "source_file": file_path}
            ))

        # Pattern 3: spark.read.json("path")
        json_pattern = r'spark\.read\.json\(["\']([^"\']+)["\']\)'
        for match in re.finditer(json_pattern, content):
            path = match.group(1)
            node_id = self._path_to_id(path)
            nodes.append(LineageNode(
                id=node_id,
                name=path,
                type="data_source",
                metadata={"path": path, "format": "json", "source_file": file_path}
            ))

        # Pattern 4: spark.read.table("table_name")
        table_pattern = r'spark\.read\.table\(["\']([^"\']+)["\']\)'
        for match in re.finditer(table_pattern, content):
            table_name = match.group(1)
            nodes.append(LineageNode(
                id=f"table_{table_name}",
                name=table_name,
                type="table",
                metadata={"table_name": table_name, "source_file": file_path}
            ))

        return nodes

    def _extract_writes(self, content: str, file_path: str) -> List[LineageNode]:
        """Extract data sinks from spark.write operations."""
        nodes = []

        # Pattern 1: df.write.parquet("path")
        parquet_pattern = r'\.write\.parquet\(["\']([^"\']+)["\']\)'
        for match in re.finditer(parquet_pattern, content):
            path = match.group(1)
            node_id = self._path_to_id(path)
            nodes.append(LineageNode(
                id=node_id,
                name=path,
                type="data_sink",
                metadata={"path": path, "format": "parquet", "source_file": file_path}
            ))

        # Pattern 2: df.write.csv("path")
        csv_pattern = r'\.write\.csv\(["\']([^"\']+)["\']\)'
        for match in re.finditer(csv_pattern, content):
            path = match.group(1)
            node_id = self._path_to_id(path)
            nodes.append(LineageNode(
                id=node_id,
                name=path,
                type="data_sink",
                metadata={"path": path, "format": "csv", "source_file": file_path}
            ))

        # Pattern 3: df.write.saveAsTable("table_name")
        table_pattern = r'\.write\.saveAsTable\(["\']([^"\']+)["\']\)'
        for match in re.finditer(table_pattern, content):
            table_name = match.group(1)
            nodes.append(LineageNode(
                id=f"table_{table_name}",
                name=table_name,
                type="table",
                metadata={"table_name": table_name, "source_file": file_path}
            ))

        return nodes

    def _path_to_id(self, path: str) -> str:
        """Convert a file path to a node ID."""
        # Handle S3 paths
        if path.startswith("s3://"):
            return f"s3_{path.replace('s3://', '').replace('/', '_')}"
        # Handle GCS paths
        elif path.startswith("gs://"):
            return f"gcs_{path.replace('gs://', '').replace('/', '_')}"
        # Handle local paths
        else:
            return f"path_{path.replace('/', '_')}"
