# Farzana

**The aide who listens carefully.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Farzana is a **read-only Markdown memory aide** on Telegram.  
She captures what you say (text or voice), keeps it in **files you own**, discusses open loops, and can resurface them later — **without** sending email, browsing, or running agent tools on your behalf.

> Not an action agent (OpenClaw / Hermes).  
> Not a hardware stenographer (Pocket).  
> Not a romantic companion bot.

---

## Motivation (where this started)

I built Farzana because **I have ADHD** and I still have to lead, ship, and remember people.

The failure mode was simple and repeated:

- Someone tells me something important — I can’t always note it in the moment.  
- Even when I do note it, the note dies in a graveyard.  
- Task notifications are cold: easy to swipe, empty of context.  
- I wanted something that **cares enough to remind**, talks through the day and at day end, adapts to patterns — and **does not do the work for me**.

That founding pain shaped the product: capture has to be frictionless, memory has to be visible, resurfacing has to be human, and agents that “just act” are too dangerous when attention and impulse are uneven.

ADHD was the **motivation** and the **design stress-test** — not a medical claim, and not the only reason the tool should exist.

---

## Beyond that — who else this is for

The same gap shows up whenever life is **spoken and unfinished**:

- A promise in a call you couldn’t pause to type  
- Context that never made it into the task title  
- Notes scattered across apps you never reopen  
- Wanting a mirror of open loops without handing control to an agent  

Farzana is for **holding the thread** — capture in the moment (text or voice), store in Markdown you own, discuss and resurface later, stay **read-only**.

It sits beside whatever system you already use. It does not replace your calendar. It catches what the calendar never heard.

---

## Inspiration: Farzana of Inspector Jamshed (Ishtiaq Ahmed)

The name comes from **careful listening** in our storytelling culture: **Ishtiaq Ahmed’s Inspector Jamshed** novels, where Jamshed works with his children **Mehmood**, **Farooq**, and **Farzana**.

In that public memory, Farzana is not the loudest hero. She is present, sharp, and **listens carefully** — holding the thread of the case while others rush into noise.

```text
You are the inspector of your own day.
Farzana catches the thread.
You still decide. She never seizes the badge.
```

Independent open source — **not** affiliated with the franchise. Full write-up: [docs/INSPIRATION.md](docs/INSPIRATION.md).

---

## What she does

| Does | Refuses |
|------|---------|
| Listen (text + voice) | Email, calendar write, browse, shell |
| Store in Markdown you own | Opaque “AI memory” only |
| Discuss & resurface open loops | Romance / therapist cosplay |
| Optional proactive briefs | Unlimited nagging (`/quiet`, daily caps) |

| Feature | Status |
|---------|--------|
| Telegram text / voice in / TTS out | Yes |
| Per-user vault, sessions, `/close` extract | Yes |
| Proactive briefs / promise scan | Yes (UTC; timezones on roadmap) |
| Single-user only (`TELEGRAM_USER_ID`) | Yes |
| External actions | **Never** |

**Memory model:** files are truth; the model only gets a temporary view. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## Quick start

```bash
git clone https://github.com/maazbin/farzana.git
cd farzana
cp .env.example .env
# TELEGRAM_* + OPENAI_API_KEY — never commit .env

uv sync
uv run farzana health
uv run farzana --no-webhook   # http://127.0.0.1:8000
```

**Telegram single-user + optional ngrok:** [docs/SETUP.md](docs/SETUP.md)  
Optional VPS/Terraform (placeholders only): [deploy/README.md](deploy/README.md)

### Secrets

Never commit `.env`, `*.pem`, or API tokens. Rotate anything that leaked.

---

## Using the bot

1. Public `PUBLIC_BASE_URL` + `uv run farzana` (or webhook after tunnel).  
2. `/start` from the Telegram account in `TELEGRAM_USER_ID`.  
3. Text or voice note.  
4. `Note this: …` → `/close`.  
5. `/brief` · `/quiet` · `/voice on|off`.

---

## Docs

| Doc | Content |
|-----|---------|
| [STORY.md](docs/STORY.md) | Full product + founder origin |
| [INSPIRATION.md](docs/INSPIRATION.md) | Jamshed / Farzana myth |
| [MOTIVATION.md](docs/MOTIVATION.md) | Why / when / when not |
| [RULES.md](docs/RULES.md) · [SECURITY.md](SECURITY.md) | Hard rules |
| [ROADMAP.md](docs/ROADMAP.md) | Future |

---

## Contributing

[CONTRIBUTING.md](CONTRIBUTING.md) · [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) · [AGENTS.md](AGENTS.md)

## License

[MIT](LICENSE)

---

*Started for a mind that drops threads under load.*  
*Useful whenever life is spoken faster than it gets written down.*
