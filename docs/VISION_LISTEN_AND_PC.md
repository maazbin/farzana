# Vision: Telegram as Pocket + PC essentials (read-only)

## Product truth (updated)

You should **not** have to re-tell your life to Farzana.

| Layer | Job | Still true |
|-------|-----|------------|
| **Listen** | Capture long audio (meeting/call/room) via Telegram | You start/stop a listen session |
| **PC essentials** | **Read** calendar, mail, key files into the vault | **No send, no book, no delete** |
| **Aide** | Remind, adapt, gentle discuss | Same Farzana tone |

```text
LISTEN (long Telegram audio / PC read) → VAULT → DISCUSS / REMIND / ADAPT
         never write email/calendar/act
```

---

## Telegram as Pocket (realistic)

Telegram bots **cannot** keep an always-open mic stream like a hardware device.

What we **can** do (Pocket-like in practice):

1. **`/listen Meeting name`** — enter listen mode.  
2. Hold Telegram record for a **long voice note** (or send a long **audio file**).  
3. Farzana **transcribes and appends** to that session (quiet ack, not a lecture).  
4. Send more voice chunks while still listening (long meeting = several clips).  
5. **`/stop`** or **`/close`** — stop listen, extract promises, discuss.

That is “open audio for a long time” **as Telegram allows**: long recordings + continuous session, not true always-on ambient hardware.

**Consent / legality:** recording others may require consent in your jurisdiction. You own that choice.

---

## PC essentials (read-only)

A small **local companion** on your PC (same vault or sync folder):

| Essential | Read | Write / act |
|-----------|------|-------------|
| Calendar | Yes (ICS / Graph / Google read scope) | **No** |
| Email | Yes (headers/snippets or labels you choose) | **No send** |
| Files / notes | Watch folders you allow | **No delete** outside vault |

Output: Markdown into `vault/inbox/` or `vault/pc/` so Farzana’s discuss/remind path stays the same.

OpenClaw/Hermes attach **tools that act**. We attach **readers that only fill memory**.

---

## Phases

| Phase | Deliverable |
|-------|-------------|
| **Done** | `/listen` + long voice/audio append + quiet ack + `/stop`/`/close` |
| **Done** | PC folder watcher: ICS / EML / MD / TXT → `vault/pc/` (`uv run farzana pc-reader`) |
| **Later** | Optional read-only OAuth calendar/mail → vault |

### PC reader quick start

```bash
# On your PC — drop exports into a folder, then:
uv run farzana pc-reader --watch ~/FarzanaInbox --once
# or keep watching:
uv run farzana pc-reader --watch ~/FarzanaInbox
```

Farzana still only **reads → vault → reminds / adapts / discusses**. No send, no book.

---

## Non-goals (still)

- Sending email, booking meetings, browsing as an agent  
- Unofficial WhatsApp reverse engineering  
- Claiming always-on secret mic without user start
