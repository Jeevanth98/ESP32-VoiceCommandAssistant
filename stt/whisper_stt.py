"""
Whisper Speech-to-Text — CPU-friendly transcription
=====================================================
Wraps OpenAI Whisper for speech-to-text transcription.
Uses the 'base' model (~150 MB) by default for a good balance
between accuracy and CPU speed.

The model is loaded lazily on first use and cached in memory.
"""

from __future__ import annotations
import os
import tempfile
import numpy as np

from config import WHISPER_MODEL, AUDIO_SAMPLE_RATE


# ─── Lazy model singleton ───────────────────────────────────────────────────
_model = None


def _load_model():
    """Load the Whisper model (once) and cache it."""
    global _model
    if _model is not None:
        return _model

    print(f"  [WHISPER] Loading Whisper '{WHISPER_MODEL}' model …")
    import whisper
    _model = whisper.load_model(WHISPER_MODEL)
    print(f"  [WHISPER] Model loaded (device: cpu).")
    return _model


def transcribe_audio_bytes(
    pcm_bytes: bytes,
    sample_rate: int = AUDIO_SAMPLE_RATE,
    bit_depth: int = 16,
) -> str:
    """
    Transcribe raw PCM audio bytes to text.

    Parameters
    ----------
    pcm_bytes : bytes
        Raw PCM audio data (signed int16, mono, little-endian).
    sample_rate : int
        Sample rate of the audio (default: 16 kHz).
    bit_depth : int
        Bit depth (default: 16).

    Returns
    -------
    str
        Transcribed text (lowered, stripped).
    """
    if not pcm_bytes:
        return ""

    model = _load_model()

    # Convert raw PCM bytes → float32 numpy array normalised to [-1, 1]
    # Explicitly force Little-Endian 16-bit to match ESP32 output
    audio_np = np.frombuffer(pcm_bytes, dtype="<i2").astype(np.float32)
    audio_np /= 32768.0  # Normalise to [-1.0, 1.0] (max val of 16-bit signed int)

    # Whisper expects float32 at 16 kHz.  Resample if needed.
    if sample_rate != 16000:
        # Simple linear resampling (good enough for voice)
        duration = len(audio_np) / sample_rate
        num_samples_16k = int(duration * 16000)
        indices = np.linspace(0, len(audio_np) - 1, num_samples_16k).astype(int)
        audio_np = audio_np[indices]

    # Transcribe
    result = model.transcribe(
        audio_np,
        language="en",
        fp16=False,      # CPU mode — no half precision
    )

    text = result.get("text", "").strip()
    print(f"  [WHISPER] Transcribed: \"{text}\"")
    return text


def transcribe_wav_file(wav_path: str) -> str:
    """
    Transcribe a WAV file to text.
    Useful for testing without raw PCM bytes.
    """
    model = _load_model()
    result = model.transcribe(
        wav_path,
        language="en",
        fp16=False,
    )
    text = result.get("text", "").strip()
    print(f"  [WHISPER] Transcribed: \"{text}\"")
    return text
