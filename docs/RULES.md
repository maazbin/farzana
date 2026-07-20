# Rules — product + engineering (must not casually break)

> If a PR conflicts with this file, update this file **deliberately** or reject the PR.

---

## A. Product rules

### A1. Read-only externally (hard)

**Allowed side effects:**

- Read/write **vault Markdown** (whitelisted paths).  
- Search vault index.  
- Send **text/voice only to the allowed user** on Telegram.  
- Schedule jobs that only do the above.  
- **Read** PC essentials into the vault (calendar/mail/files) when the user enables a reader — **never write/send/book**.  
- Long Telegram audio in **/listen** mode (Pocket-style capture).

**Forbidden (no exceptions without product decision):**

- Email **send**, calendar **write**, browser automation as agent, shell, payments, social posts.  
- Arbitrary HTTP except OpenAI/Telegram (and optional read-only OAuth providers).  
- Multi-user / open bot mode.

### A2. Markdown is source of truth

- Vectors/SQLite are **caches**. Rebuildable.  
- Never store the only copy of a memory inside an LLM provider thread.  
- User edits to `.md` files win on next cycle.

### A3. Personality (Jarvis)

- Respectful, brief, competent.  
- No pet names, flirtation, “I’m always here for you,” therapist role.  
- At most **one** clarifying question when unclear.  
- Do not invent facts not grounded in vault (say when unsure).

### A4. Proactivity discipline (Option C)

- Cap autonomous messages (default **1–3/day**).  
- Respect quiet mode and proactivity level.  
- Log **why** each proactive message fired (`vault/proactive/`).  
- Prefer voice for high-signal resurfacing when enabled.

### A5. Channel

- **Telegram** is v1.  
- WhatsApp only as later adapter with 24h/template constraints understood.  
- Never unofficial WhatsApp reverse-engineering.

### A6. Claims / positioning

- No medical claims (“treats ADHD”).  
- ADHD = design stress-test language, optional segment, not diagnosis product.

---

## B. Engineering rules

### B1. Layering (FastAPI structure)

```
api/          # HTTP only — validate, authz, enqueue
services/     # domain + adapters (vault, telegram, llm)
workers/      # Celery tasks
core/         # config, security, logging
```

- Routes must stay **thin**.  
- No OpenAI calls inside route handlers (use services/tasks).  
- No vault path math in routes.

### B2. Security

- Allowlist empty ⇒ **deny all**.  
- Webhook path secret required.  
- Secrets only in `.env` / SSM — never commit.  
- Do not log full message bodies at INFO in production later (PII).

### B3. Async / jobs

- Webhook returns quickly; heavy work in Celery (or eager only for local smoke).  
- Windows workers: `--pool=solo` when using real Celery.

### B4. Dependencies

- Prefer stdlib + small stack.  
- No LangChain agent tool-runners in v1.  
- No second TTS vendor unless OpenAI voice fails.

### B5. Docs

- Product/architecture changes update `docs/` in the **same PR**.  
- Stack changes update `docs/STACK.md`.

### B6. Testing mindset

- Capture path must write vault even if LLM fails.  
- Unauthorized users never get vault writes.

---

## C. Decision log shortcuts

| Decision | Rule reference |
|----------|----------------|
| No external tools | A1 |
| Telegram not WhatsApp v1 | A5, docs/STACK |
| OpenAI TTS | docs/STACK |
| PM2 not Docker v1 | docs/STACK |
| No diarization v1 | docs/STORY |
