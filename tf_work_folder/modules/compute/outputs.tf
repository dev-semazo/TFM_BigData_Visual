output "lambda_name" {
    description = "The name of the Lambda function"
    value       = aws_lambda_function.lambda_web_logic_core.function_name
}

output "lambda_arn" {
    description = "The ARN of the Lambda function"
    value       = aws_lambda_function.lambda_web_logic_core.arn
}

output "load_balancer_arn" {
    description = "The ARN of the Network Load Balancer"
    value       = aws_lb_listener.http_listener.arn
}
output "lambda_invoke_arn" {
    description = "The ARN for invoking the Lambda function from API Gateway"
    value       = aws_lambda_function.lambda_web_logic_core.invoke_arn
}