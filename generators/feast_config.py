import ast
from pathlib import Path
from typing import Any, Literal
from jinja2 import Environment, FileSystemLoader
from .base import BaseGenerator


class FeastConfigGenerator(BaseGenerator):
    """Generates Feast configuration from feature definitions."""

    def __init__(self, output_type: Literal["store", "features"] = "store"):
        """Initialize generator.

        Args:
            output_type: "store" for feature_store.yaml, "features" for features.py
        """
        self.output_type = output_type
        template_dir = Path(__file__).parent / "templates"
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))

    def parse_source(self, source_path: Path) -> dict[str, Any]:
        """Parse features/definitions.py to extract entities and feature views.

        Args:
            source_path: Path to features/definitions.py

        Returns:
            {
                "entities": [{"name": "user_id"}, {"name": "item_id"}],
                "feature_views": [
                    {
                        "name": "user_features",
                        "entity": "user_id",
                        "features": [{"name": "age", "type": "int"}]
                    }
                ]
            }
        """
        code = source_path.read_text()
        tree = ast.parse(code)

        entities_set = set()
        feature_views = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                if len(node.targets) == 1 and isinstance(node.value, ast.Call):
                    call = node.value
                    if (isinstance(call.func, ast.Name) and
                        call.func.id == "FeatureGroup"):

                        view = self._parse_feature_view(node.targets[0].id, call)
                        feature_views.append(view)
                        entities_set.add(view["entity"])

        entities = [{"name": e} for e in sorted(entities_set)]

        return {
            "entities": entities,
            "feature_views": feature_views
        }

    def _parse_feature_view(self, var_name: str, call: ast.Call) -> dict[str, Any]:
        """Parse a FeatureGroup(...) call into Feast FeatureView."""
        view = {"name": var_name, "features": []}

        for keyword in call.keywords:
            if keyword.arg == "name":
                view["name"] = ast.literal_eval(keyword.value)
            elif keyword.arg == "entity":
                view["entity"] = ast.literal_eval(keyword.value)
            elif keyword.arg == "features":
                if isinstance(keyword.value, ast.List):
                    for feat_call in keyword.value.elts:
                        if isinstance(feat_call, ast.Call):
                            feat_name = ast.literal_eval(feat_call.args[0])
                            feat_type = ast.literal_eval(feat_call.args[1])
                            view["features"].append({
                                "name": feat_name,
                                "type": feat_type
                            })

        return view

    def generate_code(self, parsed_data: dict[str, Any]) -> str:
        """Generate Feast config from parsed data.

        Args:
            parsed_data: Output from parse_source()

        Returns:
            Generated YAML or Python code as string
        """
        if self.output_type == "store":
            template = self.jinja_env.get_template("feast_store.yaml.j2")
        else:
            template = self.jinja_env.get_template("feast_features.py.j2")

        return template.render(**parsed_data)

    def get_output_path(self, project_root: Path) -> Path:
        """Get output path for Feast config.

        Args:
            project_root: Root directory of NanoRec project

        Returns:
            Path to feature_store.yaml or features.py
        """
        feast_dir = project_root / ".nanorec" / "generated" / "feast"

        if self.output_type == "store":
            return feast_dir / "feature_store.yaml"
        else:
            return feast_dir / "features.py"
