# Redeploy app code to a remote host (optional helper).
# Usage:
#   $env:FARZANA_HOST = "your.server.ip"
#   $env:FARZANA_SSH_KEY = "C:\path\to\key.pem"
#   $env:FARZANA_DOMAIN = "https://farzana.example.com"   # PUBLIC_BASE_URL
#   .\deploy\redeploy.ps1

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

$hostName = $env:FARZANA_HOST
$key = $env:FARZANA_SSH_KEY
$publicBase = $env:FARZANA_DOMAIN
if (-not $publicBase) { $publicBase = "https://your-domain.example.com" }
if (-not $hostName -or -not $key) {
  Write-Host "Set FARZANA_HOST and FARZANA_SSH_KEY (optional FARZANA_DOMAIN for PUBLIC_BASE_URL)."
  exit 1
}
if (-not (Test-Path $key)) { throw "Missing key: $key" }

python -c @"
from pathlib import Path
import os
src, dst = Path('.env'), Path('deploy/server.env')
base = os.environ.get('FARZANA_DOMAIN', 'https://your-domain.example.com')
if not base.startswith('http'):
    base = 'https://' + base
lines=[]
if src.exists():
    for line in src.read_text(encoding='utf-8').splitlines():
        if line.startswith('PUBLIC_BASE_URL='):
            lines.append('PUBLIC_BASE_URL=' + base)
        elif line.startswith('APP_ENV='):
            lines.append('APP_ENV=dev')
        elif line.startswith('CELERY_TASK_ALWAYS_EAGER='):
            lines.append('CELERY_TASK_ALWAYS_EAGER=true')
        elif line.startswith('VAULT_PATH='):
            lines.append('VAULT_PATH=./vault')
        else:
            lines.append(line)
else:
    lines = [f'PUBLIC_BASE_URL={base}', 'CELERY_TASK_ALWAYS_EAGER=true', 'APP_ENV=dev']
text='\n'.join(lines)+'\n'
if 'PUBLIC_BASE_URL=' not in text:
    text += f'PUBLIC_BASE_URL={base}\n'
dst.write_text(text, encoding='utf-8')
print('server.env written (local only — gitignored)')
"@

tar -czf deploy/farzana-app.tgz --exclude=.venv --exclude=deploy/keys --exclude=deploy/farzana-app.tgz --exclude=__pycache__ --exclude=.git -C . pyproject.toml uv.lock requirements.txt src deploy/Caddyfile deploy/farzana.service deploy/caddy.service deploy/remote-setup.sh README.md docs

scp -o IdentitiesOnly=yes -i $key deploy/farzana-app.tgz deploy/server.env "ec2-user@${hostName}:/opt/farzana/"
ssh -o IdentitiesOnly=yes -i $key "ec2-user@$hostName" @"
set -e
cd /opt/farzana
tar -xzf farzana-app.tgz
cp server.env .env
sudo /root/.local/bin/uv sync
sudo systemctl restart farzana
sleep 2
curl -sS http://127.0.0.1:8000/health; echo
"@
Write-Host "Redeployed to $hostName"
