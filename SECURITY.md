# Security Policy

## Reporting a vulnerability

**Do not open a public GitHub issue for secrets or exploitable bugs.**

Email or message the maintainers privately (see GitHub profile / repo Security tab).  
Include:

- Description and impact  
- Steps to reproduce  
- Affected version / commit if known  

We aim to acknowledge within a few days.

## Secrets that must never be committed

| Item | Examples | Where it lives |
|------|----------|----------------|
| Telegram bot token | `123456:ABC…` | `.env` only |
| OpenAI (or other LLM) API keys | `sk-…` | `.env` only |
| Webhook path secret | long random string | `.env` only |
| SSH private keys | `*.pem` | `deploy/keys/` (gitignored) |
| AWS credentials | access keys | AWS profile / env, not this repo |
| Production `.env` / `server.env` | full config | server disk only |
| Terraform `terraform.tfvars` with secrets | | local only |

Templates that **are** safe: `.env.example`, `deploy/terraform/terraform.tfvars.example`.

### If you accidentally commit a secret

1. **Rotate immediately** (BotFather revoke token, OpenAI revoke key, new SSH key).  
2. Remove from git history (`git filter-repo` / BFG) if already pushed.  
3. Notify maintainers.

Assuming “we’ll rewrite history later” is not enough — **rotate first**.

## Product security principles

1. **Read-only externally** — no tools that email, browse, shell, or pay.  
2. **Webhook secret** in the URL path; treat it as a password.  
3. **Single-user only** — set `TELEGRAM_USER_ID`; reject every other Telegram account.  
4. Vault Markdown may contain sensitive life data — protect disk access and backups.  
5. Proactive messaging must respect `/quiet` and daily caps.

## Dependency / supply chain

- Pin or lock deps (`uv.lock`).  
- Review new dependencies in PRs.  
- No install scripts that curl | bash untrusted URLs in the default path without documentation.
