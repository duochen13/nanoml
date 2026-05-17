"""API Gateway routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import requests

router = APIRouter()


class RecommendationRequest(BaseModel):
    """Recommendation request format."""
    user_id: str
    top_n: int = 10


class RecommendationResponse(BaseModel):
    """Recommendation response format."""
    user_id: str
    recommendations: List[Dict[str, Any]]


@router.get("/recommend")
async def get_recommendations(user_id: str, top_n: int = 10):
    """
    Get recommendations for a user.

    For MVP, returns dummy recommendations.
    Plan 4 will implement actual recommendation logic.
    """
    # Dummy implementation for MVP
    recommendations = [
        {"item_id": f"item_{i}", "score": 0.9 - (i * 0.1)}
        for i in range(top_n)
    ]

    return {
        "user_id": user_id,
        "recommendations": recommendations
    }
