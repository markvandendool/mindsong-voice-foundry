"""Voice synthesis endpoint with async job queue — multi-engine."""

import asyncio
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from src.engine.f5tts_engine import F5TTSEngine
from src.engine.chatterbox_engine import ChatterboxEngine
from src.engine.voxcpm2_engine import VoxCPM2Engine
from src.post.mix_chain import master_take
from src.presets.preset_defaults import PRESETS

router = APIRouter()

# Lazy-init engines
_engines: dict[str, object] = {}

# In-memory job store (replace with Redis for multi-worker)
_jobs: dict[str, dict] = {}


def _get_engine(provider: str):
    if provider not in _engines:
        if provider == "f5tts":
            _engines[provider] = F5TTSEngine()
        elif provider == "chatterbox":
            _engines[provider] = ChatterboxEngine()
        elif provider == "voxcpm2":
            _engines[provider] = VoxCPM2Engine()
    return _engines.get(provider)


class SynthesizeRequest(BaseModel):
    text: str
    preset: str = "mark_rocky_tutor_warm"
    persona: str = "rocky"
    quality: str = "production"
    mixPreset: str | None = None
    discloseAI: bool = True
    jobId: str | None = None


class JobStatusResponse(BaseModel):
    jobId: str
    status: str
    audioUrl: str | None = None
    rawUrl: str | None = None
    provider: str | None = None
    preset: str | None = None
    metrics: dict | None = None
    error: str | None = None
    createdAt: str
    updatedAt: str


def _run_synthesis_job(job_id: str, text: str, preset_key: str, mix_preset: str):
    """Blocking worker for background synthesis + mastering."""
    try:
        _jobs[job_id]["status"] = "running"
        _jobs[job_id]["updatedAt"] = datetime.utcnow().isoformat()

        preset = PRESETS.get(preset_key, PRESETS["mark_rocky_tutor_warm"])
        provider = preset["provider"]

        base_dir = Path("artifacts/voice/mark")
        base_dir.mkdir(parents=True, exist_ok=True)
        raw_path = base_dir / f"{job_id}.raw.wav"
        mastered_path = base_dir / f"{job_id}.mastered.wav"

        engine = _get_engine(provider)
        if engine is None:
            raise NotImplementedError(f"Provider {provider} not yet implemented in Foundry.")

        if provider == "f5tts":
            asyncio.run(
                engine.synthesize(
                    text=text,
                    ref_audio=preset["reference"],
                    output_path=str(raw_path),
                    speed=preset.get("speed", 1.0),
                    remove_silence=True,
                )
            )
        elif provider == "chatterbox":
            asyncio.run(
                engine.synthesize(
                    text=text,
                    ref_audio=preset["reference"],
                    output_path=str(raw_path),
                    preset=preset.get("emotion", "neutral"),
                )
            )
        elif provider == "voxcpm2":
            asyncio.run(
                engine.synthesize(
                    text=text,
                    ref_audio=preset.get("reference"),
                    output_path=str(raw_path),
                    voice_design=preset.get("voiceDesign"),
                )
            )

        metrics = master_take(str(raw_path), str(mastered_path), mix_preset)

        _jobs[job_id].update({
            "status": "completed",
            "audioUrl": f"/static/voice/mark/{mastered_path.name}",
            "rawUrl": f"/static/voice/mark/{raw_path.name}",
            "provider": provider,
            "preset": preset_key,
            "metrics": metrics,
            "updatedAt": datetime.utcnow().isoformat(),
        })
    except Exception as exc:
        _jobs[job_id].update({
            "status": "failed",
            "error": str(exc),
            "updatedAt": datetime.utcnow().isoformat(),
        })


@router.post("/synthesize")
async def synthesize(req: SynthesizeRequest, background_tasks: BackgroundTasks):
    job_id = req.jobId or f"voice_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow().isoformat()

    preset = PRESETS.get(req.preset, PRESETS["mark_rocky_tutor_warm"])
    mix_preset = req.mixPreset or preset.get("mixPreset", "rocky_live")

    _jobs[job_id] = {
        "jobId": job_id,
        "status": "queued",
        "createdAt": now,
        "updatedAt": now,
    }

    background_tasks.add_task(
        _run_synthesis_job,
        job_id,
        req.text,
        req.preset,
        mix_preset,
    )

    return {"jobId": job_id, "status": "queued", "pollUrl": f"/voice/synthesize/status/{job_id}"}


@router.get("/synthesize/status/{job_id}", response_model=JobStatusResponse)
async def synthesize_status(job_id: str):
    job = _jobs.get(job_id)
    if not job:
        return JobStatusResponse(
            jobId=job_id,
            status="not_found",
            createdAt=datetime.utcnow().isoformat(),
            updatedAt=datetime.utcnow().isoformat(),
        )
    return JobStatusResponse(**job)
