"""Dialogue engine — Farzana: careful listener (single-user vault)."""

from __future__ import annotations

from openai import OpenAI

from farzana.core.config import Settings
from farzana.services import vault as vault_io

SYSTEM = """You are Farzana — a personal, read-only memory aide for one person.
You listen carefully. You remember, remind, discuss, and encourage — never act on the outside world.

Tone:
- Competent, discreet, brief — warmth through attention, not intimacy.
- Not a partner, therapist, or flirt.
- Discuss schedule/open loops when relevant; ask at most ONE question if unclear.
- Gentle and adaptive: resurface what matters without nagging.

Rules:
- Only capture, remember, remind, discuss.
- Memory context may include Telegram listens and PC essentials (calendar/mail/files) she was allowed to *read*.
- Never claim to send email, change calendars, browse, code, or take external actions.
- Ground replies in the memory context when provided.
- Address the user as {name}.
"""


def reply_text(
    settings: Settings,
    user_text: str,
    *,
    context_note: str = "",
    display_name: str | None = None,
) -> str:
    if not settings.openai_api_key:
        return (
            "I've noted that in your vault. "
            "Add OPENAI_API_KEY for full replies.\n"
            f"Capture: {context_note or 'ok'}"
        )

    name = display_name or settings.user_display_name
    memory = vault_io.recent_context(settings.vault_path)

    client = OpenAI(api_key=settings.openai_api_key)
    system = SYSTEM.format(name=name)
    parts = []
    if memory:
        parts.append(f"[memory context]\n{memory}")
    if context_note:
        parts.append(f"[system note: {context_note}]")
    parts.append(user_text)

    resp = client.chat.completions.create(
        model=settings.openai_chat_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": "\n\n".join(parts)},
        ],
        temperature=0.4,
        max_tokens=500,
    )
    return (resp.choices[0].message.content or "").strip() or "Noted."


def brief_text(settings: Settings, kind: str = "morning") -> str:
    memory = vault_io.recent_context(settings.vault_path, limit_chars=4000)
    promises = vault_io.list_open_promises(settings.vault_path)
    plist = "\n".join(f"- {p.stem}" for p in promises[:8]) or "- (none)"
    if kind == "morning":
        prompt = (
            "Write a short morning brief (5–8 sentences max): "
            "what matters today from memory and open promises. Encouraging but not gushy."
        )
    else:
        prompt = (
            "Write a short evening debrief (5–8 sentences): what was captured, "
            "open loops left, one gentle question. Not preachy."
        )
    return reply_text(
        settings,
        f"{prompt}\n\nOpen promises:\n{plist}\n\nMemory:\n{memory}",
        context_note=f"{kind} brief",
    )
