# Farzana — Full product story

> Living document. Update when product decisions change.  
> Related: [MOTIVATION.md](./MOTIVATION.md) · [RULES.md](./RULES.md) · [ARCHITECTURE.md](./ARCHITECTURE.md) · [STACK.md](./STACK.md)

---

## One sentence

**Farzana is a personal, read-only Markdown memory aide** you talk to on Telegram: she captures what you say, stores it as files you own, and (in full form) comes back with voice and discussion when follow-through matters — without ever acting on the outside world.

**Tagline:** *The aide who listens carefully.*

---

## Inspiration (why “Farzana”)

> **Long form:** [INSPIRATION.md](./INSPIRATION.md) — Inspector Jamshed, the three children, and how listening became the product.

### The Jamshed household, in brief

In Ishtiaq Ahmed’s **Inspector Jamshed** detective/espionage novels — a staple of Urdu popular fiction for generations — Jamshed does not work alone. Beside him stand his children **Mehmood**, **Farooq**, and **Farzana**, each remembered for different strengths. Around them, a wider circle (strategists, scientists, field officers) fills out a world where cases are won by **attention and teamwork**, not by a lone genius with gadgets.

In that public memory, **Farzana** is not cast as the loudest hero. She is the one who is **present**, **sharp**, and **listens carefully**: she notices what was said, holds the thread of the case, and helps the mission move when others rush past a detail.

### From myth to product

| Farzana in the Jamshed myth (as we remember her) | Farzana the software |
|--------------------------------------------------|----------------------|
| Listens carefully in a noisy case | Captures Telegram text **and voice** without ceremony |
| Holds the thread of what mattered | Named sessions, promises, **Markdown you can open** |
| Supports the family mission without seizing the badge | **Read-only** aide — you still decide and act |
| Returns when the puzzle resurfaces | Briefs, promise scans, optional **voice** reminders |
| Loyalty as duty, not romance | Jarvis-like boundaries; no companion-bot intimacy |

The word **Farzana** also leans toward **wisdom / intelligence** in Persian and Urdu usage — a second layer under the character memory.

### The product parable

You are the inspector of your own day: too many conversations, half-promises, ideas that vanish.  
Farzana is the teammate who **caught the thread** — files it, and brings open loops back — without ever taking the case from you.

### What we are *not* claiming

- **Not** an official Inspector Jamshed product, adaptation, or licensed work.  
- **Not** a retelling of copyrighted plots or character Bibles.  
- **Inspiration only:** cultural memory of careful listening in a beloved detective household.  
- Full legal note: [INSPIRATION.md § Disclaimer](./INSPIRATION.md#disclaimer).

### Other design inspirations (tone & safety)

| Source | What we take | What we refuse |
|--------|----------------|----------------|
| **Inspector Jamshed / Farzana** | Name, listening myth, team-of-strengths | Franchise IP, fanfic as product |
| **Jarvis** (aide archetype) | Respect, brevity, competence, discretion | Superhero “I’ll just do it” hands |
| **ADHD-hard design** | External working memory, kind resurfacing | Medical claims |
| **Anti-agent stance** | Memory + discussion only | OpenClaw/Hermes tool execution |
| **Anti-companion stance** | Loyalty through attention | Romantic / therapist bot framing |

**Product role in one line:** careful listener · memory keeper · discreet resurfacer.

---

## Origin pain

The founder is a **leader under load** (and designs under **ADHD-hard constraints**):

- Ideas, work, and “someone told me X” arrive faster than notes can stick.
- Even written notes get forgotten; task notifications feel **cold** and get ignored.
- Cold systems fail the interest-based / working-memory brain.
- Wanted something that **cares enough to resurface**, discuss the day, and encourage from **real history** — not empty praise.
- Explicitly **does not** want an agent that emails, browses, codes, or pays (OpenClaw / Hermes class).
- Explicitly **does not** want a romantic / companion / therapist bot (Replika / Dot class).

**Product name:** Farzana.

---

## What it is / is not

| Is | Is not |
|----|--------|
| External working memory | Task executor agent |
| Capture + remember + remind + discuss | Calendar/email automation |
| Jarvis-style aide (respectful, competent) | Partner / girlfriend / dependency bot |
| Markdown vault you can edit | Opaque cloud-only “AI memory” |
| Proactive when *memory* says so | Spammy always-on chatter |
| Software on Telegram first | Hardware stenographer (Pocket class) |

---

## Heart of the product (non-negotiable)

1. **Capture** — text/voice, named sessions (“Note this: Sarah call”).  
2. **Transparent memory** — Markdown source of truth.  
3. **Proactive discussion** — morning/evening + “talks when it thinks needed.”  
4. **Voice out (TTS)** — reminders that cut through notification blindness.  
5. **Evolve** — learn timing/topics from respond vs ignore (editable pattern files).  
6. **Read-only by architecture** — no external side-effect tools.  
7. **Controls** — quiet mode, proactivity levels, “why did you message?”

**Option C locked:** ambitious proactivity in v1 (with hard caps), not a passive notepad.

---

## Audience (ADHD is design stress-test, not the only market)

| Persona | Same core need |
|---------|----------------|
| ADHD brains | External working memory + kind resurfacing |
| Lone people | Accountability without social debt |
| Lone leaders / founders | Chief-of-staff for memory |
| Overloaded / “failing” employees | Close loops before performance pain |
| Pattern-seekers | System that learns *their* cycles |

**Public framing:** external working memory that comes back to you.  
**Internal truth:** designed for ADHD + leadership load; sold broader.

---

## Competitive posture (short)

| Neighbor | They win | We win |
|----------|----------|--------|
| **Pocket / Plaud** | Hardware capture quality | No device; proactive aide; owned MD |
| **OpenClaw / Hermes** | One-command agent that *does* work | Safety; we **refuse** execution tools |
| **Dot / companions** | Relationship stickiness | Boundaried Jarvis; not intimacy |
| **Todoist / reminders** | Lists and schedules | Dialogue + context + voice + patterns |

**Positioning line:**  
> Pocket is a wearable stenographer. OpenClaw is a remote hands agent. Farzana is a read-only chief of staff for your memory — she listens carefully and starts the conversation when it matters.

---

## Journey so far (design decisions)

1. Problem framing: forget + cold notifications + want emotional competence without intimacy.  
2. Read-only constraint for v1 safety.  
3. Jarvis personality + named sessions.  
4. Markdown as long-term memory.  
5. Telegram over WhatsApp for **proactive** free-form messages.  
6. Option C + TTS + evolve.  
7. Stack: FastAPI, Celery, Redis, OpenAI (LLM/STT/TTS), PM2, cheap AWS EC2 later; local + ngrok now.  
8. Diarization deferred; mind maps = links + optional Mermaid, not Pocket visuals.

---

## Build phases (product)

| Phase | Outcome |
|-------|---------|
| **v0.1 (now)** | Telegram webhook, allowlist, text → vault, basic dialogue |
| **v0.2** | Voice in (Whisper), session close extract → promises/people |
| **v0.3** | Hybrid search + morning/evening |
| **v0.4** | Proactive scan + OpenAI TTS voice out + caps/quiet |
| **v0.5** | Pattern evolve + optional Mermaid graphs |
| **Later** | AWS deploy, optional WhatsApp adapter (template-aware), import from capturers |

---

## Success criteria (personal)

- Captures in under a few seconds from Telegram.  
- Open promise can resurface **without** opening an app.  
- User trusts vault enough to edit it in Obsidian.  
- Never sends an external action.  
- Proactivity feels useful more often than annoying (response rate, not message count).
