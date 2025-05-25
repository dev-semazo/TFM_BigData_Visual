resource "aws_apigatewayv2_api" "http_api" {
    name          = "${var.project_name}api"
    protocol_type = "HTTP"
    target = var.lambda_arn
}

resource "aws_apigatewayv2_vpc_link" "vpc_link_lambda" {
    name        = "${var.project_name}-vpc-link"
    security_group_ids = [var.security_group_id]
    subnet_ids  = [var.subnet_id] # Subredes donde se ejecuta la Lambda
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
    api_id                 = aws_apigatewayv2_api.http_api.id
    integration_type       = "VPC_LINK" # Usar VPC Link para Lambda
    connection_type        = "VPC_LINK"
    connection_id          = aws_apigatewayv2_api.vpc_link_lambda.id
    integration_uri        = var.lambda_arn
    integration_method     = "POST"
    payload_format_version = "2.0"
    timeout_milliseconds   = 29000 # Máximo 29 segundos para HTTP APIs
    depends_on = [aws_apigatewayv2_vpc_link.vpc_link_lambda]
}

resource "aws_apigatewayv2_authorizer" "cognito_authorizer_v2" {
  api_id           = aws_apigatewayv2_api.http_api.id
  name             = "${var.project_name}-cognito-authorizer"
  authorizer_type  = "JWT"
  identity_sources = ["$request.header.Authorization"] 

  # Configuración del proveedor JWT
  jwt_configuration {
    audience = ["${var.cognito_user_pool_id}"] 
    issuer   = "https://cognito-idp.${var.aws_region}.amazonaws.com/${var.cognito_user_pool_id}"
  }
}

resource "aws_apigatewayv2_route" "post_data_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /data" # Combina método HTTP y path
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
  authorizer_id = aws_apigatewayv2_authorizer.cognito_authorizer_v2.id
  authorization_type = "JWT" # Usa el tipo JWT para el autorizador Cognito
}

resource "aws_apigatewayv2_stage" "api_stage_v2" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "prod"
  auto_deploy = true # Despliega automáticamente los cambios en las rutas/integraciones
}

resource "aws_lambda_permission" "allow_apigatewayv2_to_invoke_lambda" {
  statement_id  = "AllowAPIGatewayV2Invoke"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*"
}
