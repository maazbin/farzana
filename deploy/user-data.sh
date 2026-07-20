#!/bin/bash
set -euo pipefail
exec > /var/log/farzana-bootstrap.log 2>&1

dnf update -y
dnf install -y git tar gzip curl

# uv
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="/root/.local/bin:$PATH"
echo 'export PATH="/root/.local/bin:$PATH"' >> /root/.bashrc

# Caddy (HTTPS reverse proxy)
dnf install -y 'dnf-command(copr)' || true
# Official Caddy RPM via cloudsmith-style install for AL2023
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | tee /etc/pki/rpm-gpg/caddy.gpg >/dev/null 2>&1 || true
# fallback: download static caddy binary
cd /usr/local/bin
curl -sL "https://caddyserver.com/api/download?os=linux&arch=amd64" -o caddy
chmod +x caddy

# App dir
mkdir -p /opt/farzana
useradd -r -s /sbin/nologin farzana 2>/dev/null || true

# Placeholder unit (real unit installed by deploy script)
cat > /etc/systemd/system/farzana.service <<'EOF'
[Unit]
Description=Farzana API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/farzana
Environment=PATH=/root/.local/bin:/usr/local/bin:/usr/bin
EnvironmentFile=-/opt/farzana/.env
ExecStart=/root/.local/bin/uv run farzana --no-webhook --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
echo "bootstrap done" > /opt/farzana/BOOTSTRAP_OK
