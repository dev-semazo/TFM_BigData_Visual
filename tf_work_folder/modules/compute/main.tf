

resource "aws_lambda_function" "lambda_web_logic_core" {
    function_name = "${var.project_name}web-logic-core"
    handler       = "web_logic_core.handler"
    runtime       = "python3.9"
    role          = "arn:aws:iam::${var.account_number}:role/core_app_lambda"
    s3_bucket     = var.code_bucket
    s3_key        = "lambda_functions/web_logic_core.zip"
    
}

