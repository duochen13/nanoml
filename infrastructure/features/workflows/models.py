"""Workflow data models"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class NodeConfig(BaseModel):
    """Configuration for a workflow node"""
    pass  # Dynamic config based on node type


class WorkflowNode(BaseModel):
    """A node in the workflow DAG"""
    id: str
    type: str  # Matches NODE_TYPES keys
    position: Dict[str, float]  # {x: float, y: float}
    data: Dict[str, Any]  # {label: str, config: {...}}


class WorkflowEdge(BaseModel):
    """An edge connecting nodes in the workflow"""
    id: str
    source: str  # source node id
    target: str  # target node id
    sourceHandle: Optional[str] = None
    targetHandle: Optional[str] = None


class WorkflowDAG(BaseModel):
    """Complete workflow DAG structure"""
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]


class WorkflowBase(BaseModel):
    """Base workflow model"""
    name: str
    description: Optional[str] = None
    pipeline_type: str = "batch"
    owner: str = "default"
    status: str = "draft"


class WorkflowCreate(WorkflowBase):
    """Create workflow request"""
    dag_json: WorkflowDAG
    metadata: Optional[Dict[str, Any]] = None


class WorkflowUpdate(BaseModel):
    """Update workflow request - all fields optional"""
    name: Optional[str] = None
    description: Optional[str] = None
    dag_json: Optional[WorkflowDAG] = None
    pipeline_type: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Workflow(WorkflowBase):
    """Complete workflow model"""
    id: str
    dag_json: WorkflowDAG
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkflowListItem(BaseModel):
    """Workflow summary for list view"""
    id: str
    name: str
    description: Optional[str]
    owner: str
    pipeline_type: str
    status: str
    node_count: int  # Computed from dag_json
    created_at: datetime
    updated_at: datetime


class WorkflowsResponse(BaseModel):
    """Paginated workflows response"""
    workflows: List[WorkflowListItem]
    total: int
    limit: int
    offset: int
