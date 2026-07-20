"""Speech-to-text via OpenAI Whisper."""

from __future__ import annotations

from pathlib import Path

from openai import OpenAI

from farzana.core.config import Settings


def transcribe_file(settings: Settings, audio_path: Path) -> str:
    if not settings.openai_api_key:
        return ""
    client = OpenAI(api_key=settings.openai_api_key)
    with audio_path.open("rb") as f:
        result = client.audio.transcriptions.create(
            model=settings.openai_stt_model,
            file=f,
        )
    return (result.text or "").strip()
