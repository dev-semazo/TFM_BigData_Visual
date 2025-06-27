
resource "aws_lambda_function" "bronce_etl_logic" {
    function_name = "${var.project_name}bronce_silver"
    handler       = "etl_bronce.lambda_handler"
    runtime       = "python3.9"
    role          = "arn:aws:iam::${var.account_number}:role/core_app_lambda"
    s3_bucket     = var.code_bucket
    s3_key        = "etl_bronce.zip"
    memory_size   = 256
    timeout       = 600
    id            = "tfm-educ-app-bronce_silver"
    layers        = [
          - "arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python39:29",
    ]
}

