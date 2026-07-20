# Stack (locked for v1 direction)

> Operational source of truth for technology choices.  
> Narrative product constraints: [STORY.md](./STORY.md) · [RULES.md](./RULES.md)

---

## One-liner

**FastAPI + Celery/Redis + Markdown vault + OpenAI (chat/STT/TTS) + Telegram**, process-managed by **PM2** on a **cheap AWS EC2** later; **local + ngrok** now.

---

## Components

| Layer | Choice | Why |
|-------|--------|-----|
| Language | Python 3.12+ | Ecosystem for bots/LLM |
| HTTP | FastAPI + uvicorn | Webhooks, clear structure |
| Jobs | Celery + Redis | Proactive/TTS off request path |
| Process mgr | PM2 | Easy restart/logs; no Docker required v1 |
| Channel | Telegram Bot API | Free-form proactive; simple bots |
| LLM/STT/TTS | OpenAI | One vendor; `gpt-4o-mini-tts` emotions |
| Memory | Markdown + (later) SQLite hybrid index | Transparent, editable |
| Local tunnel | ngrok | Webhook testing |
| Cloud later | Cheap EC2 (micro/small class) | Low cost personal host |

---

## Explicitly out of v1

Docker-first, ECS/EFS/ElastiCache, ElevenLabs, WhatsApp, diarization, LangChain agents, external action tools, unofficial WA.

---

## Why not WhatsApp (summary)

Outside the ~24h user-initiated window, WhatsApp only allows **template** business-initiated messages. Option C proactive dialogue is first-class on Telegram and hostile on WhatsApp. Full write-up lives in historical `FINAL_STACK.md` / design sessions.

---

## Why OpenAI TTS not ElevenLabs

Steerable instructions, one API key with Whisper/chat, enough emotion for Jarvis briefs. Revisit only if voice quality fails.

---

## Why Celery not only APScheduler

With FastAPI webhooks, STT/TTS/extract/proactive are **jobs**. Celery + Redis (+ beat later) isolates failures and retries. Local: `CELERY_TASK_ALWAYS_EAGER=true`.

---

## Why PM2

Personal deploy: `pm2 start ecosystem.config.cjs`, `pm2 logs`, `pm2 restart all`. Python venv on box; Redis via apt/Docker/Memurai.

---

## Env keys (where from)

| Key | Source |
|-----|--------|
| `TELEGRAM_BOT_TOKEN` | @BotFather |
| `TELEGRAM_USER_ID` | @userinfobot (owner only) |
| `TELEGRAM_WEBHOOK_SECRET` | you generate |
| `OPENAI_API_KEY` | platform.openai.com/api-keys |
| `PUBLIC_BASE_URL` | ngrok https URL |
| `REDIS_URL` | local Redis |
| `CELERY_TASK_ALWAYS_EAGER` | `true` for simplest local |

Details: root [README.md](../README.md) and [.env.example](../.env.example).
