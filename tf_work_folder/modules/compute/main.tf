data "aws_s3_object" "lambda_web_logic_core_zip_local" {
  bucket = "code-tfm-semazo"
  key    = "lambda_functions/web_logic_core.zip"
}

resource "aws_lambda_function" "lambda_web_logic_core" {
    function_name = "${var.project_name}web-logic-core"
    handler       = "web_logic_core.handler"
    runtime       = "python3.9"
    role          = "arn:aws:iam::${var.account_number}:role/core_app_lambda"
    filename      = data.aws_s3_object.lambda_web_logic_core_zip_local.body_path 
    source_code_hash = data.aws_s3_object.lambda_web_logic_core_zip_local.etag
    depends_on = [ data.aws_s3_object.lambda_web_logic_core_zip_local ]
    vpc_config {
        security_group_ids = [var.security_group_id]
        subnet_ids         = [var.subnet_id]
    }
}

