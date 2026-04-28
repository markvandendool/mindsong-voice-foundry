"""Chatterbox TTS engine wrapper (subprocess into isolated Python 3.10 venv)."""

import asyncio
from pathlib import Path


CHATTERBOX_VENV_PYTHON = Path.home() / "mindsong-voice-foundry/.venv-chatterbox/bin/python"
CLI_PATH = Path(__file__).with_name("chatterbox_cli.py")


class ChatterboxEngine:
    """Wraps Chatterbox TTS via subprocess into its own Python 3.10 venv."""

    def __init__(self, device: str = "mps"):
        self.device = device

    async def synthesize(
        self,
        text: str,
        ref_audio: str,
        output_path: str,
        preset: str = "neutral",
    ) -> str:
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            str(CHATTERBOX_VENV_PYTHON),
            str(CLI_PATH),
            "--text", text,
            "--reference", ref_audio,
            "--output", str(output_path),
            "--preset", preset,
            "--device", self.device,
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            raise RuntimeError(f"Chatterbox failed: {stderr.decode()}")

        return str(out_path)
