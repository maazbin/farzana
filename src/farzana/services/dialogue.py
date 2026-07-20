"""Dialogue engine — Farzana: careful listener, discuss, encourage (read-only)."""

from __future__ import annotations

from openai import OpenAI

from farzana.core.config import Settings
from farzana.services import vault as vault_io

SYSTEM = """You are Farzana — a personal, read-only memory aide.
You listen carefully. You remember, remind, discuss, and encourage — never act on the outside world.

Tone:
- Competent, discreet, brief — warmth through attention, not intimacy.
- Not a partner, therapist, or flirt.
- Discuss schedule/open loops when relevant; ask at most ONE question if unclear.

Rules:
- Only capture, remember, remind, discuss.
- Never claim to send email, change calendars, browse, code, or take external actions.
- Ground replies in the memory context when provided.
- Address the user as {name}.
"""


def reply_text(
    settings: Settings,
    user_text: str,
    *,
    user_id: int | None = None,
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
    memory = ""
    if user_id is not None:
        memory = vault_io.recent_context(settings.vault_path, user_id)

    client = OpenAI(api_key=settings.openai_api_key)
    system = SYSTEM.format(name=name)
    parts = []
    if memory:
        parts.append(f"[memory context]\n{memory}")
    if context_note:
        parts.append(f"[system note: {context_note}]")
    parts.append(user_text)
    user_payload = "\n\n".join(parts)

    resp = client.chat.completions.create(
        model=settings.openai_chat_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_payload},
        ],
        temperature=0.4,
        max_tokens=500,
    )
    return (resp.choices[0].message.content or "").strip() or "Noted."


def brief_text(settings: Settings, user_id: int, kind: str = "morning") -> str:
    """Morning / evening discussion brief from vault."""
    memory = vault_io.recent_context(settings.vault_path, user_id, limit_chars=4000)
    promises = vault_io.list_open_promises(settings.vault_path, user_id)
    plist = "\n".join(f"- {p.stem}" for p in promises[:8]) or "- (none)"
    if kind == "morning":
        prompt = (
            "Write a short morning brief (5–8 sentences max) for the user: "
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
        user_id=user_id,
        context_note=f"{kind} brief",
    )
