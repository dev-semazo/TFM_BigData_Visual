
resource "aws_lambda_function" "bronce_etl_logic" {
    function_name = "${var.project_name}etl_bronce"
    handler       = "etl_bronce.lambda_handler"
    runtime       = "python3.9"
    role          = "arn:aws:iam::${var.account_number}:role/core_app_lambda"
    s3_bucket     = var.code_bucket
    s3_key        = "lambda_functions/etl_bronce.zip"
}

