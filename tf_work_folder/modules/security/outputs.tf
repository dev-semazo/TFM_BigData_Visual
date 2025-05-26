output "cognito_user_pool_id" {
    description = "User Pool ID for Cognito"
    value       = aws_cognito_user_pool.user_auth_pool.id
}