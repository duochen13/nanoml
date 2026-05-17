import ast
from pathlib import Path
from typing import Any
from jinja2 import Environment, FileSystemLoader
from .base import BaseGenerator


class AirflowDAGGenerator(BaseGenerator):
    """Generates Airflow DAG from NanoRec components."""

    def __init__(self):
        """Initialize generator with Jinja2 environment."""
        template_dir = Path(__file__).parent / "templates"
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))

    def parse_source(self, source_path: Path) -> dict[str, Any]:
        """Parse component definitions to extract DAG structure.

        Args:
            source_path: Path to components file (e.g., pipeline.py)

        Returns:
            {
                "components": [
                    {
                        "name": "data_ingestion",
                        "type": "DataComponent",
                        "schedule": "@daily",
                        "depends_on": []
                    }
                ]
            }
        """
        code = source_path.read_text()
        tree = ast.parse(code)

        components = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                if len(node.targets) == 1 and isinstance(node.value, ast.Call):
                    call = node.value
                    if (isinstance(call.func, ast.Name) and
                        "Component" in call.func.id):

                        comp = self._parse_component(node.targets[0].id, call)
                        components.append(comp)

        return {"components": components}

    def _parse_component(self, var_name: str, call: ast.Call) -> dict[str, Any]:
        """Parse a Component(...) call node."""
        comp = {
            "name": var_name,
            "type": call.func.id,
            "schedule": "@daily",
            "depends_on": []
        }

        for keyword in call.keywords:
            if keyword.arg == "name":
                comp["name"] = ast.literal_eval(keyword.value)
            elif keyword.arg == "schedule":
                comp["schedule"] = ast.literal_eval(keyword.value)
            elif keyword.arg == "depends_on":
                # List of variable references
                if isinstance(keyword.value, ast.List):
                    for dep_node in keyword.value.elts:
                        if isinstance(dep_node, ast.Name):
                            comp["depends_on"].append(dep_node.id)

        return comp

    def generate_code(self, parsed_data: dict[str, Any]) -> str:
        """Generate Airflow DAG from parsed components.

        Args:
            parsed_data: Output from parse_source()

        Returns:
            Generated Python code as string
        """
        template = self.jinja_env.get_template("airflow_dag.py.j2")
        return template.render(**parsed_data)

    def get_output_path(self, project_root: Path) -> Path:
        """Get output path for Airflow DAG.

        Args:
            project_root: Root directory of NanoRec project

        Returns:
            .nanorec/generated/airflow/pipeline_dag.py
        """
        return project_root / ".nanorec" / "generated" / "airflow" / "pipeline_dag.py"
