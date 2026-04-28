"""Mastering endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel

from src.post.mix_chain import master_take

router = APIRouter()


class MasterRequest(BaseModel):
    inputPath: str
    preset: str = "skybeam_youtube"
    outputPath: str | None = None


class MasterResponse(BaseModel):
    outputPath: str
    metrics: dict


@router.post("/master", response_model=MasterResponse)
async def master(req: MasterRequest):
    import uuid
    from pathlib import Path

    output = req.outputPath or f"artifacts/voice/mark/mastered/{uuid.uuid4().hex[:12]}.wav"
    Path(output).parent.mkdir(parents=True, exist_ok=True)

    metrics = master_take(req.inputPath, output, req.preset)
    return MasterResponse(outputPath=output, metrics=metrics)
