"""Voice Foundry API server."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import synthesize, master, health, presets, qc

app = FastAPI(
    title="MindSong Voice Foundry",
    version="0.1.0",
    description="Production voice engine for RockyAI Tutor, Skybeam, and agent-native content generation.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/voice", tags=["health"])
app.include_router(presets.router, prefix="/voice", tags=["presets"])
app.include_router(synthesize.router, prefix="/voice", tags=["synthesize"])
app.include_router(master.router, prefix="/voice", tags=["master"])
app.include_router(qc.router, prefix="/voice", tags=["qc"])


@app.get("/")
async def root():
    return {"service": "mindsong-voice-foundry", "version": "0.1.0"}
