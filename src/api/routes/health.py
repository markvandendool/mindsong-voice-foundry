"""Health check endpoint."""

import torch
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health():
    gpu_available = torch.cuda.is_available() or torch.backends.mps.is_available()
    gpu_name = None
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
    elif torch.backends.mps.is_available():
        gpu_name = "Apple Silicon MPS"

    return {
        "status": "healthy",
        "gpuAvailable": gpu_available,
        "gpuName": gpu_name,
        "modelsLoaded": {},
        "cacheSize": 0,
    }
