"""Parser for extracting lineage from MLflow code."""

import re
from pathlib import Path
from typing import List
from .base import BaseParser, LineageNode, LineageEdge, LineageRelationType


class MLflowParser(BaseParser):
    """Extract lineage from MLflow tracking code."""

    def can_parse(self, file_path: str) -> bool:
        """Check if this file uses MLflow."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                return any(pattern in content for pattern in [
                    'import mlflow',
                    'from mlflow',
                    'mlflow.log_model',
                    'mlflow.start_run'
                ])
        except:
            return False

    def parse_file(self, file_path: str) -> tuple[List[LineageNode], List[LineageEdge]]:
        """Parse MLflow file and extract model lineage."""
        nodes = []
        edges = []

        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Create node for the training script itself
            script_name = Path(file_path).stem
            script_id = f"mlflow_script_{script_name}"
            script_node = LineageNode(
                id=script_id,
                name=script_name,
                type="training_script",
                metadata={"file_path": file_path}
            )
            nodes.append(script_node)

            # Extract mlflow.log_model calls
            logged_models = self._extract_log_model(content, file_path)
            nodes.extend(logged_models)
            for model_node in logged_models:
                edges.append(LineageEdge(
                    source_id=script_id,
                    target_id=model_node.id,
                    relation_type=LineageRelationType.PRODUCES,
                    metadata={"operation": "log_model"}
                ))

            # Extract mlflow.load_model calls
            loaded_models = self._extract_load_model(content, file_path)
            nodes.extend(loaded_models)
            for model_node in loaded_models:
                edges.append(LineageEdge(
                    source_id=model_node.id,
                    target_id=script_id,
                    relation_type=LineageRelationType.CONSUMES,
                    metadata={"operation": "load_model"}
                ))

            # Extract mlflow.log_artifact calls (datasets, plots, etc.)
            artifacts = self._extract_log_artifact(content, file_path)
            nodes.extend(artifacts)
            for artifact_node in artifacts:
                edges.append(LineageEdge(
                    source_id=script_id,
                    target_id=artifact_node.id,
                    relation_type=LineageRelationType.PRODUCES,
                    metadata={"operation": "log_artifact"}
                ))

        except Exception as e:
            print(f"Error parsing MLflow file {file_path}: {e}")

        return nodes, edges

    def _extract_log_model(self, content: str, file_path: str) -> List[LineageNode]:
        """Extract mlflow.log_model calls."""
        nodes = []

        # Pattern: mlflow.sklearn.log_model(model, "model_name")
        # Pattern: mlflow.pytorch.log_model(model, "model_name")
        # Pattern: mlflow.tensorflow.log_model(model, "model_name")
        log_model_pattern = r'mlflow\.(\w+)\.log_model\([^,]+,\s*["\']([^"\']+)["\']\)'

        for match in re.finditer(log_model_pattern, content):
            framework = match.group(1)
            model_name = match.group(2)

            nodes.append(LineageNode(
                id=f"mlflow_model_{model_name}",
                name=model_name,
                type="mlflow_model",
                metadata={
                    "model_name": model_name,
                    "framework": framework,
                    "source_file": file_path
                }
            ))

        return nodes

    def _extract_load_model(self, content: str, file_path: str) -> List[LineageNode]:
        """Extract mlflow.load_model calls."""
        nodes = []

        # Pattern: mlflow.sklearn.load_model("models:/model_name/version")
        load_model_pattern = r'mlflow\.(\w+)\.load_model\(["\']([^"\']+)["\']\)'

        for match in re.finditer(load_model_pattern, content):
            framework = match.group(1)
            model_uri = match.group(2)

            # Extract model name from URI
            if "models:/" in model_uri:
                model_name = model_uri.split("/")[1]
            else:
                model_name = model_uri

            nodes.append(LineageNode(
                id=f"mlflow_model_{model_name}",
                name=model_name,
                type="mlflow_model",
                metadata={
                    "model_uri": model_uri,
                    "framework": framework,
                    "source_file": file_path
                }
            ))

        return nodes

    def _extract_log_artifact(self, content: str, file_path: str) -> List[LineageNode]:
        """Extract mlflow.log_artifact calls."""
        nodes = []

        # Pattern: mlflow.log_artifact("path/to/file")
        artifact_pattern = r'mlflow\.log_artifact\(["\']([^"\']+)["\']\)'

        for match in re.finditer(artifact_pattern, content):
            artifact_path = match.group(1)
            artifact_name = Path(artifact_path).name

            nodes.append(LineageNode(
                id=f"mlflow_artifact_{artifact_name}",
                name=artifact_name,
                type="mlflow_artifact",
                metadata={
                    "path": artifact_path,
                    "source_file": file_path
                }
            ))

        return nodes
