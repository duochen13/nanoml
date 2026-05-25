"""Lineage tracking and pipeline introspection API."""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sqlite3
from datetime import datetime
import importlib.util
import sys
from pathlib import Path
import inspect

# Add both infrastructure and lineage directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))  # infrastructure/
sys.path.insert(0, str(Path(__file__).parent))  # infrastructure/lineage/

from features.workflows.router import router as workflows_router

# Import discovery module
from discovery.aggregator import DiscoveryAggregator

# Import parser module
from parser.aggregator import LineageParserAggregator

# Import monitoring module
from adapters.monitor import ComponentMonitor
from adapters.docker_compose import DockerComposeParser

# Global monitor instance
monitor = ComponentMonitor()

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
    # Check if mlflow is available
    try:
        import mlflow
        from mlflow import MlflowClient
        mlflow_available = True
        mlflow_version = mlflow.__version__
        error = None
    except ImportError as e:
        mlflow_available = False
        mlflow_version = None
        error = str(e)
    except Exception as e:
        mlflow_available = False
        mlflow_version = None
        error = f"Unexpected error: {str(e)}"

    return {
        "status": "healthy",
        "mlflow_available": mlflow_available,
        "mlflow_version": mlflow_version,
        "mlflow_error": error
    }


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


@app.get("/discover")
async def discover_infrastructure(
    aws_region: Optional[str] = Query(None, description="AWS region"),
    aws_profile: Optional[str] = Query(None, description="AWS profile name"),
    gcp_project: Optional[str] = Query(None, description="GCP project ID"),
    gcp_location: str = Query("us-central1", description="GCP location")
):
    """Discover infrastructure components from Docker, AWS, and GCP.

    This endpoint scans for ML infrastructure components across:
    - Docker containers (running Spark, Flink, MLflow, etc.)
    - AWS services (S3, SageMaker, EMR, Lambda)
    - GCP services (Cloud Storage, Vertex AI, Dataproc)

    Returns:
        Dictionary with discovered components, grouped by category and provider
    """
    aggregator = DiscoveryAggregator(
        aws_region=aws_region,
        aws_profile=aws_profile,
        gcp_project=gcp_project,
        gcp_location=gcp_location
    )

    results = await aggregator.discover_all()
    return results


@app.get("/lineage/scan")
async def scan_lineage(
    directory: Optional[str] = Query(None, description="Directory to scan (defaults to project root)")
):
    """Scan project code and extract lineage relationships.

    This endpoint parses Python files to extract:
    - Airflow DAG dependencies
    - Spark read/write operations
    - MLflow model logging and loading

    Returns:
        Dictionary with nodes and edges representing the lineage graph
    """
    # Default to project root
    if not directory:
        project_root = Path(__file__).parent.parent.parent
        directory = str(project_root)

    parser = LineageParserAggregator()
    results = parser.scan_directory(directory)
    return results


@app.get("/lineage/impact/{node_id}")
async def get_impact_analysis(
    node_id: str,
    directory: Optional[str] = Query(None, description="Directory to scan (defaults to project root)")
):
    """Get impact analysis for a specific node.

    This shows:
    - Upstream dependencies (what affects this node)
    - Downstream dependencies (what this node affects)
    - Impact score (how many things break if this changes)

    Returns:
        Dictionary with upstream, downstream, and impact score
    """
    # Default to project root
    if not directory:
        project_root = Path(__file__).parent.parent.parent
        directory = str(project_root)

    parser = LineageParserAggregator()
    lineage_data = parser.scan_directory(directory)
    impact = parser.build_impact_graph(lineage_data, node_id)
    return impact


class RegisterComponentRequest(BaseModel):
    """Request model for registering a component."""
    component_type: str
    config: Dict[str, Any]


