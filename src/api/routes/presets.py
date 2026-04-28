"""Voice preset registry endpoint."""

from fastapi import APIRouter
from src.presets.preset_defaults import PRESETS

router = APIRouter()


@router.get("/presets")
async def list_presets():
    return {"presets": PRESETS}
