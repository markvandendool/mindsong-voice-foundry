"""QC scan endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel

from src.post.mix_chain import measure_loudness

router = APIRouter()


class QCRequest(BaseModel):
    audioPath: str


class QCResponse(BaseModel):
    pass_: bool
    metrics: dict
    issues: list[str]


@router.post("/qc", response_model=QCResponse)
async def qc_scan(req: QCRequest):
    metrics = measure_loudness(req.audioPath)
    issues = []

    if metrics.get("integrated_lufs", 0) > -10:
        issues.append("Too loud: integrated LUFS > -10")
    if metrics.get("true_peak_db", 0) > -0.5:
        issues.append("True peak too high: > -0.5 dB")
    if metrics.get("lra", 100) < 2:
        issues.append("Loudness range too narrow: < 2 LU")

    passed = len(issues) == 0
    return QCResponse(pass_=passed, metrics=metrics, issues=issues)
