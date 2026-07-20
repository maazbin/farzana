"""Extract promises/ideas on session close (single-user vault)."""

from __future__ import annotations

import json
import re

from openai import OpenAI

from farzana.core.config import Settings
from farzana.services import vault as vault_io


def extract_and_store(settings: Settings, session_text: str, session_title: str) -> str:
    if not settings.openai_api_key:
        return "Session closed (no OpenAI key for extract)."

    client = OpenAI(api_key=settings.openai_api_key)
    prompt = f"""From this session note, extract JSON with keys:
promises: array of {{title, detail}} open commitments
ideas: array of strings
people: array of names mentioned

Session title: {session_title}
Content:
{session_text[:8000]}

Return ONLY valid JSON."""
    resp = client.chat.completions.create(
        model=settings.openai_chat_model,
        messages=[
            {"role": "system", "content": "You extract structured memory. JSON only."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=800,
    )
    raw = (resp.choices[0].message.content or "").strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return f"Session closed. (Could not parse extract.)\n{raw[:300]}"

    notes = []
    for p in data.get("promises") or []:
        title = p.get("title") or "promise"
        detail = p.get("detail") or title
        path = vault_io.write_promise(settings.vault_path, title, detail)
        notes.append(f"promise: {path.name}")
    for idea in data.get("ideas") or []:
        vault_io.append_inbox(settings.vault_path, f"[idea] {idea}", source="extract")
        notes.append(f"idea: {idea[:60]}")
    people = data.get("people") or []
    if people:
        notes.append("people: " + ", ".join(people[:10]))
    return "Session closed. Saved: " + ("; ".join(notes) if notes else "nothing structured")
