"""Optional local text-to-speech via Piper.

This module is optional because some users prefer text-only output, and Piper
requires a local voice model file.
"""

import subprocess
from pathlib import Path

from config import settings


def speak(text: str) -> None:
    """Speaks text with Piper if configured; otherwise prints a notice."""
    model_path = settings.piper_model_path.strip()
    if not model_path:
        print("TTS skipped: set PIPER_MODEL_PATH in .env to enable.")
        return

    path = Path(model_path)
    if not path.exists():
        print(f"TTS skipped: Piper model not found at {path}.")
        return

    # Piper reads stdin text and writes audio to default output.
    subprocess.run(
        ["piper", "--model", str(path)],
        input=text.encode("utf-8"),
        check=False,
    )
