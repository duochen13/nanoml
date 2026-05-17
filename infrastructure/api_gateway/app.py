"""NanoRec API Gateway."""

from fastapi import FastAPI
from infrastructure.api_gateway.routes import router

app = FastAPI(title="NanoRec API Gateway")

app.include_router(router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "NanoRec API Gateway",
        "version": "0.1.0",
        "docs": "/docs"
    }
