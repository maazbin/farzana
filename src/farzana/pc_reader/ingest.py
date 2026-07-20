"""Write PC essentials into vault/pc/ — never touch external systems for write."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from farzana.services import vault as vault_io


def ensure_pc_dirs(root: Path) -> None:
    vault_io.ensure_vault(root)
    for rel in (
        "pc",
        "pc/calendar",
        "pc/mail",
        "pc/files",
        "pc/inbox",
        "config",
    ):
        (root / rel).mkdir(parents=True, exist_ok=True)


def _state_path(root: Path) -> Path:
    ensure_pc_dirs(root)
    return root / "config" / "pc_reader_state.json"


def load_state(root: Path) -> dict:
    path = _state_path(root)
    if not path.exists():
        return {"seen": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"seen": {}}
    if "seen" not in data:
        data["seen"] = {}
    return data


def save_state(root: Path, state: dict) -> None:
    path = _state_path(root)
    state["updated"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def file_fingerprint(path: Path) -> str:
    """Stable fingerprint so re-exports with same content are skipped."""
    st = path.stat()
    h = hashlib.sha256()
    h.update(path.name.encode("utf-8", errors="ignore"))
    h.update(str(st.st_size).encode())
    # hash first + last 64k for large files without full read cost on huge dumps
    with path.open("rb") as f:
        head = f.read(65536)
        h.update(head)
        if st.st_size > 131072:
            f.seek(max(0, st.st_size - 65536))
            h.update(f.read(65536))
        elif st.st_size > 65536:
            h.update(f.read())
    return h.hexdigest()[:32]


def already_ingested(root: Path, path: Path) -> bool:
    state = load_state(root)
    key = str(path.resolve())
    fp = file_fingerprint(path)
    return state.get("seen", {}).get(key) == fp


def mark_ingested(root: Path, path: Path, out_path: Path) -> None:
    state = load_state(root)
    key = str(path.resolve())
    state.setdefault("seen", {})[key] = file_fingerprint(path)
    state.setdefault("outputs", {})[key] = str(out_path)
    save_state(root, state)


def safe_slug(name: str, max_len: int = 60) -> str:
    safe = "".join(c if c.isalnum() or c in "-_." else "-" for c in name.lower()).strip("-.")
    return (safe or "item")[:max_len]


def write_pc_markdown(
    root: Path,
    category: str,
    title: str,
    body: str,
    *,
    source_file: str = "",
    extra_front: dict | None = None,
) -> Path:
    """
    Write Markdown under vault/pc/{category}/.
    category: calendar | mail | files | inbox
    """
    ensure_pc_dirs(root)
    allowed = {"calendar", "mail", "files", "inbox"}
    if category not in allowed:
        category = "inbox"

    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    ts = datetime.now(timezone.utc).strftime("%H%M%S")
    slug = safe_slug(title)
    fname = f"{day}-{ts}-{slug}.md"
    out = root / "pc" / category / fname

    front = {
        "title": title,
        "source": "pc_reader",
        "category": category,
        "ingested": datetime.now(timezone.utc).isoformat(),
        "source_file": source_file,
    }
    if extra_front:
        front.update(extra_front)

    lines = ["---"]
    for k, v in front.items():
        if v is None or v == "":
            continue
        # one-line YAML-ish
        val = str(v).replace("\n", " ").strip()
        lines.append(f"{k}: {val}")
    lines.append("---")
    lines.append("")
    lines.append(f"# {title}")
    lines.append("")
    lines.append(body.strip())
    lines.append("")

    out.write_text("\n".join(lines), encoding="utf-8")

    # also a short pointer in daily inbox so briefs notice it
    vault_io.append_inbox(
        root,
        f"PC {category}: **{title}** → `{out.relative_to(root)}`",
        source="pc_reader",
    )
    vault_io.log_pattern_event(root, f"pc_ingest:{category}:{slug}")
    return out
