"""Centralized configuration loader.

Keeping environment access in one place avoids hidden config dependencies
throughout the project and makes local setup easier to reason about.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Runtime settings for local-only execution."""

    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1:70b")
    whisper_model: str = os.getenv("WHISPER_MODEL", "base")
    context_dir: str = os.getenv("CONTEXT_DIR", "./context")
    audio_sample_rate: int = int(os.getenv("AUDIO_SAMPLE_RATE", "16000"))
    recordings_dir: str = os.getenv("RECORDINGS_DIR", "./voice_recordings")
    piper_model_path: str = os.getenv("PIPER_MODEL_PATH", "")


settings = Settings()
