

resource "aws_lambda_function" "lambda_web_logic_core" {
    function_name = "${var.project_name}web-logic-core"
    handler       = "web_logic_core.handler"
    runtime       = "python3.9"
    role          = "arn:aws:iam::${var.account_number}:role/core_app_lambda"
    s3_bucket     = var.code_bucket
    s3_key        = "lambda_functions/web_logic_core.zip"
    vpc_config {
        security_group_ids = [var.security_group_id]
        subnet_ids         = [var.subnet_id]
    }
}

resource "aws_lb" "web_logic_core_lb" {
    name               = "${var.project_name}-web-logic-core-lb"
    internal           = true
    load_balancer_type = "application"
    subnets            = [var.subnet_id]
}

resource "aws_lb_target_group" "web_logic_core_tg" {
    name = "${var.project_name}-web-logic-core-tg"
    target_type = "lambda"
    vpc_id = var.vpc_id
    health_check {
        enabled = false # Generalmente deshabilitado para Lambdas
    }
}

resource "aws_lambda_permission" "with_lb" {
  statement_id  = "AllowExecutionFromlb"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_web_logic_core.function_name
  principal     = "elasticloadbalancing.amazonaws.com"
  source_arn    = aws_lb_target_group.web_logic_core_tg.arn
}

resource "aws_lb_target_group_attachment" "test" {
  target_group_arn = aws_lb_target_group.web_logic_core_tg.arn
  target_id        = aws_lambda_function.lambda_web_logic_core.arn
  depends_on       = [aws_lambda_permission.with_lb]
}

resource "aws_lb_listener" "http_listener" {
  load_balancer_arn = aws_lb.web_logic_core_lb.arn
  port              = 80 # Puerto que el NLB escucha
  protocol          = "HTTP" # Protocolo del listener

  default_action {
    target_group_arn = aws_lb_target_group.web_logic_core_tg.arn
    type             = "forward"
  }
}