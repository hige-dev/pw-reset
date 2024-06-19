data "archive_file" "pw_reset" {
    type = "zip"
    source_dir  = "${path.module}/scripts/pw-reset"
    output_path = "${path.module}/pw-reset.zip"
}

resource "aws_lambda_function" "pw_reset" {
    filename         = "${path.module}/pw-reset.zip"
    function_name    = "pw-reset"
    role             = aws_iam_role.pw_reset.arn
    handler          = "lambda_function.lambda_handler"
    runtime          = "python3.12"
    memory_size      = 128
    timeout          = 30
    source_code_hash = data.archive_file.pw_reset.output_base64sha256
    environment {
        variables = {
            "TZ" = "Asia/Tokyo"
        }
    }
}

resource "aws_lambda_permission" "pw_reset" {
    function_name   = aws_lambda_function.pw_reset.arn
    principal       = "apigateway.amazonaws.com"
    action          = "lambda:InvokeFunction"
    source_arn      = "${aws_apigatewayv2_api.pw_reset.execution_arn}/*/*"
}

resource "aws_cloudwatch_log_group" "pw_reset" {
  name              = "/aws/lambda/pw-reset"
  retention_in_days = 30
}


data "archive_file" "slack_workflow" {
    type = "zip"
    source_dir  = "${path.module}/scripts/slack-workflow"
    output_path = "${path.module}/slack-workflow.zip"
}

resource "aws_lambda_function" "slack_workflow" {
    filename         = "${path.module}/slack-workflow.zip"
    function_name    = "slack-workflow"
    role             = aws_iam_role.slack_workflow.arn
    handler          = "lambda_function.lambda_handler"
    runtime          = "python3.12"
    memory_size      = 128
    timeout          = 30
    source_code_hash = data.archive_file.slack_workflow.output_base64sha256
    environment {
        variables = {
            "AUTH_VALUE" = var.lambda_auth_value,
            "SLACK_WEBHOOK_URL" = var.slack_webhook_url
            "TZ" = "Asia/Tokyo"
        }
    }
}

resource "aws_lambda_permission" "slack_workflow" {
    function_name   = aws_lambda_function.slack_workflow.arn
    principal       = "apigateway.amazonaws.com"
    action          = "lambda:InvokeFunction"
    source_arn      = "${aws_apigatewayv2_api.pw_reset.execution_arn}/*/*"
}

resource "aws_cloudwatch_log_group" "slack_workflow" {
    name              = "/aws/lambda/slack-workflow"
    retention_in_days = 30
}
