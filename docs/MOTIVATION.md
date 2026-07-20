# Motivation — why Farzana exists, when to use it, when not to

> Living document for future contributors (including future you).

---

## Inspiration (name & character)

Farzana is named for **careful listening**, rooted in the public memory of **Farzana** from **Inspector Jamshed** (Ishtiaq Ahmed’s Urdu detective/espionage novels — Jamshed with children **Mehmood**, **Farooq**, and **Farzana**).

In that myth, cases are won by a **team of different strengths**. Farzana’s strength, as many readers remember it, is not spectacle: it is **attention** — hearing what was said, holding the thread, returning it when the puzzle turns.

That inspiration is **emotional and functional**, not a franchise license:

- **Emotional:** memory should feel like a teammate who was actually *in the room*, not a cold list.  
- **Functional:** listen → hold in files you own → return at the right moment.  
- **Boundary:** support *your* mission the way she supports the family case — without becoming the hero, the partner, or the agent who acts without permission.

**Long form:** [INSPIRATION.md](./INSPIRATION.md) · [STORY.md § Inspiration](./STORY.md#inspiration-why-farzana).

---

## Why this product

### Human why (including the founder’s ADHD)

The project began with a founder who has **ADHD** and must still **lead**. The original cry was simple and brutal:

> Someone tells me something — I can’t note it. Even if I note it, I forget. Notifications don’t care. I want something that *cares*, reminds, discusses my day, adapts to my patterns — and **does not do the work for me**.

That is not a feature list. That is a life under load.

People (with or without an ADHD diagnosis) **lose the moment**:

- They cannot open a notes app mid-conversation.  
- They write something and never reopen it.  
- Notifications train **ignore**, not action.  
- Shame after forgetting makes colder systems worse.  
- Agent tools tempt impulsive “just fix it” moves that can wreck trust.

They need **external working memory** that:

1. Is easy to feed (Telegram text/voice).  
2. Is **visible and editable** (Markdown).  
3. **Initiates** follow-up with context and tone.  
4. Does **not** take dangerous actions when the user is overloaded or impulsive.  

**ADHD was the design stress-test.** Lone leaders, overloaded ICs, and anyone alone with too many open loops ride the same rails — without medical claims.

### Product why (gap)

| Existing tools | Gap |
|----------------|-----|
| Note apps | Passive; you must remember to open them |
| Reminders | Cold; no discussion; wrong timing |
| AI agents (OpenClaw/Hermes) | Can act — powerful and **unsafe** for this job |
| Hardware capturers (Pocket) | Great intake; weak “aide that talks to you” |
| Companion bots | Wrong relationship model |

Farzana fills: **follow-through layer** + **relational resurfacing** + **owned memory** + **read-only safety**.

---

## Why these design choices (motivation → rule)

| Choice | Motivation | When it applies |
|--------|------------|-----------------|
| Read-only architecture | Impulsivity + agent risk; trust | Always in v1; expand tools only with explicit product change |
| Markdown vault | Transparency, Obsidian, no false-memory lock-in | Always — files win over vectors |
| Telegram first | Free-form proactive messages; easy bots | v1 channel; WhatsApp only with template strategy |
| OpenAI for LLM+STT+TTS | One vendor; steerable TTS emotions | Until voice quality fails product feel |
| Celery + Redis | Proactive/TTS must not block webhooks | Production path; eager OK for local smoke |
| FastAPI | Webhooks, health, future admin | HTTP front door |
| PM2 (not Docker first) | Simple personal deploy | EC2/local ops simplicity |
| No diarization v1 | Most capture is user narration | Until full meeting uploads dominate |
| ADHD as stress-test | Hardest user for timing/ignore | Design constraint, not exclusive ICP |

---

## When to use Farzana

- You drop promises and ideas.  
- You want a **second brain that pings you**, not another dashboard.  
- You want memory **you can open in a text editor**.  
- You refuse agents that can email/browse/pay on your behalf.  
- You live in messaging apps.

## When **not** to use Farzana

- You need an agent that **does work** (deploy, code, book, email) → OpenClaw/Hermes class.  
- You need **court-grade multi-speaker transcripts** as primary → Pocket/Plaud + diarization.  
- You want a **companion** for loneliness → different product ethics.  
- You need team CRM / shared workspaces as core → not v1.

---

## Why not “just use OpenClaw with a system prompt”?

Because **prompt-only safety fails**. Agents ship with tools. Under load, users ask for action. Architecture without write-tools is the product requirement — see [RULES.md](./RULES.md) and [OPENCLAW_HERMES.md](./OPENCLAW_HERMES.md).

---

## Emotional design motivation (not therapy)

- Encouragement is **grounded in vault history**, not generic pep.  
- Tone is **Jarvis**: competence and discretion.  
- Forgetting is framed as **load**, not moral failure — without clinical claims.  
- Quiet mode exists because **over-nagging destroys trust**, especially for ADHD-like users.
