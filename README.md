# Farzana

**The aide who listens carefully.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Farzana is a **read-only Markdown memory aide** you talk to on Telegram.

She captures text and voice, stores **transparent memory you own**, discusses open loops, and can resurface reminders (including voice) — **without** sending email, browsing, or running agent tools on your behalf.

> Not OpenClaw/Hermes (action agents). Not Pocket (hardware stenographer). Not a romantic companion bot.

---

## Inspiration

The name **Farzana** is inspired by careful listening — including **Farzana** from the **Inspector Jamshed** world of Urdu detective fiction: present, sharp, and remembered for *hearing* what matters, not for spectacle.

This project is an **independent open-source product**. It is **not** affiliated with or endorsed by the Inspector Jamshed franchise or its rights holders. We borrow a *quality of attention*, not characters, plots, or official branding.

Tone also draws on a **Jarvis-like aide** (competence and discretion) and **ADHD-hard** design (external memory, resurfacing, anti-nag controls).

**Full story:** [docs/STORY.md](docs/STORY.md#inspiration-why-farzana) · [docs/MOTIVATION.md](docs/MOTIVATION.md)

---

## Why

People forget what was said. Notifications are cold. Agent tools are powerful and risky.

Farzana is **external working memory**: listen → store → discuss → resurface.  
Designed under ADHD-hard constraints; useful for anyone alone with too many open loops.

**Story & motivation:** [docs/STORY.md](docs/STORY.md) · [docs/MOTIVATION.md](docs/MOTIVATION.md)  
**Rules:** [docs/RULES.md](docs/RULES.md) · [SECURITY.md](SECURITY.md)  
**Architecture / stack:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) · [docs/STACK.md](docs/STACK.md)  
**Roadmap:** [docs/ROADMAP.md](docs/ROADMAP.md)

---

## Features (current)

| Area | Support |
|------|---------|
| Telegram text | Yes |
| Voice notes → Whisper | Yes |
| Voice replies (TTS) | Yes |
| Per-user Markdown vault | Yes |
| Named sessions + `/close` extract | Yes |
| Proactive briefs / promise scan | Yes (UTC schedules) |
| Multi-user open mode | Yes (`TELEGRAM_ALLOW_ALL_USERS`) |
| External actions | **Never** (by design) |

---

## Quick start

```bash
git clone https://github.com/maazbin/farzana.git
cd farzana
cp .env.example .env
# Edit .env — tokens stay local (never commit)

uv sync
uv run farzana health
uv run farzana --no-webhook   # http://127.0.0.1:8000
```

Webhook + public URL: see **[docs/SETUP.md](docs/SETUP.md)**.  
AWS/Terraform: **[deploy/README.md](deploy/README.md)** · **[deploy/terraform/README.md](deploy/terraform/README.md)**.

### Critical: secrets

| Never commit | Use instead |
|--------------|-------------|
| `.env`, `deploy/server.env` | `.env.example` |
| `*.pem`, `deploy/keys/` | generate locally / Terraform |
| API tokens in docs or issues | redacted logs |

If a key leaked in chat/logs, **rotate it** (BotFather + OpenAI dashboard).

---

## Using the bot

1. Start the server with a public `PUBLIC_BASE_URL` and register webhook (`uv run farzana` or deploy).  
2. Open your bot on Telegram → `/start`.  
3. Send text or a **voice note**.  
4. `Note this: meeting` → dump notes → `/close` to extract promises.  
5. `/brief` for an on-demand discussion; proactive jobs may message later.  
6. `/quiet` pauses proactive outreach.

---

## Project layout

```text
src/farzana/     # FastAPI app, services, workers
docs/            # product + engineering docs
deploy/          # EC2 scripts + Terraform (no secrets)
.github/         # PR/issue templates, CODEOWNERS
AGENTS.md        # guidance for coding agents
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).  
AI/agent contributors: follow [AGENTS.md](AGENTS.md).

---

## License

[MIT](LICENSE)
