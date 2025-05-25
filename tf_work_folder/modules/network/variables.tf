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