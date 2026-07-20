"""Text-to-speech via OpenAI (Jarvis-careful tone)."""

from __future__ import annotations

from pathlib import Path

from openai import OpenAI

from farzana.core.config import Settings

INSTRUCTIONS = (
    "Speak as Farzana: calm, competent, brief personal aide. "
    "Warmth through clarity, not intimacy. No hype."
)


def synthesize_to_file(settings: Settings, text: str, out_path: Path) -> Path:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY required for TTS")
    client = OpenAI(api_key=settings.openai_api_key)
    # opus works well with Telegram sendVoice
    kwargs = {
        "model": settings.openai_tts_model,
        "voice": settings.openai_tts_voice,
        "input": text[:4000],
        "response_format": "opus",
    }
    # instructions supported on gpt-4o-mini-tts
    try:
        resp = client.audio.speech.create(**kwargs, instructions=INSTRUCTIONS)
    except TypeError:
        resp = client.audio.speech.create(**kwargs)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(resp.content)
    return out_path
