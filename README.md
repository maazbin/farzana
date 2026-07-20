# Farzana

**The aide who listens carefully.**  
**Built by someone with ADHD — for minds that drop the thread.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## My story — from the start

I have **ADHD**.

I also have to **lead**, build, remember people, and carry more open loops than a notes app was ever designed for.

This project did not begin with a market map. It began with a pattern I could not escape:

> Someone tells me something important.  
> I mean to write it down.  
> I can’t — not in that second, not with that app, not while life is still talking.  
> Sometimes I *do* write it down.  
> **I still forget.**

I already had task apps. I already had notifications. They did not fail because I was lazy. They failed because they were **cold**.

A red badge does not care that I was in a meeting.  
A reminder does not know what *Sarah actually said*.  
A todo list does not talk to me at the end of the day and ask what still hurts.

So I wrote down what I actually wanted — almost exactly like this:

- A **lite personal aide**, not a task robot.  
- When I have an idea, or work, or **someone tells me something** — capture it.  
- If I forget to give instructions, **ask me one clear question**.  
- **Care** enough to remind me — not scream at me.  
- Talk **during the day** and at **day end**. Discuss my schedule.  
- Try to **adapt to my pattern of life**.  
- Live first where I already live: **mobile messaging** — then the same memory on **PC**.  
- And the line I would not cross:

> **It does not do the work.**  
> No OpenClaw. No Hermes. No “I’ll just email them for you.”  
> Sole purpose: **read, remember, remind, encourage, discuss.**

That is the birth certificate of **Farzana**.

ADHD was not a buzzword I bolted on later.  
**ADHD was the reason the product exists.**

---

## Why ADHD is the product (we sell the hard case)

Most “productivity AI” is designed for a fantasy user: always organized, always opens the app, always trusts the agent.

ADHD under load is the opposite fantasy:

| What ADHD (and high load) actually does | What most tools assume |
|----------------------------------------|-------------------------|
| Working memory drops mid-sentence | “You’ll type it into the form” |
| Interest ≠ importance | “You’ll open the dashboard because it matters” |
| Notifications train **ignore** | “One more ping will fix it” |
| Shame after forgetting | “Streaks and guilt will motivate you” |
| Impulsivity + powerful agents | “Let the agent act for you” |

Farzana is designed **against** those assumptions.

### What “ADHD-hard” means in the product

| Reality | Farzana’s answer |
|---------|------------------|
| I can’t note in the moment | **Telegram** — text or **voice note**, no new app ritual |
| Notes die in graveyards | Memory is **Markdown files I can see and edit** |
| Cold pings fail | **Discussion**, not only alarms — optional **voice** replies |
| I forget what people said | Named sessions (`Note this: …`) + extract on `/close` |
| Open loops haunt me | **Proactive** briefs and promise resurfacing (with `/quiet`) |
| Agents are dangerous when I’m impulsive | **Read-only by architecture** — no email, shell, browse, pay |
| My patterns are real | Log what I answer or ignore; evolve timing over time |

We do **not** claim Farzana diagnoses or treats ADHD.  
We claim something sharper for builders and users:

> **If it works for an ADHD mind under leadership load, it is not “nice to have.” It is necessary infrastructure for a leaky brain — and a gift for anyone who has ever lost a day.**

That is how we **sell ADHD**: not as a pity niche, but as the **highest bar**. Pass that bar, and the product is worth existing.

---

## Who else this is for (same wound, different labels)

ADHD was the **founding fire**. It is not the only passport.

| If you are… | You might feel… | Farzana is… |
|-------------|------------------|-------------|
| ADHD / ADHD-like | Leaky memory, ignored alarms, shame | External working memory that talks back |
| Alone | No one holds your commitments | Accountability without performing for a partner |
| A lone leader / founder | Too many promises, no EA | Chief of staff for **memory**, not for execution |
| Overloaded at work | Dropped follow-ups look like character | A place to close loops before they become performance |
| Tool-drowned | Notes + todos + agents, none that *care* | One aide, one vault, hard safety rails |

Same product. Different landing story. One design stress-test: **the mind that forgets under load.**

---

## The name: Farzana of Inspector Jamshed (Ishtiaq Ahmed)

