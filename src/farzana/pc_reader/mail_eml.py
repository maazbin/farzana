"""Parse .eml drops → Markdown (read-only). Never send mail."""

from __future__ import annotations

import email
from email import policy
from email.message import Message
from pathlib import Path


def _get_body(msg: Message) -> str:
    if msg.is_multipart():
        plain_parts: list[str] = []
        html_parts: list[str] = []
        for part in msg.walk():
            ctype = part.get_content_type()
            disp = str(part.get("Content-Disposition") or "")
            if "attachment" in disp.lower():
                continue
            try:
                payload = part.get_content()
            except Exception:
                raw = part.get_payload(decode=True)
                if isinstance(raw, bytes):
                    payload = raw.decode(part.get_content_charset() or "utf-8", errors="replace")
                else:
                    payload = str(raw or "")
            if not isinstance(payload, str):
                continue
            if ctype == "text/plain":
                plain_parts.append(payload)
            elif ctype == "text/html":
                html_parts.append(payload)
        if plain_parts:
            return "\n\n".join(plain_parts).strip()
        if html_parts:
            # crude strip tags — enough for memory context
            import re

            text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", html_parts[0])
            text = re.sub(r"(?s)<[^>]+>", " ", text)
            text = re.sub(r"\s+", " ", text).strip()
            return text[:8000]
        return ""
    try:
        content = msg.get_content()
        return content.strip() if isinstance(content, str) else str(content)[:8000]
    except Exception:
        raw = msg.get_payload(decode=True)
        if isinstance(raw, bytes):
            return raw.decode(msg.get_content_charset() or "utf-8", errors="replace")[:8000]
        return str(msg.get_payload() or "")[:8000]


def parse_eml(path: Path) -> dict:
    raw = path.read_bytes()
    msg = email.message_from_bytes(raw, policy=policy.default)
    subject = str(msg.get("Subject") or "(no subject)")
    return {
        "subject": subject,
        "from": str(msg.get("From") or ""),
        "to": str(msg.get("To") or ""),
        "cc": str(msg.get("Cc") or ""),
        "date": str(msg.get("Date") or ""),
        "message_id": str(msg.get("Message-ID") or ""),
        "body": _get_body(msg),
    }


def eml_to_markdown(path: Path) -> tuple[str, str]:
    data = parse_eml(path)
    title = f"Mail - {data['subject']}"
    lines = [
        "_Read-only import — Farzana never sends email._",
        "",
        f"- **From:** {data['from']}",
        f"- **To:** {data['to']}",
    ]
    if data.get("cc"):
        lines.append(f"- **Cc:** {data['cc']}")
    if data.get("date"):
        lines.append(f"- **Date:** {data['date']}")
    if data.get("message_id"):
        lines.append(f"- **Message-ID:** `{data['message_id']}`")
    lines.append("")
    lines.append("## Body")
    lines.append("")
    body = (data.get("body") or "").strip() or "_(empty or unreadable body)_"
    # cap huge mail dumps
    if len(body) > 12000:
        body = body[:12000] + "\n\n… _(truncated for vault)_"
    lines.append(body)
    return title, "\n".join(lines)
