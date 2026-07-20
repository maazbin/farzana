# Deploy (optional)

Farzana is designed to run **on any machine you control**: laptop, VPS, or cloud VM.  
There is **no required vendor, domain, or IP**. Set `PUBLIC_BASE_URL` to whatever public HTTPS origin reaches your process on port 8000.

```env
PUBLIC_BASE_URL=https://your-public-origin.example
```

The app does **not** know about ngrok, Cloudflare, AWS, or any brand domain. Those are *your* choices for exposing the port.

---

## Path A — Local machine (most people)

See **[docs/SETUP.md](../docs/SETUP.md)** for the full guide.

Short version:

1. `uv sync` + `.env` with Telegram + OpenAI keys  
2. `uv run farzana --no-webhook` (API on `:8000`)  
3. Optionally expose `:8000` with **ngrok** (or any tunnel) and set `PUBLIC_BASE_URL`  
4. `uv run farzana webhook`  

---

## Path B — Linux VPS / any cloud VM (generic)

1. Install Python/`uv`, put the repo in e.g. `/opt/farzana`  
2. Copy `.env.example` → `.env` (secrets stay on the server)  
3. `PUBLIC_BASE_URL=https://your.domain`  
4. Run API (systemd example: `deploy/farzana.service`) on `127.0.0.1:8000`  
5. Terminate TLS with Caddy/nginx (`deploy/Caddyfile` as a template)  
6. Point DNS A/AAAA for your domain at the VM  
7. `uv run farzana webhook`  

Example unit files in this folder are **templates** — edit paths/user for your host.

---

## Path C — Terraform (optional AWS scaffold)

`deploy/terraform/` creates a small EC2-style box (SG, key, EIP) if you want AWS.  
Defaults use placeholders (`your-domain.example.com`). Override in `terraform.tfvars` (gitignored).

```bash
cd deploy/terraform
cp terraform.tfvars.example terraform.tfvars
# edit domain, profile, region
terraform init && terraform apply
```

See [terraform/README.md](./terraform/README.md).

**Do not commit:** `terraform.tfvars`, state files, `*.pem`, `server.env`, `infra.env`.

---

## Scripts in this folder

| File | Purpose |
|------|---------|
| `farzana.service` | systemd template for the API |
| `caddy.service` / `Caddyfile` | TLS reverse-proxy templates |
| `user-data.sh` | optional cloud-init bootstrap sketch |
| `redeploy.ps1` | optional helper — **set your own host/key env vars** |
| `finish-after-dns.ps1` | optional helper after DNS points at your host |

These scripts used to embed a private deployment; they now read:

```powershell
$env:FARZANA_HOST   # e.g. 203.0.113.10 or your hostname
$env:FARZANA_SSH_KEY  # path to your private key
$env:FARZANA_DOMAIN   # e.g. farzana.example.com
```

---

## Security

Never put production tokens, SSH keys, or real IPs in git.  
Rotate any key that was ever pasted into chat or committed by mistake.
