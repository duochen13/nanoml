"""Workflow service layer - all database operations"""
import json
import uuid
from typing import List, Optional
from datetime import datetime

from .models import (
    Workflow,
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowListItem,
    WorkflowsResponse,
    WorkflowDAG,
)
from .db import get_db_connection


class WorkflowService:
    """Service for workflow CRUD operations"""

    @staticmethod
    def create_workflow(workflow_create: WorkflowCreate) -> Workflow:
        """Create a new workflow"""
        workflow_id = str(uuid.uuid4())
        dag_json_str = workflow_create.dag_json.model_dump_json()
        metadata_str = json.dumps(workflow_create.metadata) if workflow_create.metadata else None

        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO workflows (id, name, description, dag_json, owner, pipeline_type, status, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    workflow_id,
                    workflow_create.name,
                    workflow_create.description,
                    dag_json_str,
                    workflow_create.owner,
                    workflow_create.pipeline_type,
                    workflow_create.status,
                    metadata_str,
                ),
            )

            # Fetch and return the created workflow
            row = conn.execute("SELECT * FROM workflows WHERE id = ?", (workflow_id,)).fetchone()
            return WorkflowService._row_to_workflow(row)

    @staticmethod
    def get_workflow(workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID"""
        with get_db_connection() as conn:
            row = conn.execute("SELECT * FROM workflows WHERE id = ?", (workflow_id,)).fetchone()
            if not row:
                return None
            return WorkflowService._row_to_workflow(row)

    @staticmethod
    def list_workflows(
        status: Optional[str] = None,
        pipeline_type: Optional[str] = None,
        owner: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> WorkflowsResponse:
        """List workflows with filtering and pagination"""
        conditions = []
        params = []

        if status:
            conditions.append("status = ?")
            params.append(status)
        if pipeline_type:
            conditions.append("pipeline_type = ?")
            params.append(pipeline_type)
        if owner:
            conditions.append("owner = ?")
            params.append(owner)
        if search:
            conditions.append("(name LIKE ? OR description LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        with get_db_connection() as conn:
            # Get total count
            count_row = conn.execute(
                f"SELECT COUNT(*) as total FROM workflows WHERE {where_clause}", params
            ).fetchone()
            total = count_row["total"]

            # Get paginated results
            rows = conn.execute(
                f"""
                SELECT * FROM workflows
                WHERE {where_clause}
                ORDER BY updated_at DESC
                LIMIT ? OFFSET ?
                """,
                params + [limit, offset],
            ).fetchall()

            workflows = [WorkflowService._row_to_list_item(row) for row in rows]

            return WorkflowsResponse(
                workflows=workflows,
                total=total,
                limit=limit,
                offset=offset,
            )

    @staticmethod
    def update_workflow(workflow_id: str, workflow_update: WorkflowUpdate) -> Optional[Workflow]:
        """Update workflow"""
        # Build dynamic update query
        updates = []
        params = []

        if workflow_update.name is not None:
            updates.append("name = ?")
            params.append(workflow_update.name)
        if workflow_update.description is not None:
            updates.append("description = ?")
            params.append(workflow_update.description)
        if workflow_update.dag_json is not None:
            updates.append("dag_json = ?")
            params.append(workflow_update.dag_json.model_dump_json())
        if workflow_update.pipeline_type is not None:
            updates.append("pipeline_type = ?")
            params.append(workflow_update.pipeline_type)
        if workflow_update.status is not None:
            updates.append("status = ?")
            params.append(workflow_update.status)
        if workflow_update.metadata is not None:
            updates.append("metadata = ?")
            params.append(json.dumps(workflow_update.metadata))

        if not updates:
            # No updates provided, just return current
            return WorkflowService.get_workflow(workflow_id)

        params.append(workflow_id)
        update_clause = ", ".join(updates)

        with get_db_connection() as conn:
            conn.execute(
                f"UPDATE workflows SET {update_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                params,
            )

            # Return updated workflow
            return WorkflowService.get_workflow(workflow_id)

    @staticmethod
    def delete_workflow(workflow_id: str) -> bool:
        """Delete workflow"""
        with get_db_connection() as conn:
            cursor = conn.execute("DELETE FROM workflows WHERE id = ?", (workflow_id,))
            return cursor.rowcount > 0

    @staticmethod
    def duplicate_workflow(workflow_id: str, new_name: str) -> Optional[Workflow]:
        """Duplicate an existing workflow"""
        original = WorkflowService.get_workflow(workflow_id)
        if not original:
            return None

        new_workflow = WorkflowCreate(
            name=new_name,
            description=original.description,
            dag_json=original.dag_json,
            owner=original.owner,
            pipeline_type=original.pipeline_type,
            status="draft",  # Always create duplicates as draft
            metadata=original.metadata,
        )

        return WorkflowService.create_workflow(new_workflow)

    # Helper methods

    @staticmethod
    def _row_to_workflow(row) -> Workflow:
        """Convert database row to Workflow model"""
        dag_json = WorkflowDAG(**json.loads(row["dag_json"]))
        metadata = json.loads(row["metadata"]) if row["metadata"] else None

        return Workflow(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            dag_json=dag_json,
            owner=row["owner"],
            pipeline_type=row["pipeline_type"],
            status=row["status"],
            metadata=metadata,
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    @staticmethod
    def _row_to_list_item(row) -> WorkflowListItem:
        """Convert database row to WorkflowListItem"""
        dag_json = json.loads(row["dag_json"])
        node_count = len(dag_json.get("nodes", []))

        return WorkflowListItem(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            owner=row["owner"],
            pipeline_type=row["pipeline_type"],
            status=row["status"],
            node_count=node_count,
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
