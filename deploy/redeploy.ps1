# Redeploy app code to EC2 (does not recreate instance)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
$eip = "54.208.17.19"
$key = Join-Path $PSScriptRoot "keys\farzana-dev.pem"

python -c @"
from pathlib import Path
src, dst = Path('.env'), Path('deploy/server.env')
lines=[]
for line in src.read_text(encoding='utf-8').splitlines():
    if line.startswith('PUBLIC_BASE_URL='): lines.append('PUBLIC_BASE_URL=https://farzana.jambits.io')
    elif line.startswith('APP_ENV='): lines.append('APP_ENV=dev')
    elif line.startswith('CELERY_TASK_ALWAYS_EAGER='): lines.append('CELERY_TASK_ALWAYS_EAGER=true')
    elif line.startswith('VAULT_PATH='): lines.append('VAULT_PATH=./vault')
    else: lines.append(line)
text='\n'.join(lines)+'\n'
dst.write_text(text, encoding='utf-8')
"@

tar -czf deploy/farzana-app.tgz --exclude=.venv --exclude=deploy/keys --exclude=deploy/farzana-app.tgz --exclude=__pycache__ --exclude=.git -C . pyproject.toml uv.lock requirements.txt src deploy/Caddyfile deploy/farzana.service deploy/caddy.service deploy/remote-setup.sh README.md docs

scp -o IdentitiesOnly=yes -i $key deploy/farzana-app.tgz deploy/server.env "ec2-user@${eip}:/opt/farzana/"
ssh -o IdentitiesOnly=yes -i $key "ec2-user@$eip" @"
set -e
cd /opt/farzana
tar -xzf farzana-app.tgz
cp server.env .env
sudo /root/.local/bin/uv sync
sudo systemctl restart farzana
sleep 2
curl -sS http://127.0.0.1:8000/health; echo
"@
Write-Host "Redeployed."
