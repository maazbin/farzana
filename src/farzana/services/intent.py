"""
Semantic intent for text + voice transcripts.

Users should not need slash commands. We map natural phrases to modes:
  listen · stop · close · quiet · brief · note · discuss

Rules first (fast, free). Optional tiny LLM fallback when ambiguous
while listen mode is on or the phrase looks command-like.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass

from farzana.core.config import Settings

log = logging.getLogger(__name__)

# Slash commands still work (Telegram-style)
_SLASH_LISTEN = re.compile(
    r"^/listen(?:@\w+)?(?:\s+(.+))?$",
    re.IGNORECASE,
)
_SLASH_STOP = re.compile(r"^/(?:stop|stoplisten)(?:@\w+)?\s*$", re.IGNORECASE)
_SLASH_CLOSE = re.compile(r"^/close(?:@\w+)?(?:\s+(.+))?$", re.IGNORECASE)
_SLASH_NOTE = re.compile(r"^/note(?:@\w+)?\s+(.+)$", re.IGNORECASE | re.DOTALL)
_SLASH_BRIEF = re.compile(r"^/brief(?:@\w+)?\s*$", re.IGNORECASE)
_SLASH_QUIET = re.compile(r"^/quiet(?:@\w+)?\s*$", re.IGNORECASE)
_SLASH_VOICE = re.compile(r"^/voice(?:@\w+)?(?:\s+(on|off))?\s*$", re.IGNORECASE)
_SLASH_HELP = re.compile(r"^/help(?:@\w+)?\s*$", re.IGNORECASE)
_SLASH_START = re.compile(r"^/start(?:@\w+)?\s*$", re.IGNORECASE)

# Natural language — listen start
_LISTEN_START = re.compile(
    r"(?ix)^\s*"
    r"(?:"
    r"(?:please\s+)?(?:start|begin|open|enter|go\s+into|switch\s+to)\s+"
    r"(?:listening|listen\s+mode|recording|record\s+mode|pocket(?:\s+mode)?|capture\s+mode)"
    r"(?:\s+(?:for|on|to|about)?\s*(.+))?"
    r"|"
    r"(?:please\s+)?(?:listen|record|capture)\s+(?:this|the)\s+"
    r"(?:meeting|call|session|standup|sync|conversation|room)"
    r"(?:\s*[:\-]?\s*(.+))?"
    r"|"
    r"(?:please\s+)?record\s+(?:this|everything|the\s+meeting)"
    r"(?:\s*[:\-]?\s*(.+))?"
    r"|"
    r"listen(?:\s*:\s*|\s+)(.+)"
    r")\s*$"
)

# Natural language — stop listen
_LISTEN_STOP = re.compile(
    r"(?ix)^\s*"
    r"(?:"
    r"(?:please\s+)?(?:stop|end|quit|exit|leave|pause)\s+"
    r"(?:listening|listen\s+mode|recording|record\s+mode|pocket(?:\s+mode)?|capture)"
    r"|"
    r"(?:i(?:'m|\s+am)\s+)?done\s+listening"
    r"|"
    r"(?:that(?:'s|\s+is)\s+)?(?:enough|all)\s+(?:for\s+)?(?:now\s+)?(?:listening|recording)?"
    r"|"
    r"stop\s+recording"
    r")\s*[.!?]?\s*$"
)

# Close session / extract
_CLOSE = re.compile(
    r"(?ix)^\s*"
    r"(?:"
    r"(?:please\s+)?(?:close|finish|wrap\s*up|end)\s+"
    r"(?:the\s+)?(?:session|notes|meeting\s+notes|this\s+session)"
    r"(?:\s+(?:named|called|for)?\s*(.+))?"
    r"|"
    r"(?:please\s+)?(?:extract|pull\s+out)\s+(?:the\s+)?(?:promises|tasks|open\s+loops)"
    r"|"
    r"close\s+notes(?:\s*:\s*(.+))?"
    r")\s*[.!?]?\s*$"
)

# Brief
_BRIEF = re.compile(
    r"(?ix)^\s*"
    r"(?:"
    r"(?:please\s+)?(?:give\s+me\s+)?(?:a\s+)?(?:morning\s+|evening\s+|daily\s+)?brief(?:ing)?"
    r"|"
    r"what(?:'s|\s+is)\s+on\s+my\s+plate"
    r"|"
    r"catch\s+me\s+up"
    r"|"
    r"summary\s+of\s+(?:my\s+)?day"
    r")\s*[.!?]?\s*$"
)

# Quiet
_QUIET = re.compile(
    r"(?ix)^\s*"
    r"(?:"
    r"(?:please\s+)?(?:be\s+)?quiet(?:\s+mode)?"
    r"|"
    r"(?:please\s+)?(?:stop|don't|do\s+not)\s+(?:messaging|pinging|notifying|reminding)\s+me"
    r"|"
    r"(?:go\s+)?silent(?:\s+mode)?"
    r"|"
    r"no\s+more\s+(?:proactive\s+)?(?:messages|pings|reminders)"
    r")\s*[.!?]?\s*$"
)

# Un-quiet (resume proactive)
_UNQUIET = re.compile(
    r"(?ix)^\s*"
    r"(?:"
    r"(?:you\s+can\s+)?(?:message|ping|remind)\s+me\s+again"
    r"|"
    r"(?:end|leave|exit|turn\s+off)\s+quiet(?:\s+mode)?"
    r"|"
    r"(?:unmute|unquiet|resume\s+proactive)"
    r")\s*[.!?]?\s*$"
)

# Note this
_NOTE = re.compile(
    r"(?ix)^\s*(?:note\s+this|open\s+session|new\s+session)\s*[:\-]?\s*(.+)\s*$",
    re.DOTALL,
)

# Talking to Farzana while (or outside) listen — prefer discuss
_ADDRESS = re.compile(
    r"(?ix)^\s*(?:hey\s+|hi\s+|ok\s+)?farzana\b[,:]?\s*(.+)$",
    re.DOTALL,
)

# Question / request directed at the aide (not ambient meeting content)
_QUESTION = re.compile(
    r"(?ix)"
    r"(?:"
    r"\?"  # any question mark
    r"|"
    r"\b(?:will|can|could|would|should|do|did|are|is|have)\s+you\b"
    r"|"
    r"\b(?:remind|remember|tell|help|explain|summarize|summarise)\s+me\b"
    r"|"
    r"\b(?:what\s+do\s+you\s+think|what\s+should\s+i)\b"
    r"|"
    r"\bi\s+want\s+you\s+to\b"
    r")"
)


@dataclass
class Intent:
    kind: str
    """listen_start | listen_stop | close | quiet | unquiet | brief | note |
    voice_on | voice_off | help | start | discuss | capture"""

    title: str | None = None
    body: str | None = None
    source: str = "rules"
    also_capture: bool = False
    """If True while listen-active, still append transcript before acting."""


def _clean_title(raw: str | None) -> str | None:
    if not raw:
        return None
    t = raw.strip().strip("\"'").strip()
    t = re.sub(r"\s+", " ", t)
    if not t or t.lower() in {"this", "that", "please", "now", "mode"}:
        return None
    return t[:80]


def detect_intent(
    text: str,
    *,
    listen_active: bool = False,
    settings: Settings | None = None,
    use_llm_fallback: bool = True,
) -> Intent:
    raw = (text or "").strip()
    if not raw:
        return Intent(kind="discuss", body="")

    # --- Slash commands ---
    if _SLASH_START.match(raw):
        return Intent(kind="start", source="slash")
    if _SLASH_HELP.match(raw):
        return Intent(kind="help", source="slash")
    m = _SLASH_LISTEN.match(raw)
    if m:
        return Intent(kind="listen_start", title=_clean_title(m.group(1)) or "listen", source="slash")
    if _SLASH_STOP.match(raw):
        return Intent(kind="listen_stop", source="slash")
    m = _SLASH_CLOSE.match(raw)
    if m:
        return Intent(kind="close", title=_clean_title(m.group(1)), source="slash")
    if _SLASH_BRIEF.match(raw):
        return Intent(kind="brief", source="slash")
    if _SLASH_QUIET.match(raw):
        return Intent(kind="quiet", source="slash")
    m = _SLASH_VOICE.match(raw)
    if m:
        on = (m.group(1) or "on").lower() != "off"
        return Intent(kind="voice_on" if on else "voice_off", source="slash")
    m = _SLASH_NOTE.match(raw)
    if m:
        return Intent(kind="note", title=_clean_title(m.group(1)), body=m.group(1).strip(), source="slash")

    # --- Natural language commands ---
    m = _LISTEN_START.match(raw)
    if m:
        title = _clean_title(next((g for g in m.groups() if g), None)) or "listen"
        return Intent(kind="listen_start", title=title, source="rules")

    if _LISTEN_STOP.match(raw):
        return Intent(kind="listen_stop", source="rules")

    m = _CLOSE.match(raw)
    if m:
        title = _clean_title(next((g for g in m.groups() if g), None))
        return Intent(kind="close", title=title, source="rules")

    if _BRIEF.match(raw):
        return Intent(kind="brief", source="rules")

    if _QUIET.match(raw):
        return Intent(kind="quiet", source="rules")

    if _UNQUIET.match(raw):
        return Intent(kind="unquiet", source="rules")

    m = _NOTE.match(raw)
    if m:
        body = m.group(1).strip()
        title = body.split("\n", 1)[0].strip() if body else "note"
        return Intent(kind="note", title=_clean_title(title), body=body, source="rules")

    m = _ADDRESS.match(raw)
    if m:
        # "Farzana, stop listening" etc. — re-run on remainder once
        rest = m.group(1).strip()
        if rest and rest.lower() != raw.lower():
            inner = detect_intent(
                rest,
                listen_active=listen_active,
                settings=settings,
                use_llm_fallback=False,
            )
            if inner.kind not in {"discuss", "capture"}:
                inner.source = "address+" + inner.source
                return inner
        return Intent(kind="discuss", body=raw, source="address", also_capture=listen_active)

    # While listening: question → discuss (+ still capture); else pure capture
    if listen_active:
        if _QUESTION.search(raw) or len(raw) < 40 and raw.endswith("?"):
            return Intent(
                kind="discuss",
                body=raw,
                source="listen+question",
                also_capture=True,
            )
        # Short pure command leftovers
        low = raw.lower().strip("!. ")
        if low in {"stop", "enough", "done", "pause", "end"}:
            return Intent(kind="listen_stop", source="rules")
        if low in {"close", "wrap up", "wrapup", "finish"}:
            return Intent(kind="close", source="rules")

        # Ambiguous short phrase → optional LLM
        if use_llm_fallback and settings and settings.openai_api_key and len(raw) < 120:
            llm = _llm_intent(settings, raw, listen_active=True)
            if llm:
                return llm
        return Intent(kind="capture", body=raw, source="listen", also_capture=True)

    # Not listening: optional LLM if it looks like a mode command
    if (
        use_llm_fallback
        and settings
        and settings.openai_api_key
        and _looks_like_command(raw)
    ):
        llm = _llm_intent(settings, raw, listen_active=False)
        if llm and llm.kind != "discuss":
            return llm

    return Intent(kind="discuss", body=raw, source="rules")


def _looks_like_command(raw: str) -> bool:
    if len(raw) > 160:
        return False
    low = raw.lower()
    keys = (
        "listen",
        "record",
        "stop",
        "quiet",
        "brief",
        "close",
        "session",
        "remind",
        "mode",
        "capture",
        "pocket",
    )
    return any(k in low for k in keys) and len(raw.split()) <= 18


def _llm_intent(settings: Settings, text: str, *, listen_active: bool) -> Intent | None:
    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        system = (
            "Classify the user message for a personal memory aide bot. "
            "Return ONLY JSON: "
            '{"kind":"listen_start|listen_stop|close|quiet|unquiet|brief|note|discuss|capture",'
            '"title":null_or_string,"also_capture":bool}. '
            "listen_start = start long audio capture mode. "
            "listen_stop = stop capture mode without extracting. "
            "close = end session and extract promises. "
            "capture = ambient content while already listening (not a command). "
            "discuss = talking to the aide / asking a question. "
            f"listen_mode_currently_active={listen_active}. "
            "If ambiguous and listen is active, prefer capture for meeting content, "
            "discuss if they address the aide."
        )
        resp = client.chat.completions.create(
            model=settings.openai_chat_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": text[:500]},
            ],
            temperature=0,
            max_tokens=80,
        )
        raw = (resp.choices[0].message.content or "").strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        data = json.loads(raw)
        kind = str(data.get("kind") or "discuss").strip().lower()
        allowed = {
            "listen_start",
            "listen_stop",
            "close",
            "quiet",
            "unquiet",
            "brief",
            "note",
            "discuss",
            "capture",
        }
        if kind not in allowed:
            return None
        title = _clean_title(data.get("title"))
        also = bool(data.get("also_capture")) or (listen_active and kind in {"discuss", "capture"})
        if kind == "listen_start" and not title:
            title = "listen"
        return Intent(
            kind=kind,
            title=title,
            body=text,
            source="llm",
            also_capture=also if kind == "discuss" else (kind == "capture"),
        )
    except Exception:
        log.exception("intent LLM fallback failed")
        return None
