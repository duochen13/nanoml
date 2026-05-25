"""Parser for extracting lineage from Airflow DAGs."""

import ast
import re
from pathlib import Path
from typing import List, Dict, Any
from .base import BaseParser, LineageNode, LineageEdge, LineageRelationType


class AirflowParser(BaseParser):
    """Extract lineage from Airflow DAG files."""

    def can_parse(self, file_path: str) -> bool:
        """Check if this is an Airflow DAG file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                return any(pattern in content for pattern in [
                    'from airflow',
                    'import airflow',
                    'DAG(',
                    '@dag'
                ])
        except:
            return False

    def parse_file(self, file_path: str) -> tuple[List[LineageNode], List[LineageEdge]]:
        """Parse Airflow DAG and extract task dependencies."""
        nodes = []
        edges = []

        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Parse the Python AST
            tree = ast.parse(content)

            # Extract DAG information
            dag_info = self._extract_dag_info(tree, file_path)
            if dag_info:
                dag_node = LineageNode(
                    id=dag_info["id"],
                    name=dag_info["name"],
                    type="airflow_dag",
                    metadata=dag_info["metadata"]
                )
                nodes.append(dag_node)

                # Extract tasks
                tasks = self._extract_tasks(tree, content, file_path)
                nodes.extend(tasks)

                # Connect tasks to DAG
                for task_node in tasks:
                    edges.append(LineageEdge(
                        source_id=task_node.id,
                        target_id=dag_node.id,
                        relation_type=LineageRelationType.DEPENDS_ON,
                        metadata={"belongs_to": "dag"}
                    ))

                # Extract task dependencies
                task_deps = self._extract_task_dependencies(content, tasks)
                edges.extend(task_deps)

        except Exception as e:
            print(f"Error parsing Airflow DAG {file_path}: {e}")

        return nodes, edges

    def _extract_dag_info(self, tree: ast.AST, file_path: str) -> Dict[str, Any]:
        """Extract DAG name and metadata."""
        for node in ast.walk(tree):
            # Look for DAG instantiation: DAG(dag_id="name", ...)
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "DAG":
                    # Extract dag_id from arguments
                    dag_id = None
                    for keyword in node.keywords:
                        if keyword.arg == "dag_id":
                            if isinstance(keyword.value, ast.Constant):
                                dag_id = keyword.value.value

                    if dag_id:
                        return {
                            "id": f"airflow_dag_{dag_id}",
                            "name": dag_id,
                            "metadata": {"file_path": file_path}
                        }

        # If no explicit DAG found, use filename
        dag_name = Path(file_path).stem
        return {
            "id": f"airflow_dag_{dag_name}",
            "name": dag_name,
            "metadata": {"file_path": file_path}
        }

    def _extract_tasks(self, tree: ast.AST, content: str, file_path: str) -> List[LineageNode]:
        """Extract task definitions."""
        tasks = []

        # Pattern 1: PythonOperator, BashOperator, etc.
        operator_pattern = r'(\w+)\s*=\s*(\w+Operator)\('
        for match in re.finditer(operator_pattern, content):
            task_id = match.group(1)
            operator_type = match.group(2)

            tasks.append(LineageNode(
                id=f"airflow_task_{task_id}",
                name=task_id,
                type="airflow_task",
                metadata={
                    "operator": operator_type,
                    "source_file": file_path
                }
            ))

        # Pattern 2: @task decorator
        task_decorator_pattern = r'@task\s+def\s+(\w+)\('
        for match in re.finditer(task_decorator_pattern, content):
            task_name = match.group(1)

            tasks.append(LineageNode(
                id=f"airflow_task_{task_name}",
                name=task_name,
                type="airflow_task",
                metadata={
                    "operator": "TaskFlowAPI",
                    "source_file": file_path
                }
            ))

        return tasks

    def _extract_task_dependencies(self, content: str, tasks: List[LineageNode]) -> List[LineageEdge]:
        """Extract task dependencies (>> and <<)."""
        edges = []

        # Pattern: task1 >> task2
        dep_pattern_1 = r'(\w+)\s*>>\s*(\w+)'
        for match in re.finditer(dep_pattern_1, content):
            source_task = match.group(1)
            target_task = match.group(2)

            # Find matching nodes
            source_node = next((t for t in tasks if t.name == source_task), None)
            target_node = next((t for t in tasks if t.name == target_task), None)

            if source_node and target_node:
                edges.append(LineageEdge(
                    source_id=source_node.id,
                    target_id=target_node.id,
                    relation_type=LineageRelationType.DEPENDS_ON,
                    metadata={"dependency": "upstream"}
                ))

        # Pattern: task2 << task1 (reverse)
        dep_pattern_2 = r'(\w+)\s*<<\s*(\w+)'
        for match in re.finditer(dep_pattern_2, content):
            target_task = match.group(1)
            source_task = match.group(2)

            # Find matching nodes
            source_node = next((t for t in tasks if t.name == source_task), None)
            target_node = next((t for t in tasks if t.name == target_task), None)

            if source_node and target_node:
                edges.append(LineageEdge(
                    source_id=source_node.id,
                    target_id=target_node.id,
                    relation_type=LineageRelationType.DEPENDS_ON,
                    metadata={"dependency": "upstream"}
                ))

        return edges
