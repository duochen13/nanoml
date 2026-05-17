import ast
from pathlib import Path
from typing import Any
from jinja2 import Environment, FileSystemLoader
from .base import BaseGenerator


class FlinkJobGenerator(BaseGenerator):
    """Generates Flink streaming jobs from feature definitions."""

    def __init__(self):
        """Initialize generator with Jinja2 environment."""
        template_dir = Path(__file__).parent / "templates"
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))

    def parse_source(self, source_path: Path) -> dict[str, Any]:
        """Parse features/definitions.py to extract FeatureGroups.

        Args:
            source_path: Path to features/definitions.py

        Returns:
            {
                "feature_groups": [
                    {
                        "name": "user_features",
                        "entity": "user_id",
                        "source": "kafka://user_events",
                        "features": [
                            {"name": "age", "type": "int"},
                            {"name": "country", "type": "string"}
                        ]
                    }
                ]
            }
        """
        code = source_path.read_text()
        tree = ast.parse(code)

        feature_groups = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                # Look for: var_name = FeatureGroup(...)
                if len(node.targets) == 1 and isinstance(node.value, ast.Call):
                    call = node.value
                    if (isinstance(call.func, ast.Name) and
                        call.func.id == "FeatureGroup"):

                        fg_data = self._parse_feature_group(node.targets[0].id, call)
                        feature_groups.append(fg_data)

        return {"feature_groups": feature_groups}

    def _parse_feature_group(self, var_name: str, call: ast.Call) -> dict[str, Any]:
        """Parse a FeatureGroup(...) call node."""
        fg = {"name": var_name, "features": []}

        for keyword in call.keywords:
            if keyword.arg == "name":
                fg["name"] = ast.literal_eval(keyword.value)
            elif keyword.arg == "entity":
                fg["entity"] = ast.literal_eval(keyword.value)
            elif keyword.arg == "source":
                fg["source"] = ast.literal_eval(keyword.value)
            elif keyword.arg == "features":
                # List of Feature(...) calls
                if isinstance(keyword.value, ast.List):
                    for feat_call in keyword.value.elts:
                        if isinstance(feat_call, ast.Call):
                            feat_name = ast.literal_eval(feat_call.args[0])
                            feat_type = ast.literal_eval(feat_call.args[1])
                            fg["features"].append({
                                "name": feat_name,
                                "type": feat_type
                            })

        return fg

    def generate_code(self, parsed_data: dict[str, Any]) -> str:
        """Generate Flink job code from parsed feature groups.

        Args:
            parsed_data: Output from parse_source()

        Returns:
            Generated Python code as string
        """
        template = self.jinja_env.get_template("flink_job.py.j2")
        return template.render(**parsed_data)

    def get_output_path(self, project_root: Path) -> Path:
        """Get output path for Flink job.

        Args:
            project_root: Root directory of NanoRec project

        Returns:
            .nanorec/generated/flink/streaming_features.py
        """
        return project_root / ".nanorec" / "generated" / "flink" / "streaming_features.py"
