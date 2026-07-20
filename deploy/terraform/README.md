# Terraform (optional AWS)

Scaffold a small VM for Farzana. **Not required** — most people run locally or on any VPS.

## Defaults are placeholders

| Variable | Default |
|----------|---------|
| `domain` | `farzana.example.com` |
| `aws_profile` | `default` |
| `instance_type` | `t3.micro` |

Override in **gitignored** `terraform.tfvars` (copy from `terraform.tfvars.example`).

## Apply

```bash
cd deploy/terraform
cp terraform.tfvars.example terraform.tfvars
# edit domain, profile, region

terraform init
terraform plan
terraform apply
```

Outputs: Elastic IP, SSH command, paths. Point **your** DNS at the IP (or set `create_dns` + Route53 zone).

Then set on the server:

```env
PUBLIC_BASE_URL=https://your-real-domain.example
```

and follow [../README.md](../README.md) / [../../docs/SETUP.md](../../docs/SETUP.md).

## Secrets

Never commit:

- `terraform.tfvars`
- `*.tfstate*`
- SSH private keys under `deploy/keys/`
