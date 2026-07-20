# How OpenClaw & Hermes install “in one command” and talk on Telegram  
## vs what Farzana is doing

> Reference for product and engineering. Not an install guide for those tools.

---

## 1. What those products are

| | **OpenClaw** (and similar “personal AI agent” runtimes) | **Hermes**-class agent stacks | **Farzana** |
|--|--------------------------------------------------------|----------------------------------|-----------|
| Job | Agent that can **do work** on a machine/cloud (tools, shell, browser, etc.) | Agent framework / runtime with tools + channels | **Read-only memory aide** |
| Install UX | One-liner installer + wizard | npm/pip/CLI bootstrap | App repo + `.env` (this project) |
| Danger model | High if tools enabled | High if tools enabled | Low by design (no external act tools) |

They solve “remote hands / autonomous worker.”  
Farzana solves “external working memory that initiates.”  
**We deliberately are not them** (see original brief).

---

## 2. Why “one command” install feels magical

A typical agent product ships a **distribution**, not a blank FastAPI app:

```text
curl -fsSL https://…/install.sh | bash
# or: npm create … / pipx install …
```

That script usually:

1. **Detects OS** and installs a binary or Node/Python runtime deps.  
2. Drops a **CLI** on your `PATH` (`openclaw`, `hermes`, …).  
3. Creates a **config directory** (`~/.openclaw`, etc.).  
4. Runs an **interactive wizard**: API keys, model, channels.  
5. Optionally installs a **background service** (launchd/systemd) so the agent stays up.  
6. Bundles **defaults** (prompts, tool plugins, channel adapters).

So “one command” = **packaging + onboarding product**, not less software. Under the hood there is still a long-running process, credentials, and a channel loop.

Farzana is currently a **source-first personal build** (you own the code). We can add a one-liner later; it is not the v1 priority.

---

## 3. How they connect to Telegram (why it feels instant)

### Shared ingredients (same as us)

1. Create a bot with **@BotFather** → token.  
2. Put token in the agent’s config.  
3. Restrict who can talk (pairing code, allowlist, “only my user id”).  
4. Long-running process receives messages and replies.

### The trick that avoids ngrok: **long polling**

Telegram bots have two receive modes:

| Mode | How it works | Public HTTPS needed? |
|------|----------------|----------------------|
| **Long polling** | Your process calls `getUpdates` repeatedly | **No** |
| **Webhook** | Telegram POSTs to your URL | **Yes** (ngrok/EC2/TLS) |

Most personal agent installers default to **long polling** for local machines:

```text
Agent process (always on)
    │
    │  getUpdates loop
    ▼
Telegram servers  ◄── user messages on phone
    │
    │  sendMessage
    ▼
Your phone
```

No public URL, no ngrok, fewer moving parts for a laptop demo.

**Farzana v0.1 uses webhooks** (FastAPI) because:

- Matches production shape on EC2 + HTTPS.  
- Clean HTTP boundary for health/admin.  
- Celery-friendly “request → enqueue” model.

We *can* add optional long-polling mode later for zero-ngrok local dev; it is an adapter choice, not a product identity.

### Pairing flow (typical agent UX)

1. You message the bot `/start`.  
2. Bot shows a **pairing code** or asks you to paste token into CLI.  
3. Config stores `allowed_user_ids`.  
4. Unpaired users are ignored.

Same security idea as our `TELEGRAM_ALLOWLIST_USER_IDS`.

---

## 4. What happens after a Telegram message (agents vs Farzana)

### OpenClaw / Hermes-class

```text
Message → agent runtime → LLM plans → TOOLS
   (shell, browser, files, email plugins, …)
→ side effects on system/network → reply on Telegram
```

That is why installers emphasize “control your computer from Telegram.”

### Farzana

```text
Message → FastAPI webhook → Celery task
→ capture to Markdown vault → (optional) LLM dialogue
→ reply on Telegram
→ NO shell/browser/email tools
```

---

## 5. Why we still look “harder” to run today

| Friction | Why we have it | Agent products hide it by |
|----------|----------------|---------------------------|
| Clone repo + venv | You own/modify code | Prebuilt binary |
| `.env` keys | Explicit secrets | Wizard writes config |
| ngrok | Webhook mode | Long polling default |
| Redis/Celery (optional eager) | Job architecture for proactive/TTS | In-process loops often |
| No single `curl | bash` yet | Early personal codebase | Mature packaging |

This is temporary product maturity, not a law of nature.

---

## 6. Could Farzana become one-command later?

Yes, without becoming OpenClaw:

```bash
# hypothetical future
curl -fsSL https://farzana.example/install.sh | bash
Farzana init   # keys + botfather instructions
Farzana start  # pm2 or service + optional poll mode
```

Still **no tool execution**. Packaging ≠ agent.

---

## 7. Decision for this repo

| Topic | Decision |
|-------|----------|
| Copy OpenClaw tool model | **No** |
| Copy their Telegram channel idea | **Yes** (already) |
| Copy long-polling for local DX | **Optional later** |
| Copy one-line installer | **Optional later** |
| Use webhook + FastAPI now | **Yes** |

---

## 8. Further reading (external)

- OpenClaw Telegram channel docs: `https://docs.openclaw.ai/channels/telegram`  
- Search “OpenClaw install one liner” / “Hermes agent Telegram” for current install commands (they change often).

When citing competitors in product work, re-check their sites — packaging moves fast; the **agent vs read-only aide** distinction does not.
