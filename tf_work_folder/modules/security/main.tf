resource "aws_cognito_user_pool" "user_auth_pool" {
    name = "${var.project_name}-user-pool"
    account_recovery_setting {
        recovery_mechanism {
        name     = "verified_email"
        priority = 1
        }
    }
    admin_create_user_config {
      allow_admin_create_user_only = true
    }
    deletion_protection = "ACTIVE"
    user_pool_tier = "LITE"
    password_policy {
        minimum_length    = 8
        require_uppercase = true
        require_lowercase = true
        require_numbers   = true
        require_symbols   = true
    }
    alias_attributes = ["email"]
    auto_verified_attributes = ["email"]
}