# Run AFTER A record farzana.jambits.io -> 54.208.17.19 resolves
$ErrorActionPreference = "Stop"
$eip = "54.208.17.19"
$key = Join-Path $PSScriptRoot "keys\farzana-dev.pem"
if (-not (Test-Path $key)) { throw "Missing $key" }

Write-Host "Checking DNS..."
try {
  $r = Resolve-DnsName farzana.jambits.io -Type A -ErrorAction Stop
  Write-Host ($r | Format-Table -AutoSize | Out-String)
} catch {
  Write-Host "DNS not ready yet. Create A record: farzana.jambits.io -> $eip"
  throw
}

ssh -o IdentitiesOnly=yes -i $key "ec2-user@$eip" @"
set -e
echo 'Restarting Caddy for TLS...'
sudo systemctl restart caddy
sleep 15
echo 'Local health:'
curl -sS http://127.0.0.1:8000/health; echo
echo 'Public health (HTTPS):'
curl -sS -o /dev/null -w '%{http_code}\n' https://farzana.jambits.io/health || true
echo 'Registering Telegram webhook...'
cd /opt/farzana
sudo /root/.local/bin/uv run farzana webhook
echo DONE
"@
