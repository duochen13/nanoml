"""Workflow API router"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from .models import (
    Workflow,
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowsResponse,
)
from .service import WorkflowService
from .constants import get_config

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("/config")
async def get_workflow_config():
    """
    Get workflow configuration (node types, categories, statuses, etc.)
    Frontend fetches this to populate UI - single source of truth
    """
    return get_config()


@router.post("", response_model=Workflow, status_code=201)
async def create_workflow(workflow: WorkflowCreate):
    """Create a new workflow"""
    try:
        return WorkflowService.create_workflow(workflow)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=WorkflowsResponse)
async def list_workflows(
    status: Optional[str] = Query(None, description="Filter by status"),
    pipeline_type: Optional[str] = Query(None, description="Filter by pipeline type"),
    owner: Optional[str] = Query(None, description="Filter by owner"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    limit: int = Query(50, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
):
    """
    List workflows with filtering and pagination

    Query parameters:
    - status: Filter by workflow status (draft, active, archived)
    - pipeline_type: Filter by pipeline type (batch, streaming, inference, feature)
    - owner: Filter by owner
    - search: Search in workflow name and description
    - limit: Results per page (default: 50, max: 100)
    - offset: Pagination offset (default: 0)
    """
    try:
        return WorkflowService.list_workflows(
            status=status,
            pipeline_type=pipeline_type,
            owner=owner,
            search=search,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}", response_model=Workflow)
async def get_workflow(workflow_id: str):
    """Get workflow by ID"""
    workflow = WorkflowService.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@router.patch("/{workflow_id}", response_model=Workflow)
async def update_workflow(workflow_id: str, workflow_update: WorkflowUpdate):
    """Update workflow (partial update)"""
    workflow = WorkflowService.update_workflow(workflow_id, workflow_update)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(workflow_id: str):
    """Delete workflow"""
    deleted = WorkflowService.delete_workflow(workflow_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return None


@router.post("/{workflow_id}/duplicate", response_model=Workflow, status_code=201)
async def duplicate_workflow(
    workflow_id: str,
    new_name: str = Query(..., description="Name for the duplicated workflow"),
):
    """Duplicate an existing workflow"""
    workflow = WorkflowService.duplicate_workflow(workflow_id, new_name)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow
