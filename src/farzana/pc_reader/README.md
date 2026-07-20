# PC essentials reader (read-only)

Give Farzana **eyes on the PC** for essentials **without hands**.

| Source | Read | Write |
|--------|------|-------|
| Calendar (`.ics` export) | yes | **no** |
| Email (`.eml` drop) | yes | **no send** |
| Notes / files (`.md` / `.txt`) | yes | **no delete** outside vault |

Output always lands as Markdown under `vault/pc/` so discuss / remind / adapt stay the same.

---

## Layout

```text
src/farzana/pc_reader/
  __main__.py      # CLI entry
  watch.py         # scan + poll folder
  calendar_ics.py  # ICS → vault/pc/calendar/
  mail_eml.py      # EML → vault/pc/mail/
  ingest.py        # vault write + fingerprint state
```

---

## How to use

1. Create a drop folder, e.g. `~/FarzanaInbox` (or `C:\Users\You\FarzanaInbox`).
2. Export calendar to ICS (Google/Outlook “export” or subscribe copy).
3. Save important mail as `.eml`, or drop notes as `.md`.
4. Run the reader on your PC (same vault, or Syncthing the vault with the server):

```bash
# One-shot
uv run farzana pc-reader --watch ~/FarzanaInbox --once

# Keep watching (poll every 15s)
uv run farzana pc-reader --watch ~/FarzanaInbox

# Explicit vault
uv run python -m farzana.pc_reader --watch C:\Users\You\FarzanaInbox --vault ./vault --once
```

5. Message Farzana on Telegram: `/brief` or “what’s on my calendar?” — context includes recent `vault/pc/` files.

---

## Rules

- **Read-only** only. Never send mail or create calendar events.  
- User opts in by placing exports (or later, read-only OAuth).  
- Re-import of the same file content is skipped (fingerprint).  
- Farzana still only **reminds, adapts, discusses gently** — she does not act.

## Status

Implemented: folder scan + poll watcher for ICS / EML / MD / TXT.  
Later: optional read-only OAuth calendar/mail.
