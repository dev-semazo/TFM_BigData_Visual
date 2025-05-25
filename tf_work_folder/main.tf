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