"""Standalone CLI wrapper for Chatterbox TTS (runs in separate Python 3.10 venv)."""

import argparse
import sys
from pathlib import Path

from chatterbox import ChatterboxTTS


def main():
    parser = argparse.ArgumentParser(description="Chatterbox TTS CLI wrapper")
    parser.add_argument("--text", required=True)
    parser.add_argument("--reference", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--preset", default="neutral")
    parser.add_argument("--device", default="mps")
    args = parser.parse_args()

    ref_path = Path(args.reference)
    if not ref_path.exists():
        print(f"Reference audio not found: {ref_path}", file=sys.stderr)
        sys.exit(1)

    tts = ChatterboxTTS.from_pretrained(device=args.device)
    tts.load_voice(ref_path)

    preset_map = {
        "neutral": {"exaggeration": 1.0, "cfg_weight": 1.5},
        "storytelling": {"exaggeration": 0.8, "cfg_weight": 0.4},
        "audiobook": {"exaggeration": 0.6, "cfg_weight": 0.3},
        "expressive": {"exaggeration": 1.5, "cfg_weight": 2.0},
    }
    settings = preset_map.get(args.preset, preset_map["neutral"])

    wav = tts.generate(text=args.text, **settings)
    tts.save(wav, args.output)
    print(args.output)


if __name__ == "__main__":
    main()
