#!/bin/bash
# Run on the EC2 instance after code is in /opt/farzana
set -euo pipefail
export PATH="/root/.local/bin:$PATH"

cd /opt/farzana

# Install uv if missing
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="/root/.local/bin:$PATH"
fi

# Caddy binary
if [ ! -x /usr/local/bin/caddy ]; then
  curl -sL "https://caddyserver.com/api/download?os=linux&arch=amd64" -o /usr/local/bin/caddy
  chmod +x /usr/local/bin/caddy
fi

mkdir -p /etc/caddy
cp /opt/farzana/deploy/Caddyfile /etc/caddy/Caddyfile
cp /opt/farzana/deploy/farzana.service /etc/systemd/system/farzana.service
cp /opt/farzana/deploy/caddy.service /etc/systemd/system/caddy.service

# Python deps
uv sync

# Ensure env
if [ ! -f /opt/farzana/.env ]; then
  echo "ERROR: /opt/farzana/.env missing"
  exit 1
fi

systemctl daemon-reload
systemctl enable farzana caddy
systemctl restart farzana
sleep 2
systemctl restart caddy
sleep 2
systemctl --no-pager status farzana || true
systemctl --no-pager status caddy || true
curl -sS http://127.0.0.1:8000/health || true
echo "remote-setup done"
