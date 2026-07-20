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

ADHD was the **motivation** — why I started. It is not a diagnosis product, and you do not need ADHD to benefit.

---

## Most assistants assume you’re already organized

Look at the landscape: calendars, todo suites, “second brains,” and agent tools usually work best when you already:

- open the app on purpose  
- maintain the system  
- trust yourself to follow through  
- can ignore noise and still find the signal  

They reward people who are **already up**. If you’re there, many tools are fine.

**Farzana was built from the opposite direction.**

ADHD forced a different pattern: capture must work when you *can’t* pause, memory must be visible when you don’t trust your head, reminders must *care* (context + discussion, not only badges), and the system must not take dangerous actions when impulse is high.

That pattern does not only serve ADHD. It can help a **low-capacity day** become a higher-capacity life — for anyone who:

- loses spoken promises  
- abandons note apps after a week  
- feels behind, not “optimized”  
- wants support without an agent that acts for them  

You don’t need ADHD for that. ADHD was just the **reason the bar was set high**.  
Pass a hard bar, and people starting lower get a ladder — not another tool that assumes they already climbed.

```text
Most tools:  built for people who already run a system
Farzana:     built so you can hold a thread even when the system fails
Motivation:  ADHD under load
Audience:    anyone who needs the thread held
```

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
| Listen (text + long voice = Pocket-style) | Always-on secret mic; acting for you |
| **Read** PC essentials (calendar/mail/files → vault) | Email **send**, calendar **write**, browse, shell |
| Store in Markdown you own | Opaque “AI memory” only |
| Remind, adapt, gentle discuss | Romance / therapist cosplay |
| Optional proactive briefs | Unlimited nagging (`/quiet`, daily caps) |

| Feature | Status |
|---------|--------|
| Telegram text / voice in / TTS out | Yes |
| `/listen` long audio sessions (Telegram as Pocket) | Yes |
| PC read-only essentials (`farzana pc-reader`) | Yes (ICS / EML / MD drops) |
| Vault sessions, `/close` extract | Yes |
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
**Telegram as Pocket + PC eyes:** [docs/VISION_LISTEN_AND_PC.md](docs/VISION_LISTEN_AND_PC.md)  
Optional VPS/Terraform (placeholders only): [deploy/README.md](deploy/README.md)

```bash
# Long listen on Telegram: /listen Meeting name → long voice clips → /stop or /close

# On your PC — drop calendar/mail exports, read-only into vault:
mkdir FarzanaInbox
uv run farzana pc-reader --watch ./FarzanaInbox --once
```

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

*Started from ADHD under load — that was the motivation.*  
*Built so anyone who needs a thread held can climb, even without ADHD.*
