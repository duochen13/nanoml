"""SHALLOW: Basic lineage tracking API."""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
from datetime import datetime

app = FastAPI(title="NanoRec Lineage API")


class Artifact(BaseModel):
    """Artifact model."""
    id: Optional[int] = None
    name: str
    type: str
    path: Optional[str] = None
    created_at: Optional[datetime] = None


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
