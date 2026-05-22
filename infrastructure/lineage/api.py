"""Lineage tracking and pipeline introspection API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sqlite3
from datetime import datetime
import importlib.util
import sys
from pathlib import Path
import inspect

# Import workflows feature router
sys.path.insert(0, str(Path(__file__).parent.parent))
from features.workflows.router import router as workflows_router

app = FastAPI(title="NanoML Lineage API")

# Enable CORS for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include feature routers
app.include_router(workflows_router, prefix="/api")


class Artifact(BaseModel):
    """Artifact model."""
    id: Optional[int] = None
    name: str
    type: str
    path: Optional[str] = None
    created_at: Optional[datetime] = None


class PipelineStage(BaseModel):
    """Pipeline stage model."""
    name: str
    type: str
    depends_on: List[str]
    schedule: Optional[str] = None


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy"}


@app.get("/artifacts")
async def list_artifacts():
    """List all artifacts."""
    # SHALLOW: Returns empty list for MVP
    return {"artifacts": []}


@app.post("/artifacts")
async def create_artifact(artifact: Artifact):
    """Create artifact."""
    # SHALLOW: No-op for MVP
    return {"id": 1, **artifact.dict()}


@app.get("/pipeline")
async def get_pipeline():
    """Introspect and return pipeline DAG structure."""
    try:
        # Find the example project (or user project in production)
        project_root = Path(__file__).parent.parent.parent
        components_dir = project_root / "examples" / "movie_recommendations" / "components"

        if not components_dir.exists():
            return {
                "training_pipeline": [],
                "serving_pipeline": [],
                "error": "No pipeline components found"
            }

        training_stages = []
        serving_stages = []

        # Component files to check
        component_files = {
            "data_ingestion": "Data Ingestion",
            "features": "Feature Computation",
            "training": "Model Training",
            "evaluation": "Model Evaluation",
            "serving": "Model Serving"
        }

        for file_name, display_name in component_files.items():
            component_file = components_dir / f"{file_name}.py"
            if not component_file.exists():
                continue

            try:
                # Load the module
                spec = importlib.util.spec_from_file_location(file_name, component_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Find the component class
                for item_name in dir(module):
                    item = getattr(module, item_name)
                    if inspect.isclass(item) and item_name.endswith("Component"):
                        # Try to instantiate to get metadata
                        try:
                            instance = item(name=display_name)
                            stage = {
                                "name": display_name,
                                "type": file_name,
                                "depends_on": getattr(instance, "depends_on", []),
                                "schedule": getattr(instance, "schedule", None)
                            }

                            # Categorize into training or serving pipeline
                            if file_name == "serving":
                                serving_stages.append(stage)
                            else:
                                training_stages.append(stage)
                        except:
                            pass
                        break
            except Exception as e:
                print(f"Error loading {file_name}: {e}")
                continue

        # Build dependency graph for training pipeline
        training_dag = build_dag(training_stages)

        # Serving pipeline is separate (real-time)
        serving_dag = [
            {
                "name": "User Request",
                "type": "input",
                "icon": "👤",
                "description": "Incoming traffic",
                "color": "#e8eaf6",
                "borderColor": "#5c6bc0"
            },
            {
                "name": "Feature Store",
                "type": "feature_fetch",
                "icon": "🗄️",
                "description": "Fetch features (Feast)",
                "color": "#fff3e0",
                "borderColor": "#ff9800"
            },
            {
                "name": "Model Serving",
                "type": "serving",
                "icon": "🚀",
                "description": "Inference endpoint",
                "color": "#fce4ec",
                "borderColor": "#e91e63"
            },
            {
                "name": "Response",
                "type": "output",
                "icon": "✨",
                "description": "Predictions returned",
                "color": "#f1f8e9",
                "borderColor": "#8bc34a"
            }
        ]

        return {
            "training_pipeline": training_dag,
            "serving_pipeline": serving_dag,
            "metadata": {
                "components_found": len(training_stages),
                "project": "movie_recommendations"
            }
        }

    except Exception as e:
        return {
            "training_pipeline": [],
            "serving_pipeline": [],
            "error": str(e)
        }


def build_dag(stages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build DAG with icons and styling from component stages."""
    stage_icons = {
        "data_ingestion": ("📊", "Raw Data", "Data ingestion", "#e3f2fd", "#2196f3"),
        "features": ("🗄️", "Feature Store", "Flink + Feast", "#fff3e0", "#ff9800"),
        "training": ("🧠", "Model Training", "Train & register (MLflow)", "#e8f5e9", "#4caf50"),
        "evaluation": ("📈", "Model Evaluation", "Metrics & validation", "#f3e5f5", "#9c27b0"),
    }

    # Add Data Processing stage if it's implied
    dag = [
        {
            "name": "Raw Data",
            "type": "data_ingestion",
            "icon": "📊",
            "description": "Data ingestion",
            "color": "#e3f2fd",
            "borderColor": "#2196f3"
        },
        {
            "name": "Data Processing",
            "type": "data_processing",
            "icon": "⚙️",
            "description": "Cleaning & transformation",
            "color": "#f3e5f5",
            "borderColor": "#9c27b0"
        }
    ]

    # Add stages based on what components exist
    for stage in stages:
        stage_type = stage["type"]
        if stage_type in stage_icons:
            icon, name, desc, color, border = stage_icons[stage_type]
            dag.append({
                "name": name,
                "type": stage_type,
                "icon": icon,
                "description": desc,
                "color": color,
                "borderColor": border
            })

    return dag
