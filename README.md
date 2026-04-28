# MindSong Voice Foundry

Production voice engine for RockyAI Tutor, Skybeam, and agent-native content generation.

## Architecture

- **Foundry repo** (this repo): Python/FastAPI voice engine — inference, mastering, QC, bakeoff.
- **Runtime repo** (`mindsong-juke-hub`): Thin TypeScript integration layer — HTTP client, preset registry, provenance.
- **Protocol**: Local HTTP service on `localhost:8788`.

## Quick Start

```bash
# Setup
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start server
./scripts/start_server.sh

# Test
curl http://localhost:8788/voice/health
curl -X POST http://localhost:8788/voice/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text":"RockyAI tutor is online.","preset":"mark_rocky_tutor_warm"}'
```

## Service Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/voice/health` | GET | Service health + GPU status |
| `/voice/presets` | GET | List voice presets |
| `/voice/synthesize` | POST | Generate voice from preset |
| `/voice/master` | POST | Apply mastering chain |
| `/voice/qc` | POST | Quality control scan |
| `/voice/bakeoff` | POST | Run model comparison |

## Directory Layout

```
src/
  engine/         # F5-TTS, Chatterbox, VoxCPM2, ElevenLabs wrappers
  post/           # FFmpeg mastering pipeline + loudness
  dataset/        # Source ingestion + reference builder
  bakeoff/        # Model comparison runner
  presets/        # Voice preset registry
  provenance/     # Disclosure, watermark, audit log
  api/            # FastAPI routes
voices/
  mark/           # Mark's voice dataset
artifacts/        # Generated outputs
tools/            # CLI utilities
```

## License

Internal use only. All generated voice outputs require AI-generated disclosure.
