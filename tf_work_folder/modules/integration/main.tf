resource "aws_apigatewayv2_api" "http_api" {
    name          = "${var.project_name}api"
    protocol_type = "HTTP"
    target = var.lambda_arn
}

resource "aws_apigatewayv2_vpc_link" "vpc_link_lambda" {
    name        = "${var.project_name}-vpc-link"
    security_group_ids = []
    subnet_ids  = var.subnet_id 
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
    api_id                 = aws_apigatewayv2_api.http_api.id
    integration_type       = "HTTP_PROXY" # Usar VPC Link para Lambda
    connection_type        = "VPC_LINK"
    connection_id          = aws_apigatewayv2_vpc_link.vpc_link_lambda.id
    integration_uri        = var.arn_alb_listener
    integration_method     = "GET"
    payload_format_version = "1.0"
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
    audience = ["27i9jfal404bkhcjdjn10gijsh"] 
    issuer   = "https://cognito-idp.${var.aws_region}.amazonaws.com/${var.cognito_user_pool_id}"
  }
}

resource "aws_apigatewayv2_route" "post_data_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /data" # Combina método HTTP y path
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
  authorizer_id = aws_apigatewayv2_authorizer.cognito_authorizer_v2.id
  authorization_type = "JWT" # Usa el tipo JWT para el autorizador Cognito
}

resource "aws_apigatewayv2_stage" "api_stage_v2" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "prod"
  auto_deploy = true # Despliega automáticamente los cambios en las rutas/integraciones
}

