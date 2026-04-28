"""Voice input listener using local Whisper transcription.

This module records microphone audio and transcribes it locally so the
interview loop can stay hands-free without any cloud API calls.
"""

import threading
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf
from faster_whisper import WhisperModel

from config import settings


class WhisperListener:
    """Handles one-shot record + transcribe calls for answers."""

    def __init__(self) -> None:
        # Use GPU if available, fallback to CPU
        device = "cuda" if settings.cuda_available else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"
        self.model = WhisperModel(settings.whisper_model, device=device, compute_type=compute_type)
        self.recordings_dir = Path(settings.recordings_dir)
        self.recordings_dir.mkdir(parents=True, exist_ok=True)

    def record_and_transcribe(self, seconds: int = 180) -> str:
        """Records audio until user presses Enter or max time reached."""
        sample_rate = settings.audio_sample_rate
        print(f"\nRecording... speak now. Press ENTER when done (max {seconds}s):")
        
        stop_event = threading.Event()
        
        def wait_for_enter():
            input()
            stop_event.set()
        
        # Start keyboard listener thread
        keyboard_thread = threading.Thread(target=wait_for_enter, daemon=True)
        keyboard_thread.start()
        
        # Record in chunks to allow early stopping
        chunk_size = int(sample_rate * 0.1)  # 100ms chunks
        max_chunks = int(seconds * 10)  # Total chunks for max duration
        recorded_chunks = []
        
        with sd.InputStream(samplerate=sample_rate, channels=1, dtype=np.float32) as stream:
            for _ in range(max_chunks):
                if stop_event.is_set():
                    break
                chunk, _ = stream.read(chunk_size)
                recorded_chunks.append(chunk)
            else:
                # Max time reached - give 500ms grace period for Enter key
                print("  (Time limit reached - press ENTER now to stop)")
                stop_event.wait(0.5)
        
        print("  Stopped recording.")
        
        # Concatenate and save
        audio = np.concatenate(recorded_chunks) if recorded_chunks else np.array([])
        wav_path = self.recordings_dir / "latest_answer.wav"
        sf.write(str(wav_path), audio, sample_rate)

        segments, _ = self.model.transcribe(str(wav_path))
        return " ".join([segment.text for segment in segments]).strip()
