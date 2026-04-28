"""Voice synthesis endpoint."""

import os
import uuid
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

from src.engine.f5tts_engine import F5TTSEngine
from src.post.mix_chain import master_take
from src.presets.preset_defaults import PRESETS

router = APIRouter()

# Lazy-init engine
_f5_engine = None


def get_f5_engine():
    global _f5_engine
    if _f5_engine is None:
        _f5_engine = F5TTSEngine()
    return _f5_engine


class SynthesizeRequest(BaseModel):
    text: str
    preset: str = "mark_rocky_tutor_warm"
    persona: str = "rocky"
    quality: str = "production"
    mixPreset: str | None = None
    discloseAI: bool = True
    jobId: str | None = None


class SynthesizeResponse(BaseModel):
    audioPath: str
    rawPath: str
    provider: str
    preset: str
    metrics: dict


@router.post("/synthesize", response_model=SynthesizeResponse)
async def synthesize(req: SynthesizeRequest):
    preset = PRESETS.get(req.preset, PRESETS["mark_rocky_tutor_warm"])
    provider = preset["provider"]
    mix_preset = req.mixPreset or preset.get("mixPreset", "rocky_live")
    job_id = req.jobId or f"voice_{uuid.uuid4().hex[:12]}"

    base_dir = Path("artifacts/voice/mark")
    base_dir.mkdir(parents=True, exist_ok=True)

    raw_path = base_dir / f"{job_id}.raw.wav"
    mastered_path = base_dir / f"{job_id}.mastered.wav"

    if provider == "f5tts":
        engine = get_f5_engine()
        ref_audio = preset["reference"]
        await engine.synthesize(
            text=req.text,
            ref_audio=ref_audio,
            output_path=str(raw_path),
        )
    else:
        raise NotImplementedError(f"Provider {provider} not yet implemented in Foundry.")

    # Mastering pass
    metrics = master_take(str(raw_path), str(mastered_path), mix_preset)

    return SynthesizeResponse(
        audioPath=str(mastered_path),
        rawPath=str(raw_path),
        provider=provider,
        preset=req.preset,
        metrics=metrics,
    )
