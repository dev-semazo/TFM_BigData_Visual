output "subnet_id" {
    description = "ID of the private subnet"
    value       = aws_subnet.private_subnet[0].id
}

output "security_group_id" {
    description = "ID of the security group"
    value       = aws_security_group.sg_lambda_core.id
}