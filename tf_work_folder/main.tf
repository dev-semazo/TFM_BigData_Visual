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
        region = "us-east-1"
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

variable "code_bucket" {
    description = "Nombre del bucket para recursos de código."
    type        = string
}

variable "account_number" {
    description = "Numero de la cuenta AWS."
    type        = string
}



#Llamado a Módulos
module "s3_data_lake" {
    source = "./modules/data_lake"
    project_name = var.project_name
    aws_region = var.aws_region
}

module "app_web" {
    source = "./modules/app_web"
    project_name = var.project_name
    aws_region = var.aws_region
}

module "network" {
    source = "./modules/network"
    project_name = var.project_name
    aws_region = var.aws_region
    account_number = var.account_number
}

module "compute" {
    source = "./modules/compute"
    project_name = var.project_name
    aws_region = var.aws_region
    code_bucket = var.code_bucket
    account_number = var.account_number
    subnet_id = module.network.subnet_id
    security_group_id = module.network.security_group_id
}

module "security" {
    source = "./modules/security"
    project_name = var.project_name
    aws_region = var.aws_region
}

module "integration" {
    source = "./modules/integration"
    project_name = var.project_name
    aws_region = var.aws_region
    account_number = var.account_number
    code_bucket = var.code_bucket
    lambda_name = module.compute.lambda_name
    lambda_arn = module.compute.lambda_arn
    cognito_user_pool_id = module.security.cognito_user_pool_id
    security_group_id = module.network.security_group_id
    subnet_id = module.network.subnet_id
}
