# Farzana — setup (any machine)

Anyone can run Farzana on a laptop or server.  
There is **no fixed domain, IP, or cloud account**. Your case may differ; the only contract is:

```env
PUBLIC_BASE_URL=https://whatever-public-https-origin-reaches-your-app
```

---

## 1. Clone and install

```bash
git clone https://github.com/maazbin/farzana.git
cd farzana
cp .env.example .env
uv sync
```

---

## 2. Telegram (single-user product — required)

Farzana is **only for one person**. There is no multi-user mode.

### Create the bot

1. Telegram → **@BotFather** → `/newbot`  
2. Copy the token → `TELEGRAM_BOT_TOKEN` in `.env`

### Bind the bot to **you**

1. **@userinfobot** → copy your numeric **Id**  
2. In `.env`:

```env
TELEGRAM_BOT_TOKEN=...
TELEGRAM_USER_ID=123456789
TELEGRAM_WEBHOOK_SECRET=long-random-string-you-invent
OPENAI_API_KEY=sk-...
```

| Setting | Meaning |
|---------|---------|
| `TELEGRAM_USER_ID` | **Your** Telegram user id (not the bot’s). Only this account works. |

Anyone else who messages the bot is rejected.

### OpenAI

https://platform.openai.com/api-keys → `OPENAI_API_KEY`

Check:

```bash
uv run farzana health
```

---

## 3. Run the API (always)

```bash
uv run farzana --no-webhook
```

API listens on **http://127.0.0.1:8000**  
Health: http://127.0.0.1:8000/health

---

## 4. Public HTTPS (required for Telegram webhooks)

Telegram must **POST** updates to a **public https** URL.  
`localhost` alone is not enough.

### Option A — ngrok (optional, great for local dev)

1. Install [ngrok](https://ngrok.com/download) and auth once:  
   `ngrok config add-authtoken YOUR_TOKEN`
2. In another terminal:

```bash
ngrok http 8000
```

3. Copy the `https://….ngrok-free.app` origin into `.env`:

```env
PUBLIC_BASE_URL=https://YOUR-SUBDOMAIN.ngrok-free.app
```

(no path, no trailing slash)

4. Register webhook (API can stay running with `--no-webhook`, or restart):

```bash
uv run farzana webhook
```

5. Free ngrok URLs **change** when you restart ngrok → update `PUBLIC_BASE_URL` and run `webhook` again.

Other tunnels (Cloudflare Tunnel, localtunnel, etc.) work the same way: any public HTTPS origin is fine.

### Option B — your domain + VPS

1. Deploy the app on a server (systemd templates under `deploy/`).  
2. TLS with Caddy/nginx (`deploy/Caddyfile` is a template — replace the hostname).  
3. DNS **A/AAAA** for your domain → server IP.  
4. `PUBLIC_BASE_URL=https://your.domain`  
5. `uv run farzana webhook`  

---

## 5. One command (webhook + server)

If `PUBLIC_BASE_URL` is already set in `.env`:

```bash
uv run farzana
```

This registers the Telegram webhook from env, then starts `:8000`.  
It does **not** start ngrok or any cloud for you.

```bash
uv run farzana --force        # start API even if webhook fails
uv run farzana --no-webhook   # API only
```

---

## 6. Use the bot

1. Open your bot in Telegram (same account as `TELEGRAM_USER_ID`).  
2. `/start`  
3. Text or **voice note**  
4. `Note this: …` · `/close` · `/brief` · `/quiet`  

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Bot silent | Webhook URL must be https; re-run `farzana webhook` after tunnel URL changes |
| Not authorized | Your id must match `TELEGRAM_USER_ID` |
| ConnectTimeout to api.telegram.org | Network blocks Telegram API — VPN/proxy on the **machine running Farzana** |
| OpenAI errors | Key / billing |

---

## Optional: cloud / Terraform

Not required. See [deploy/README.md](../deploy/README.md) if you want a VM scaffold.  
Defaults use **example.com** placeholders only — never a private deployment hostname.
