resource "aws_apigatewayv2_api" "pw_reset" {
    name          = "pw-reset"
    protocol_type = "HTTP"
    # disable_execute_api_endpoint = true
}

resource "aws_apigatewayv2_route" "pw_reset" {
    api_id = aws_apigatewayv2_api.pw_reset.id
    route_key = "POST /pw-reset"
    target = "integrations/${aws_apigatewayv2_integration.pw_reset.id}"
    authorizer_id = aws_apigatewayv2_authorizer.pw_reset.id
    authorization_type = "CUSTOM"
}

resource "aws_apigatewayv2_integration" "pw_reset" {
    api_id           = aws_apigatewayv2_api.pw_reset.id
    connection_type  = "INTERNET"
    integration_method = "POST"
    integration_uri  = aws_lambda_function.pw_reset.arn
    integration_type = "AWS_PROXY"
    payload_format_version = "2.0"
}

resource "aws_apigatewayv2_authorizer" "pw_reset" {
    api_id = aws_apigatewayv2_api.pw_reset.id
    authorizer_payload_format_version = "2.0"
    enable_simple_responses = true
    authorizer_uri = aws_lambda_function.pw_reset.invoke_arn
    authorizer_type = "REQUEST"
    identity_sources = [
        "$request.header.Authorization"
    ]
    name = "pw-reset-auth"
}

resource "aws_apigatewayv2_stage" "pw_reset" {
    name = "$default"
    stage_variables = {}
    api_id = aws_apigatewayv2_api.pw_reset.id
    # deployment_id = aws_apigatewayv2_deployment.pw_reset.id
    default_route_settings {
        detailed_metrics_enabled = false
        throttling_rate_limit  = 3
        throttling_burst_limit = 3
    }
    auto_deploy = true
    tags = {}
}

resource "aws_apigatewayv2_deployment" "pw_reset" {
    api_id = aws_apigatewayv2_api.pw_reset.id
    description = "Automatic deployment triggered by changes to the Api configuration"
    depends_on = [aws_apigatewayv2_route.pw_reset]
}
