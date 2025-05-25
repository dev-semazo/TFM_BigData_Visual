variable "aws_region" {
  description = "Región de AWS para desplegar los recursos."
  type        = string
}

variable "project_name" {
  description = "Nombre del proyecto para prefijos de recursos."
  type        = string
}

variable "code_bucket" {
  description = "Nombre del bucket para recursos de código."
  type        = string
}

variable "account_number" {
  description = "Numero de la cuenta AWS."
  type        = string
}
variable "subnet_id" {
  description = "Lista de IDs de subredes para la configuración de VPC."
  type        = string
}
variable "security_group_id" {
  description = "ID del grupo de seguridad para la función Lambda."
  type        = string
}