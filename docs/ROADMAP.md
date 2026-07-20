# Roadmap

Tracked in **GitHub Issues**. Living board: **[#13 Status · done vs expected](https://github.com/maazbin/farzana/issues/13)**  
Also summarized in the root [README · Status](../README.md#-status--done-vs-expected).

## Done (baseline)

- [x] Telegram webhook + FastAPI  
- [x] Markdown vault (single-user)  
- [x] Text dialogue (Farzana tone)  
- [x] Single-user auth (`TELEGRAM_USER_ID`)  
- [x] Voice in (Whisper) + voice out (TTS)  
- [x] Semantic mode switching (natural language + slash)  
- [x] Session open/close + promise extract  
- [x] Proactive morning/evening + promise scan  
- [x] Pattern event logging  
- [x] **/listen** Pocket-style long audio sessions on Telegram  
- [x] PC read-only folder watcher (ICS / EML / MD → `vault/pc/`)  
- [x] Deploy notes + Terraform module  

## Near term

| Item | Issue |
|------|-------|
| Timezone-aware briefs | [#1](https://github.com/maazbin/farzana/issues/1) |
| Pattern evolve pass | [#2](https://github.com/maazbin/farzana/issues/2) |
| Hybrid vault search | [#3](https://github.com/maazbin/farzana/issues/3) |
| CI + secret scan | [#4](https://github.com/maazbin/farzana/issues/4) |
| Unit + webhook tests | [#6](https://github.com/maazbin/farzana/issues/6) |
| Proactivity UX polish | [#12](https://github.com/maazbin/farzana/issues/12) |
| PC reader: recursive / PDF / Syncthing | [#15](https://github.com/maazbin/farzana/issues/15) |
| Gentle open-loop accountability | [#16](https://github.com/maazbin/farzana/issues/16) |
| Timed soft reminders | [#17](https://github.com/maazbin/farzana/issues/17) |
| Scrub tokens from logs | [#18](https://github.com/maazbin/farzana/issues/18) |

## Later

| Item | Issue |
|------|-------|
| Optional long-polling local DX | [#7](https://github.com/maazbin/farzana/issues/7) |
| WhatsApp adapter | [#8](https://github.com/maazbin/farzana/issues/8) |
| Pocket/export import | [#9](https://github.com/maazbin/farzana/issues/9) |
| Mermaid maps on `/close` | [#10](https://github.com/maazbin/farzana/issues/10) |
| One-line installer | [#11](https://github.com/maazbin/farzana/issues/11) |
| Read-only OAuth calendar/mail | [#14](https://github.com/maazbin/farzana/issues/14) |

## Explicit non-goals (unless product decision flips)

- Autonomous external actions (email, browser, shell)  
- Romantic companion positioning  
- Always-on ambient hardware mic as core identity  