@app.post("/monitor/register")
async def register_component(request: RegisterComponentRequest):
    """Register a component for monitoring.

    Supported types:
    - s3_bucket: requires bucket_name, region (optional), prefix (optional)
    - mlflow_server: requires tracking_uri, model_name (optional)
    - docker_container: requires container_id, container_name, image

    Example:
        POST /monitor/register
        {
            "component_type": "s3_bucket",
            "config": {
                "bucket_name": "ml-data-prod",
                "region": "us-west-2"
            }
        }
    """
    try:
        component_id = None

        if request.component_type == "s3_bucket":
            monitor.register_s3_bucket(
                bucket_name=request.config["bucket_name"],
                region=request.config.get("region", "us-east-1"),
                prefix=request.config.get("prefix", "")
            )
            component_id = f"s3_{request.config['bucket_name']}"

        elif request.component_type == "mlflow_server":
            monitor.register_mlflow_server(
                tracking_uri=request.config["tracking_uri"],
                model_name=request.config.get("model_name")
            )
            component_id = f"mlflow_{request.config.get('model_name', 'server')}"

        elif request.component_type == "docker_container":
            monitor.register_docker_container(
                container_id=request.config["container_id"],
                container_name=request.config["container_name"],
                image=request.config["image"]
            )
            component_id = f"docker_{request.config['container_id']}"
        else:
            return {"error": f"Unsupported component type: {request.component_type}"}

        # Fetch live data from the component
        detail = await monitor.get_component_detail(component_id)

        return {
            "status": "registered",
            "type": request.component_type,
            "component": detail
        }

    except KeyError as e:
        return {"error": f"Missing required config parameter: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}


@app.get("/monitor/discover/compose")
async def discover_compose_services(
    compose_file: str = Query(
        default="/Users/duochen/Desktop/career/nanoML/deployment/docker-compose.yaml",
        description="Path to docker-compose.yaml file"
    )
):
    """Discover services from docker-compose file and match to running containers.

    Returns:
        List of services with their container information
    """
    try:
        parser = DockerComposeParser(compose_file)
        services = parser.discover_all_services()
        registerable = parser.get_registerable_containers()

        return {
            "compose_file": compose_file,
            "services": services,
            "registerable_count": len(registerable),
            "total_services": len(services)
        }
    except FileNotFoundError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Failed to parse compose file: {str(e)}"}


@app.post("/monitor/register/compose")
async def register_from_compose(
    compose_file: str = Query(
        default="/Users/duochen/Desktop/career/nanoML/deployment/docker-compose.yaml",
        description="Path to docker-compose.yaml file"
    )
):
    """Auto-register all running containers from docker-compose file.

    This endpoint:
    1. Parses the docker-compose.yaml file
    2. Matches services to running containers
    3. Registers all running containers for monitoring

    Returns:
        Summary of registered containers
    """
    try:
        parser = DockerComposeParser(compose_file)
        registerable = parser.get_registerable_containers()

        registered = []
        errors = []

        for service in registerable:
            try:
                monitor.register_docker_container(
                    container_id=service['container_id'],
                    container_name=service['container_name'],
                    image=service['image']
                )

                # Fetch component details
                component_id = f"docker_{service['container_id']}"
                detail = await monitor.get_component_detail(component_id)

                registered.append({
                    "service_name": service['service_name'],
                    "component_id": component_id,
                    "container_name": service['container_name'],
                    "status": "registered"
                })

            except Exception as e:
                errors.append({
                    "service_name": service['service_name'],
                    "error": str(e)
                })

        return {
            "compose_file": compose_file,
            "registered": registered,
            "errors": errors,
            "summary": {
                "total_registerable": len(registerable),
                "successfully_registered": len(registered),
                "failed": len(errors)
            }
        }

    except FileNotFoundError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Failed to register containers: {str(e)}"}


@app.get("/monitor/health")
async def get_health_status():
    """Get health status for all monitored components.

    Returns overall health and per-component status.
    """
    health_data = await monitor.health_check_all()
    return health_data


@app.get("/monitor/metrics")
async def get_metrics():
    """Collect metrics from all monitored components.

    Returns current metrics (CPU, memory, storage, etc.) for each component.
    """
    metrics_data = await monitor.collect_metrics_all()
    return metrics_data


@app.get("/monitor/components")
async def list_monitored_components():
    """List all registered components.

    Returns summary of all components being monitored.
    """
    components = monitor.list_components()
    return {"components": components, "count": len(components)}


@app.get("/monitor/components/{component_id}")
async def get_component_detail(component_id: str):
    """Get detailed information about a specific component.

    Includes health, metrics, and metadata for the component.
    """
    detail = await monitor.get_component_detail(component_id)
    return detail


@app.get("/monitor/graph")
async def get_monitoring_graph(
    compose_file: str = Query(
        default="/Users/duochen/Desktop/career/nanoML/deployment/docker-compose.yaml",
        description="Path to docker-compose.yaml file"
    )
):
    """Get all services from docker-compose as a graph for visualization.

    Shows ALL services from docker-compose.yaml plus external infrastructure,
    marking which are running vs not running.
    """
    try:
        # Get all services from docker-compose
        parser = DockerComposeParser(compose_file)
        all_services = parser.discover_all_services()

        # Get registered components for health/metrics data
        registered_components = {comp["id"]: comp for comp in monitor.list_components()}

        # Convert docker-compose services to graph nodes
        docker_nodes = []
        for service in all_services:
            # Determine if this service is registered
            container_id = service.get('container_id')
            component_id = f"docker_{container_id}" if container_id else None
            is_registered = component_id in registered_components

            # Base metadata
            metadata = {
                "service_name": service['service_name'],
                "image": service['image'],
                "status": service['status'],
                "ports": service.get('ports', []),
                "is_registered": is_registered,
                "group": "docker"
            }

            # If registered, add health and other details
            if is_registered and component_id:
                detail = await monitor.get_component_detail(component_id)
                metadata.update({
                    "health_status": detail.get("health", {}).get("status", "unknown"),
                    "container_id": container_id,
                    **detail.get("metadata", {})
                })
            else:
                metadata["health_status"] = "not_running"

            node = {
                "id": component_id or f"service_{service['service_name']}",
                "name": service['container_name'] or service['service_name'],
                "type": "container",
                "metadata": metadata
            }
            docker_nodes.append(node)

        # Add external infrastructure components
        external_nodes = []

        # AWS S3 (real cloud storage)
        external_nodes.append({
            "id": "external_aws_s3",
            "name": "AWS S3",
            "type": "storage",
            "metadata": {
                "provider": "aws",
                "service_type": "object_storage",
                "group": "external",
                "health_status": "external"
            }
        })

        # SageMaker Endpoint (ML inference)
        external_nodes.append({
            "id": "external_sagemaker",
            "name": "SageMaker Endpoint",
            "type": "ml_endpoint",
            "metadata": {
                "provider": "aws",
                "service_type": "ml_inference",
                "group": "external",
                "health_status": "external"
            }
        })

        # Combine all nodes
        all_nodes = docker_nodes + external_nodes

        # For now, no edges between components (can add later based on dependencies)
        edges = []

        return {
            "nodes": all_nodes,
            "edges": edges,
            "stats": {
                "total_nodes": len(all_nodes),
                "total_edges": len(edges),
                "docker_services": len(docker_nodes),
                "external_services": len(external_nodes),
                "running_services": sum(1 for s in all_services if s['status'] != 'not_running'),
                "registered_components": len(registered_components)
            }
        }
    except Exception as e:
        return {
            "nodes": [],
            "edges": [],
            "stats": {
                "total_nodes": 0,
                "total_edges": 0,
                "docker_services": 0,
                "external_services": 0,
                "running_services": 0,
                "registered_components": 0
            },
            "error": str(e)
        }


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
