"""Health check endpoint."""

import importlib
import torch
from fastapi import APIRouter

from src.engine.chatterbox_engine import CHATTERBOX_VENV_PYTHON

router = APIRouter()


def _engine_available(provider: str) -> bool:
    if provider == "f5tts":
        return True  # Always available via CLI
    if provider == "chatterbox":
        return CHATTERBOX_VENV_PYTHON.exists()
    if provider == "voxcpm2":
        try:
            importlib.import_module("voxcpm")
            return True
        except Exception:
            return False
    return False


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
        "gpuDevice": "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"),
        "engines": {
            "f5tts": _engine_available("f5tts"),
            "chatterbox": _engine_available("chatterbox"),
            "voxcpm2": _engine_available("voxcpm2"),
        },
        "modelsLoaded": {},
        "cacheSize": 0,
    }
