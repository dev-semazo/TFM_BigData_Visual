resource "aws_lambda_function" "this" {
    function_name = "${var.project_name}web-logic-core"
    handler       = "web_logic_core.handler"
    runtime       = "python3.9"
    role          = "arn:aws:iam::${var.account_number}:role/core_app_lambda"
    filename      = "s3://${var.code_bucket}/lambda_functions/web_logic_core.zip"
}