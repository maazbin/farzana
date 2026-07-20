"""Capture engine — single-user vault."""

from __future__ import annotations

from pathlib import Path

from farzana.services import vault as vault_io


def capture_text(
    vault_root: Path,
    text: str,
    session_name: str | None = None,
) -> str:
    if session_name:
        path = vault_io.append_session(vault_root, session_name, text)
        return f"session:{path.name}"
    path = vault_io.append_inbox(vault_root, text)
    return f"inbox:{path.name}"
