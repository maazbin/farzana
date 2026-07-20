# Farzana — simple setup

The app **does not know about ngrok**. It only reads **`PUBLIC_BASE_URL`** from `.env`  
(your public HTTPS base that reaches this machine on port 8000).  
Locally you often fill that with an ngrok URL; in prod, your real domain.

---

## Once

```powershell
cd C:\Users\ABC\Desktop\d\myDay
uv sync
notepad .env
```

| Variable | Meaning |
|----------|---------|
| `TELEGRAM_BOT_TOKEN` | From @BotFather |
| `TELEGRAM_ALLOWLIST_USER_IDS` | Your id from @userinfobot |
| `TELEGRAM_WEBHOOK_SECRET` | Random string you invent |
| `OPENAI_API_KEY` | OpenAI key |
| `PUBLIC_BASE_URL` | Public https base **no path** (see below) |
| `CELERY_TASK_ALWAYS_EAGER` | `true` for easy local |
| `HTTPS_PROXY` | Optional if Telegram API is blocked |

### `PUBLIC_BASE_URL` examples

```env
# local tunnel (you run the tunnel yourself)
PUBLIC_BASE_URL=https://abc123.ngrok-free.app

# production later
PUBLIC_BASE_URL=https://farzana.yourdomain.com
```

---

## Every day

**1. Expose port 8000** (your choice — ngrok, cloudflare tunnel, reverse proxy, etc.)

```powershell
ngrok http 8000
```

Put the https origin into `.env` as `PUBLIC_BASE_URL` (if it changed).

**2. One command — webhook + server**

```powershell
uv run farzana
```

That:

1. Reads `PUBLIC_BASE_URL` from `.env`  
2. Tells Telegram: send updates to `{PUBLIC_BASE_URL}/telegram/{SECRET}`  
3. Starts FastAPI on **:8000**

**3.** Message the bot on Telegram.

---

## If Telegram API times out

Your PC cannot open `api.telegram.org` (block/firewall). Then:

1. Turn on **VPN**, or set in `.env`:

```env
HTTPS_PROXY=http://127.0.0.1:7890
```

2. Test: `curl https://api.telegram.org`  
3. `uv run farzana` again  

Or start API only while you fix network:

```powershell
uv run farzana --no-webhook
# later, with VPN:
uv run farzana webhook
```

Force start even if webhook fails:

```powershell
uv run farzana --force
```

---

## Commands

| Command | Does |
|---------|------|
| `uv run farzana` | Webhook from `.env` + API :8000 |
| `uv run farzana --reload` | Same + reload |
| `uv run farzana --no-webhook` | API only |
| `uv run farzana webhook` | Webhook only |
| `uv run farzana health` | Print config |
