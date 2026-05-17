"""Local model serving server."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import torch
import numpy as np
from pathlib import Path

app = FastAPI(title="NanoML Model Server")


class PredictionRequest(BaseModel):
    """Prediction request format."""
    features: List[List[float]]
    model_name: str = "default"


class PredictionResponse(BaseModel):
    """Prediction response format."""
    predictions: List[float]
    model_name: str


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Make predictions using loaded model.

    For MVP, returns dummy predictions.
    Plan 4 will implement actual model loading.
    """
    # Dummy implementation for MVP
    predictions = [0.5] * len(request.features)

    return PredictionResponse(
        predictions=predictions,
        model_name=request.model_name
    )


@app.get("/models")
async def list_models():
    """List available models."""
    return {"models": ["default"]}
