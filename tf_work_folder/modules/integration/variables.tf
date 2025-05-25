variable "aws_region" {
  description = "Región de AWS para desplegar los recursos."
  type        = string
}

variable "project_name" {
  description = "Nombre del proyecto para prefijos de recursos."
  type        = string
}

variable "account_number" {
  description = "Numero de la cuenta AWS."
  type        = string
}

variable "code_bucket" {
  description = "Nombre del bucket para recursos de código."
  type        = string
}
variable "lambda_name" {
  description = "Nombre de la función Lambda."
  type        = string
}
variable "lambda_arn" {
  description = "Arn de la función Lambda."
  type        = string
}
variable "cognito_user_pool_id" {
  description = "ID del User Pool de Cognito."
  type        = string
}

variable "subnet_id" {
  description = "ID de la subred para la configuración de VPC."
  type        = string
}

variable "security_group_id" {
  description = "ID del grupo de seguridad para la función Lambda."
  type        = string
}