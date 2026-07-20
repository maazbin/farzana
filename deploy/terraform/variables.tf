variable "aws_profile" {
  description = "AWS CLI profile name"
  type        = string
  default     = "default"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project" {
  type    = string
  default = "farzana"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "instance_type" {
  description = "Prefer free-tier eligible types (t3.micro / t2.micro)"
  type        = string
  default     = "t3.micro"
}

variable "volume_size_gb" {
  type    = number
  default = 20
}

variable "domain" {
  description = "Public hostname for PUBLIC_BASE_URL and Caddy TLS (your domain)"
  type        = string
  default     = "farzana.example.com"
}

variable "ssh_cidr" {
  description = "Who may SSH (tighten in production)"
  type        = string
  default     = "0.0.0.0/0"
}

variable "create_dns" {
  description = "If true, create Route53 A record (needs hosted_zone_id)"
  type        = bool
  default     = false
}

variable "hosted_zone_id" {
  description = "Route53 hosted zone id (only if create_dns)"
  type        = string
  default     = ""
}
