# Farzana infrastructure (Terraform)

**Preferred way to create/change AWS resources.**  
App deploys stay in PowerShell/`uv`; infra is Terraform.

## Layout

```text
deploy/terraform/     # this module
deploy/keys/          # SSH private key (gitignored; written by Terraform)
deploy/user-data.sh   # EC2 bootstrap
deploy/infra.env      # generated summary (gitignored optional)
```

## Prerequisites

- [Terraform](https://developer.hashicorp.com/terraform/install) ≥ 1.5  
- AWS CLI profile **`dev`** configured  
- Domain you control (default `farzana.jambits.io`)

## First-time apply (greenfield)

```powershell
cd deploy\terraform
copy terraform.tfvars.example terraform.tfvars
# edit if needed

terraform init
terraform plan
terraform apply
```

Outputs:

- `elastic_ip` — put DNS **A** record here (or enable Route53 below)  
- `ssh_command`  
- private key written to `deploy/keys/farzana-dev.pem`

Then deploy the app:

```powershell
cd ..\..
# set PUBLIC_BASE_URL=https://farzana.jambits.io in .env / deploy/server.env
.\deploy\redeploy.ps1
.\deploy\finish-after-dns.ps1
```

## DNS

### Recommended (simple TLS with Caddy)

At your DNS host (or Cloudflare **DNS only / grey cloud**):

```text
A  farzana.jambits.io  →  <elastic_ip from terraform output>
```

**Do not** orange-cloud proxy until you intentionally configure Cloudflare origin SSL.

### Optional: Route53 via Terraform

```hcl
# terraform.tfvars
create_dns     = true
hosted_zone_id = "Z...."
```

## Variables

| Name | Default | Notes |
|------|---------|--------|
| `aws_profile` | `dev` | |
| `aws_region` | `us-east-1` | |
| `instance_type` | `t3.micro` | free-tier friendly |
| `domain` | `farzana.jambits.io` | used for docs / infra.env |
| `ssh_cidr` | `0.0.0.0/0` | tighten later |
| `create_dns` | `false` | set true + zone id for Route53 |

## Import existing manual resources (optional)

If you already created resources by hand (current dev box), either:

1. **Keep them** and use Terraform only for the next environment, or  
2. **Import** (IDs from `deploy/infra.env`), then `terraform plan` until clean:

```powershell
terraform import aws_instance.app i-xxxxxxxx
terraform import aws_eip.app eipalloc-xxxxxxxx
terraform import aws_security_group.app sg-xxxxxxxx
# key pair / tls key: usually recreate via Terraform rather than import
```

Importing a hand-made key pair is awkward; for a clean state prefer:

```powershell
terraform destroy   # only if safe
terraform apply
.\deploy\redeploy.ps1
```

## Destroy

```powershell
terraform destroy
```

Releases EIP and instance (watch costs / free tier).
