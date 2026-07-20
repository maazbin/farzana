# After DNS for your domain points at your host, restart TLS proxy and register webhook.
# Usage:
#   $env:FARZANA_HOST = "203.0.113.10"
#   $env:FARZANA_SSH_KEY = "C:\path\to\key.pem"
#   $env:FARZANA_DOMAIN = "farzana.example.com"
#   .\deploy\finish-after-dns.ps1

$ErrorActionPreference = "Stop"
$hostName = $env:FARZANA_HOST
$key = $env:FARZANA_SSH_KEY
$domain = $env:FARZANA_DOMAIN

if (-not $hostName -or -not $key -or -not $domain) {
  Write-Host "Set FARZANA_HOST, FARZANA_SSH_KEY, and FARZANA_DOMAIN environment variables."
  Write-Host "Example:"
  Write-Host '  $env:FARZANA_HOST = "your.server.ip"'
  Write-Host '  $env:FARZANA_SSH_KEY = "C:\path\to\key.pem"'
  Write-Host '  $env:FARZANA_DOMAIN = "farzana.example.com"'
  exit 1
}
if (-not (Test-Path $key)) { throw "Missing key: $key" }

Write-Host "Checking DNS for $domain ..."
try {
  $r = Resolve-DnsName $domain -Type A -ErrorAction Stop
  Write-Host ($r | Format-Table -AutoSize | Out-String)
} catch {
  Write-Host "DNS not ready. Create an A record: $domain -> your server IP"
  throw
}

ssh -o IdentitiesOnly=yes -i $key "ec2-user@$hostName" @"
set -e
echo 'Restarting Caddy for TLS...'
sudo systemctl restart caddy
sleep 15
echo 'Local health:'
curl -sS http://127.0.0.1:8000/health; echo
echo 'Public health (HTTPS):'
curl -sS -o /dev/null -w '%{http_code}\n' https://$domain/health || true
echo 'Registering Telegram webhook...'
cd /opt/farzana
sudo /root/.local/bin/uv run farzana webhook
echo DONE
"@
