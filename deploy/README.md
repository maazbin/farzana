# Farzana AWS dev (profile `dev`)

## Infrastructure: use Terraform

New/changed AWS resources should go through:

```text
deploy/terraform/
```

See **[terraform/README.md](./terraform/README.md)**.  
Manual `aws ec2 …` clicks/scripts are legacy for the first box only.

---

## Live resources (current hand-built dev box)

| Item | Value |
|------|--------|
| AWS profile | `dev` |
| Region | `us-east-1` |
| Instance | see `infra.env` (`farzana-dev`, **t3.micro**) |
| Elastic IP | **54.208.17.19** |
| Security group | `farzana-dev-sg` (22, 80, 443) |
| SSH key | `deploy/keys/farzana-dev.pem` (**do not commit**) |
| App path | `/opt/farzana` |
| Domain | `https://farzana.jambits.io` |
| `PUBLIC_BASE_URL` | `https://farzana.jambits.io` |

Farzana API + Caddy are **running** on the instance. Health on the box:

```bash
curl http://127.0.0.1:8000/health
```

## What you must do: DNS (blocking)

Right now `farzana.jambits.io` resolves to **Cloudflare proxy IPs** (e.g. `104.21…`), not the EC2 Elastic IP. Caddy/Let's Encrypt and Telegram webhook need the name to reach **54.208.17.19**.

### Recommended (Cloudflare DNS only)

| Type | Name | Content | Proxy status |
|------|------|---------|----------------|
| **A** | `farzana` | **`54.208.17.19`** | **DNS only (grey cloud)** |

Check:

```powershell
nslookup farzana.jambits.io
# must show 54.208.17.19 — not 104.21.x / 172.67.x
```

Then:

```powershell
cd C:\Users\ABC\Desktop\d\myDay
.\deploy\finish-after-dns.ps1
```

That issues TLS and runs `farzana webhook` on the server.

Then message the bot (phone VPN if Telegram is blocked in PK).

## Why EC2 (not local)

Telegram API is blocked from many Pakistan networks. The **server in us-east-1** can call `api.telegram.org`. Your phone only needs Telegram app access (VPN if needed).

## SSH

```powershell
ssh -i deploy\keys\farzana-dev.pem ec2-user@54.208.17.19
```

## Redeploy code later

```powershell
.\deploy\redeploy.ps1
```
