"""Model bakeoff endpoint — run same text through all installed engines."""

import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from .synthesize import _run_synthesis_job, _jobs

router = APIRouter()

# Bakeoff aggregations
_bakeoffs: dict[str, dict] = {}

# Engines participating in bakeoff
BAKEOFF_ENGINE_PRESETS = {
    "f5tts": "mark_rocky_tutor_warm",
    "chatterbox": "mark_chatterbox_storytelling",
    "voxcpm2": "mark_voxcpm2_clone",
}


class BakeoffRequest(BaseModel):
    text: str
    mixPreset: str = "rocky_live"
    bakeoffId: str | None = None


class BakeoffResponse(BaseModel):
    bakeoffId: str
    status: str
    jobs: list[dict]
    createdAt: str
    updatedAt: str


@router.post("/bakeoff")
async def bakeoff(req: BakeoffRequest, background_tasks: BackgroundTasks):
    bid = req.bakeoffId or f"bake_{uuid.uuid4().hex[:8]}"
    now = datetime.utcnow().isoformat()

    jobs_meta = []
    for engine, preset in BAKEOFF_ENGINE_PRESETS.items():
        job_id = f"{bid}_{engine}"
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
            preset,
            req.mixPreset,
        )
        jobs_meta.append({"jobId": job_id, "engine": engine, "preset": preset, "status": "queued"})

    _bakeoffs[bid] = {
        "bakeoffId": bid,
        "status": "running",
        "jobs": jobs_meta,
        "createdAt": now,
        "updatedAt": now,
    }

    return {"bakeoffId": bid, "status": "running", "jobs": jobs_meta}


@router.get("/bakeoff/status/{bakeoff_id}")
async def bakeoff_status(bakeoff_id: str):
    bake = _bakeoffs.get(bakeoff_id)
    if not bake:
        return {"bakeoffId": bakeoff_id, "status": "not_found", "jobs": []}

    # Aggregate latest job statuses
    all_completed = True
    any_failed = False
    updated_jobs = []
    for j in bake["jobs"]:
        job = _jobs.get(j["jobId"], {})
        j["status"] = job.get("status", "unknown")
        j["audioUrl"] = job.get("audioUrl")
        j["metrics"] = job.get("metrics")
        j["error"] = job.get("error")
        updated_jobs.append(j)
        if j["status"] not in ("completed", "failed"):
            all_completed = False
        if j["status"] == "failed":
            any_failed = True

    bake["jobs"] = updated_jobs
    if all_completed:
        bake["status"] = "completed"
    elif any_failed:
        bake["status"] = "partial_failure"

    return bake
