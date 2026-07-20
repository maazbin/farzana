# Roadmap

Tracked in GitHub Issues. This file is a summary.

## Done (baseline)

- [x] Telegram webhook + FastAPI  
- [x] Markdown vault (single-user)  
- [x] Text dialogue (Farzana tone)  
- [x] Single-user auth (`TELEGRAM_USER_ID`)  
- [x] Voice in (Whisper) + voice out (TTS)  
- [x] Session open/close + promise extract  
- [x] Proactive morning/evening + promise scan  
- [x] Pattern event logging  
- [x] **/listen** Pocket-style long audio sessions on Telegram  
- [x] PC read-only folder watcher (ICS / EML / MD → `vault/pc/`)  
- [x] Deploy notes + Terraform module  

## Near term

- Improve long-audio (chunk merge, duration limits, better acks)  
- PC reader: recursive watch, PDF text, optional Syncthing recipes  
  
- Timezone-aware briefs  
- Pattern evolve pass  
- Hybrid search over vault  
- Tests + CI + secret scan  

## Later

- Read-only OAuth calendar/mail (still no send/book)  
- Optional long-polling for local DX  
- WhatsApp adapter  
- Hardware/Pocket export import  
- Mermaid maps on `/close`

## Explicit non-goals (unless product decision flips)

- Autonomous external actions (email, browser, shell)  
- Romantic companion positioning  
- Always-on ambient hardware mic as core identity  
