# AGENTS.md — guidance for coding agents & AI assistants

This file steers automated agents (and humans) working on Farzana.

## What Farzana is

**Single-user** read-only Markdown memory aide (Telegram).  
Listens carefully, stores transparent memory, discusses, resurfaces open loops, optional voice.  
**Not** multi-tenant. **Not** an action agent. **Not** a romantic companion bot.

**Name inspiration:** careful listening — Farzana from the **Inspector Jamshed** literary world (Ishtiaq Ahmed; Jamshed with Mehmood, Farooq, Farzana). She holds the thread; we do not ship franchise IP. See `docs/INSPIRATION.md` and `docs/STORY.md`.

Canonical product docs: `docs/STORY.md`, `docs/MOTIVATION.md`, `docs/RULES.md`, `docs/ARCHITECTURE.md`, `docs/STACK.md`.

## Hard constraints (do not violate)

1. **No external side-effect tools** — no email, calendar write, shell, browser automation, payments, social post.  
2. **Never commit secrets** — `.env`, `*.pem`, `server.env`, AWS keys, bot tokens, OpenAI keys.  
3. **Vault is source of truth** — one Markdown tree under `vault/` (single owner).  
4. **Public URL is config only** — `PUBLIC_BASE_URL`; app must not hardcode ngrok/Cloudflare.  
5. **Thin FastAPI routes** — business logic in `services/` and `workers/`.

## Preferred stack

- Python 3.11+, `uv`, FastAPI, Celery (eager OK for small deploys), OpenAI (chat/STT/TTS)  
- Telegram Bot API webhooks  
- Deploy: cheap EC2 + Caddy; infra via `deploy/terraform/`  

## When implementing features

| Area | Notes |
|------|--------|
| Capture | Text + voice → STT → vault |
| Dialogue | Jarvis-competent Farzana tone; max one clarify question |
| Proactive | Caps, quiet mode, log why in `proactive/` |
| Patterns | Log events; human-editable pattern files |
| Auth | Only `TELEGRAM_USER_ID` — never open multi-user |

## Security checklist before finishing a task

- [ ] No secrets in source or docs  
- [ ] `.gitignore` covers new secret paths  
- [ ] Webhook secret still required  
- [ ] Still single-user (`TELEGRAM_USER_ID`)  

## Out of scope unless issue explicitly asks

- WhatsApp (template/24h constraints)  
- Real phone calls  
- Hardware capture devices  
- Agent frameworks with tools  

## How to run locally (agents)

```bash
cp .env.example .env   # human fills secrets
uv sync
uv run farzana health
uv run farzana --no-webhook
```

Do not invent API keys. Do not print secrets in logs or PR bodies.
