# Architecture

> How Farzana is shaped. Update when modules move.  
> Stack versions and host choices: [STACK.md](./STACK.md)

---

## 1. Goals of the architecture

1. **HTTP is dumb and fast** — Telegram webhooks ACK quickly.  
2. **Jobs own intelligence and I/O** — capture, LLM, later TTS/proactive.  
3. **Vault is truth** — Markdown on disk.  
4. **Read-only externally** — tool allowlist enforced by simply not implementing forbidden tools.  
5. **Personal single-user** — allowlist, not multi-tenant RBAC.

---

## 2. Logical diagram

```
                    Telegram
                       │
                       │ webhook HTTPS (ngrok local / Caddy EC2)
                       ▼
              ┌────────────────────┐
              │  FastAPI (farzana.main:app)
              │  api/routes/* thin
              └─────────┬──────────┘
                        │ delay()
                        ▼
              ┌────────────────────┐
              │  Celery + Redis
              │  workers/tasks.py
              └─────────┬──────────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
     services/     services/     services/
     capture       dialogue      telegram
          │             │             │
          ▼             ▼             ▼
       vault/*.md    OpenAI API    Telegram API
```

**Local shortcut:** `CELERY_TASK_ALWAYS_EAGER=true` runs tasks in-process (no Redis).

---

## 3. Package layout (FastAPI-proper)

```text
src/Farzana/
  main.py                 # create_app(), lifespan
  core/
    config.py             # Settings / env
    security.py           # allowlist
    logging.py
  api/
    deps.py               # FastAPI Depends
    router.py             # include routers
    routes/
      health.py
      telegram.py         # webhook only
      admin.py            # set-webhook helpers
  services/
    vault.py              # markdown I/O
    capture.py
    dialogue.py
    telegram.py           # Bot API client
  workers/
    celery_app.py
    tasks.py              # handle_text_message, later proactive_*
vault/                    # runtime data (not package code)
docs/                     # product + engineering story
```

### Layer rules

| Layer | May import | Must not |
|-------|------------|----------|
| `api` | core, services (light), workers.tasks | raw OpenAI SDK, deep vault writes except via services |
| `workers` | core, services | FastAPI Request objects |
| `services` | core, external SDKs | FastAPI |
| `core` | stdlib, pydantic | services, api |

---

## 4. Request lifecycle (text message)

1. Telegram POSTs update → `POST /telegram/{secret}`.  
2. Route checks path secret + allowlist.  
3. Enqueues `handle_text_message.delay(chat_id, user_id, text)`.  
4. Returns `{"ok": true, "queued": true}` quickly.  
5. Worker: parse commands → `capture` → `dialogue` → `TelegramClient.send_message`.  
6. Vault files under `vault/inbox` or `vault/sessions`.

---

## 5. Memory architecture

```
Markdown files  ──►  (later) SQLite FTS + embeddings  ──►  retrieval pack  ──►  LLM
     ▲                         │
     └────── rebuildable ──────┘
```

**Entities (folders):**

- `inbox/` — unsessioned dumps  
- `sessions/` — named capture units  
- `promises/`, `people/`, `ideas/` — structured extracts (post v0.1)  
- `patterns/` — evolve outputs (editable)  
- `proactive/` — audit of why we spoke  
- `config/` — identity + preferences  

---

## 6. Engines map (product → code)

| Engine | Status | Code home |
|--------|--------|-----------|
| Guard | v0.1 | `core/security.py` |
| Capture | v0.1 | `services/capture.py` |
| Dialogue | v0.1 thin | `services/dialogue.py` |
| Close / extract | planned | `services/close.py` |
| Retrieve | planned | `services/retrieve.py` |
| Rhythm / Proactive | planned | `workers/tasks.py` + services |
| Voice out | planned | `services/tts.py` |
| Evolve | planned | `services/evolve.py` |

---

## 7. Trust boundaries

| Boundary | Mechanism |
|----------|-----------|
| Who can talk to bot | `TELEGRAM_ALLOWLIST_USER_IDS` |
| Who can hit webhook | path secret (+ optional Telegram secret_token later) |
| What bot can do | no tool registry for external actions |
| What is true | vault files user can open |

---

## 8. Deployment shapes

### Local dev

- uvicorn `farzana.main:app`  
- ngrok → `PUBLIC_BASE_URL`  
- eager Celery **or** Redis + worker  

### AWS cheap EC2 (later)

- PM2: `farzana-api`, `farzana-worker`, (`farzana-beat`)  
- redis-server apt  
- Caddy TLS  
- vault on disk + S3 backup  

See [STACK.md](./STACK.md).

---

## 9. Extension points (future-safe)

1. `services/channels/` if WhatsApp added — keep Telegram as one adapter.  
2. `services/retrieve.py` without changing webhook.  
3. Beat schedule in Celery for proactive without touching routes.  
4. Import pipeline: drop files into `vault/inbox` from Pocket exports.
