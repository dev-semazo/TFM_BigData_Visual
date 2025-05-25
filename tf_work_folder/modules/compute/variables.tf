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