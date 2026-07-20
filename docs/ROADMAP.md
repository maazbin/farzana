# Roadmap

Tracked in GitHub Issues. This file is a summary.

## Done (baseline)

- [x] Telegram webhook + FastAPI  
- [x] Markdown vault (per-user)  
- [x] Text dialogue (Farzana tone)  
- [x] Open multi-user mode  
- [x] Voice in (Whisper) + voice out (TTS)  
- [x] Session open/close + promise extract  
- [x] Proactive morning/evening + promise scan  
- [x] Pattern event logging  
- [x] EC2 deploy notes + Terraform module  

## Near term

- Timezone-aware briefs (not only UTC)  
- Better pattern “evolve” pass (summarize events → `patterns/*.md`)  
- Hybrid search (FTS + embeddings) over vault  
- Stronger quiet/proactivity levels UX  
- Grey-cloud / production domain webhook path  
- Tests (unit + webhook payload fixtures)  
- CI (lint + secret scan + tests)  

## Later

- Optional long-polling mode for local DX  
- WhatsApp adapter (template-aware)  
- Import from Pocket/Plaud exports  
- Optional Mermaid maps on session close  
- One-line installer (still no action tools)  
- Multi-instance / harder tenancy  

## Explicit non-goals (unless product decision flips)

- Autonomous external actions (email, browser, shell)  
- Romantic companion positioning  
- Always-on ambient hardware mic as core identity  
