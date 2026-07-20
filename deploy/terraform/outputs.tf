output "instance_id" {
  value = aws_instance.app.id
}

output "elastic_ip" {
  value       = aws_eip.app.public_ip
  description = "Point DNS A record for domain here (if not using create_dns)"
}

output "public_base_url" {
  value = "https://${var.domain}"
}

output "ssh_command" {
  value = "ssh -i deploy/keys/${var.project}-${var.environment}.pem ec2-user@${aws_eip.app.public_ip}"
}

output "security_group_id" {
  value = aws_security_group.app.id
}

output "key_path" {
  value = abspath("${path.module}/../keys/${var.project}-${var.environment}.pem")
}
