"""F5-TTS inference engine wrapper."""

import asyncio
import subprocess
from pathlib import Path


class F5TTSEngine:
    """Wraps the f5-tts_infer-cli command for async generation."""

    def __init__(self):
        self.model = "F5TTS_v1_Base"

    async def synthesize(self, text: str, ref_audio: str, output_path: str) -> str:
        ref_path = Path(ref_audio)
        if not ref_path.is_absolute():
            ref_path = Path.cwd() / ref_audio

        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            "f5-tts_infer-cli",
            "--model", self.model,
            "--ref_audio", str(ref_path),
            "--ref_text", "",
            "--gen_text", text,
            "--output_dir", str(out_path.parent),
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            raise RuntimeError(f"F5-TTS failed: {stderr.decode()}")

        # f5-tts_infer-cli names output infer_cli_basic.wav in the output dir
        default_out = out_path.parent / "infer_cli_basic.wav"
        if default_out.exists() and str(default_out) != str(out_path):
            default_out.rename(out_path)

        return str(out_path)
