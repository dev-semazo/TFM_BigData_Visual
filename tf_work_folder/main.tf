terraform {
    required_version = "1.2.5"
    required_providers {
        aws = {
            source  = "hashicorp/aws"
            version = ">= 2.7.0"
        }
    }
    backend "s3" {
        bucket = ""
        key    = ""
        region = ""
    }
}

variable "aws_region" {
  description = "Región de AWS para desplegar los recursos."
  type        = string
}

variable "project_name" {
  description = "Nombre del proyecto para prefijos de recursos."
  type        = string
}

#Llamado a Módulos
module "s3_data_lake" {
    source = "./modules/data_lake"
    project_name = var.project_name
    aws_region = var.aws_region
}