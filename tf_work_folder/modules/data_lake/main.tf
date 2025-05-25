resource "aws_s3_bucket" "bronze_bucket" {
    bucket = "${var.project_name}bronze"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "bronze_encryption" {
  bucket = aws_s3_bucket.bronze_bucket.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "athena_query_exp" {
  bucket = aws_s3_bucket.bronze_bucket.id
  rule {
    id = "query_results_expiration"
    filter {
      prefix = "athena_results/"
    }
    expiration {
      days = 5
    }
    status = "Enabled"
  }
}

resource "aws_s3_bucket" "silver_bucket" {
    bucket = "${var.project_name}silver"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "silver_encryption" {
  bucket = aws_s3_bucket.silver_bucket.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "AES256"
    }
  }
}

resource "aws_s3_bucket" "gold_bucket" {
    bucket = "${var.project_name}gold"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "gold_encryption" {
  bucket = aws_s3_bucket.gold_bucket.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "AES256"
    }
  }
}

#----------------------------------
# AWS Glue Data Catalog
#---------------------------------
resource "aws_glue_catalog_database" "bronze_db" {
  name = "${var.project_name}bronze"
  description = "Base de datos bronze del Data Lake"
}

resource "aws_glue_catalog_database" "silver_db" {
  name = "${var.project_name}silver"
  description = "Base de datos Silver del Data Lake"
}

resource "aws_glue_catalog_database" "gold_db" {
  name = "${var.project_name}gold"
  description = "Base de datos gold del Data Lake"
}

#----------------------------------
# LakeFormation
#---------------------------------

resource "aws_lakeformation_resource" "lf_bronze" {
  arn = aws_s3_bucket.bronze_bucket.arn
}

resource "aws_lakeformation_resource" "lf_silver" {
  arn = aws_s3_bucket.silver_bucket.arn
}

resource "aws_lakeformation_resource" "lf_gold" {
  arn = aws_s3_bucket.gold_bucket.arn
}

#----------------------------------
# Athena
#---------------------------------

resource "aws_athena_workgroup" "quicksight_workgroup" {
  name = "${var.project_name}athena"
  description = "Workgroup de Athena para consultas de QuickSight"
  state = "ENABLED"
  configuration {
    result_configuration {
      output_location = "s3://${var.project_name}bronze/athena_results/"
    }
    publish_cloudwatch_metrics_enabled = false
  }
}