I did not want another Silicon Valley codename.

I wanted a name from **our** storytelling culture — **Ishtiaq Ahmed’s Inspector Jamshed** universe of Urdu detective and espionage fiction. Local. Moral. Endless cases. A household myth for readers who grew up with digests and bookstalls.

Inspector Jamshed does not win alone. Beside him stand his children:

| Name | In the myth as many of us remember it |
|------|----------------------------------------|
| **Mehmood** | Clever, sharp — the quick mind |
| **Farooq** | Field energy — motion into danger |
| **Farzana** | Present, intelligent — she **listens carefully** and holds the thread |

In that public memory, Farzana is not the loudest hero.  
She is the one who **hears** what was said while others rush into noise.

That is the spirit of this software:

```text
You are the inspector of your own day.
Farzana catches the thread.
She files it where you can see it.
She brings open loops back — in text or voice.
You still decide.
She never seizes the badge.
She never acts on the outside world.
```

**Independent open source.** Not affiliated with or endorsed by Inspector Jamshed rights holders.  
Inspiration of *attention* — not licensed franchise IP.

**Deep dive:** [docs/INSPIRATION.md](docs/INSPIRATION.md) · [docs/STORY.md](docs/STORY.md)

---

## What Farzana does (and refuses)

| She does | She refuses |
|----------|-------------|
| Listen (Telegram text + voice) | Email, calendar write, browse, shell |
| Store in **Markdown you own** | Black-box memory you cannot edit |
| Discuss & encourage from history | Romance / therapist cosplay |
| Resurface open loops | “I’ll just handle it” agent moves |
| Adapt via patterns (logged → evolving) | Nag without `/quiet` and caps |

**Architecture of memory:** files are truth; the model only gets a temporary view.  
See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## Features (current)

| Area | Support |
|------|---------|
| Telegram text | Yes |
| Voice → Whisper | Yes |
| Voice replies (TTS) | Yes |
| Per-user Markdown vault | Yes |
| Sessions + `/close` extract | Yes |
| Proactive briefs / promise scan | Yes (UTC; timezones on roadmap) |
| Single-user allowlist or open mode | Yes |
| External actions | **Never** |

---

## Quick start

```bash
git clone https://github.com/maazbin/farzana.git
cd farzana
cp .env.example .env
# Put TELEGRAM_* and OPENAI_API_KEY in .env only — never commit

uv sync
uv run farzana health
uv run farzana --no-webhook   # http://127.0.0.1:8000
```

Full setup (webhook, **optional ngrok**, single-user Telegram): **[docs/SETUP.md](docs/SETUP.md)**  

Optional VPS/Terraform templates (placeholders only — no private hosts in git): **[deploy/README.md](deploy/README.md)**

### Secrets

Never commit `.env`, `*.pem`, `server.env`, or API tokens.  
If a key leaked — **rotate it**.

---

## Using the bot

1. Deploy or run with `PUBLIC_BASE_URL` + webhook.  
2. Telegram → bot → `/start` (your allowlisted account if single-user).  
3. Send **text** or a **voice note** — the ADHD-friendly path.  
4. `Note this: meeting` → dump → `/close`.  
5. `/brief` when you need the board reviewed.  
6. `/quiet` when the world is too loud.

---

## Docs map

| Doc | Content |
|-----|---------|
| [STORY.md](docs/STORY.md) | Founder ADHD origin + product arc |
| [INSPIRATION.md](docs/INSPIRATION.md) | Inspector Jamshed / Farzana mythology |
| [MOTIVATION.md](docs/MOTIVATION.md) | Why / when / when not |
| [RULES.md](docs/RULES.md) | Hard product rules |
| [ROADMAP.md](docs/ROADMAP.md) | Future (also GitHub Issues) |

---

## Contributing

[CONTRIBUTING.md](CONTRIBUTING.md) · [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) · [AGENTS.md](AGENTS.md)

---

## License

[MIT](LICENSE)

---

*I built this because my mind drops threads under load.*  
*I open-sourced it so other leaky, ambitious, alone-carrying minds can hold a better thread too.*  
*Not a cure. A teammate who listens.*
