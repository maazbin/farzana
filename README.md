# Farzana

**The aide who listens carefully.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> *Someone told you something important.*  
> *You nodded. You meant to write it down.*  
> *By night, the words were gone — and the cold notification on your phone could not care less.*

**Farzana** is a **read-only Markdown memory aide** on Telegram: she captures what you say (text or voice), keeps it in **files you own**, discusses your open loops, and can come back when follow-through matters — **without** sending email, browsing, or running agent tools on your behalf.

> Not OpenClaw / Hermes (action agents).  
> Not Pocket (hardware stenographer).  
> Not a romantic companion bot.

---

## Why I started this (ADHD, leadership, and a leaky mind)

I did not start Farzana as a startup pitch.

I started it because **I live with ADHD** — and I also live as someone who has to **lead**, ship, remember people, and hold too many threads at once.

The pain was specific, and it was daily:

- Someone tells me something important — **I cannot note it in the moment**.  
- Even when I *do* note it, **I still forget**.  
- Task apps ping me like alarms: cold, flat, easy to swipe away.  
- I wanted something that **cares enough to remind me**, that **talks at the end of the day**, that **discusses my schedule**, that tries to **adapt to my patterns** — not another dashboard I would abandon.  
- First home had to be **mobile** (messaging I already live in), then the same memory on **PC**.  
- And the hard line: **it must not do the work for me.** No OpenClaw. No Hermes. No “I’ll just email them.”  
  Its sole purpose: **read, remember, remind, encourage, discuss** — with emotional intelligence, without emotional dependency.

ADHD did not make me “want a toy.”  
It made the **hardest user** of memory products: interest-based attention, time blindness, notification blindness, shame after forgetting, impulsivity that makes *agent* tools dangerous.

So I designed for that hard case.

If Farzana works when your working memory drops mid-conversation, it works for a lot of other people too.

---

## How that helps people who are *not* “just ADHD”

ADHD was the **stress test**, not the only audience.

The same failure mode shows up whenever life has **too many open loops** and **no one holding the thread**:

| Who | What breaks | What Farzana offers |
|-----|-------------|---------------------|
| **ADHD brains** | Working memory, cold pings, shame | External memory, voice, resurfacing, quiet mode |
| **Lone people** | No partner to “remember for me” | Accountability without social debt |
| **Lone leaders / founders** | Too many promises, no EA | Chief of staff for *memory*, not for execution |
| **Overloaded employees** | Dropped follow-ups look like character | Close loops before they become performance pain |
| **Anyone drowning in tools** | Notes + todos + agents, none that *talk back* | One aide over one vault you own |

**Same product, different stories.**  
We do not claim to diagnose or treat ADHD. We claim a design truth:

> Build for the brain that forgets under load — and you build something kinder for everyone who carries too much alone.

---

## The myth: Farzana of Inspector Jamshed (Ishtiaq Ahmed)

Long before productivity apps, many of us grew up with **Inspector Jamshed** — the detective/espionage world of **Ishtiaq Ahmed’s** Urdu novels: local, moral, endless cases, a household name across bookstalls and childhoods.

Jamshed did not win alone. Beside him stood his children:

| Name | In the public memory of the myth |
|------|-----------------------------------|
| **Mehmood** | Clever, sharp — the quick mind |
| **Farooq** | Drive, field energy — the push into action |
| **Farzana** | Present, intelligent — the one who **listens carefully** |

Around them: strategists, scientists, field officers — a **team of different strengths**. Cases mixed crime, conspiracy, and stakes larger than one ego.

In that shared cultural memory, **Farzana** is not cast as the loudest hero.  
She is the one who **hears** what was said, **holds the thread**, and helps the mission when others rush into noise and spectacle.

That is the spirit this project takes — not plots, not licensed characters, not an official franchise product.

**Independent open source.** Inspired by a *quality of attention* our stories already taught us.

The name **Farzana** also carries shades of **wisdom / intelligence** in Persian and Urdu — a second layer under the character memory.

### The parable we built the software on

```text
You are the inspector of your own day.
Too many conversations. Half-promises. Ideas that vanish by night.

Farzana does not seize your badge.
She catches the thread.
She files it where you can see it.
She brings open loops back — in text or voice — when follow-through matters.

You still decide.
She never acts on the outside world.
```

Deep dive: **[docs/INSPIRATION.md](docs/INSPIRATION.md)** · **[docs/STORY.md](docs/STORY.md)**

---

## What Farzana *is* (product)

**External working memory** you talk to on Telegram:

| She does | She refuses |
|----------|-------------|
| Listen (text + voice) | Email, calendar write, browse, shell |
| Store in **Markdown you own** | Black-box “AI remembered something” only |
| Discuss & encourage from history | Romance / therapist cosplay |
| Resurface open loops (proactive + `/brief`) | “I’ll just handle it” agent behavior |
| Adapt via patterns (logged; evolving) | Silent nag without controls (`/quiet`) |

**Docs:** [MOTIVATION](docs/MOTIVATION.md) · [RULES](docs/RULES.md) · [ARCHITECTURE](docs/ARCHITECTURE.md) · [STACK](docs/STACK.md) · [ROADMAP](docs/ROADMAP.md) · [SECURITY](SECURITY.md)

---

## Features (current)

| Area | Support |
|------|---------|
| Telegram text | Yes |
| Voice notes → Whisper | Yes |
| Voice replies (TTS) | Yes |
| Per-user Markdown vault | Yes |
| Named sessions + `/close` extract | Yes |
| Proactive briefs / promise scan | Yes (UTC; timezone UX on roadmap) |
| Single-user allowlist **or** open mode | Yes |
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

Webhook + public URL: **[docs/SETUP.md](docs/SETUP.md)**  
AWS / Terraform: **[deploy/README.md](deploy/README.md)** · **[deploy/terraform/README.md](deploy/terraform/README.md)**

### Secrets

Never commit `.env`, `*.pem`, `server.env`, or API tokens.  
If a key leaked in chat or logs — **rotate it**.

---

## Using the bot

1. Run with a public `PUBLIC_BASE_URL` and register webhook.  
2. Telegram → your bot → `/start` (from your allowlisted account if single-user).  
3. Send **text** or a **voice note**.  
4. `Note this: meeting` → dump → `/close` to extract promises.  
5. `/brief` to discuss open loops; proactive jobs may message later.  
6. `/quiet` pauses outreach.

---

## Project layout

```text
src/farzana/     # FastAPI app, services, workers
docs/            # story, inspiration, architecture
deploy/          # EC2 + Terraform (no secrets in git)
AGENTS.md        # guidance for coding agents
```

---

## Contributing

[CONTRIBUTING.md](CONTRIBUTING.md) · [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) · [AGENTS.md](AGENTS.md)

---

## License

[MIT](LICENSE)

---

*For everyone who was told to “just write it down” — and still lost the day.*
