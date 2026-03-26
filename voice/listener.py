"""Voice input listener using local Whisper transcription.

This module records microphone audio and transcribes it locally so the
interview loop can stay hands-free without any cloud API calls.
"""

from pathlib import Path

import sounddevice as sd
import soundfile as sf
import whisper

from config import settings


class WhisperListener:
    """Handles one-shot record + transcribe calls for answers."""

    def __init__(self) -> None:
        self.model = whisper.load_model(settings.whisper_model)
        self.recordings_dir = Path(settings.recordings_dir)
        self.recordings_dir.mkdir(parents=True, exist_ok=True)

    def record_and_transcribe(self, seconds: int = 45) -> str:
        """Records audio for a fixed window and returns transcript text."""
        sample_rate = settings.audio_sample_rate
        print(f"\nRecording for up to {seconds}s... speak now.")
        audio = sd.rec(int(seconds * sample_rate), samplerate=sample_rate, channels=1)
        sd.wait()

        wav_path = self.recordings_dir / "latest_answer.wav"
        sf.write(str(wav_path), audio, sample_rate)

        result = self.model.transcribe(str(wav_path))
        return result.get("text", "").strip()
