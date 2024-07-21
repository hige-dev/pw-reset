data "archive_file" "pw_reset" {
    type = "zip"
    source_dir  = "${path.module}/scripts/pw-reset"
    output_path = "/tmp/pw-reset.zip"
}

resource "aws_lambda_function" "pw_reset" {
    filename         = "/tmp/pw-reset.zip"
    function_name    = "pw-reset"
    role             = aws_iam_role.pw_reset.arn
    handler          = "lambda_function.lambda_handler"
    runtime          = "python3.12"
    memory_size      = 256
    timeout          = 30
    source_code_hash = data.archive_file.pw_reset.output_base64sha256
    environment {
        variables = {
            "TZ" = "Asia/Tokyo"
        }
    }
}

resource "aws_lambda_permission" "pw_reset" {
    function_name   = aws_lambda_function.pw_reset.function_name
    principal       = "apigateway.amazonaws.com"
    action          = "lambda:InvokeFunction"
    source_arn      = "${aws_apigatewayv2_api.pw_reset.execution_arn}/*/*"
}

resource "aws_cloudwatch_log_group" "pw_reset" {
  name              = "/aws/lambda/pw-reset"
  retention_in_days = 30
}

resource "aws_lambda_function_event_invoke_config" "pw_reset" {
  function_name                = aws_lambda_function.pw_reset.function_name
  maximum_event_age_in_seconds = 60
  maximum_retry_attempts       = 0
}

data "archive_file" "pw_reset_exec" {
    type = "zip"
    source_dir  = "${path.module}/scripts/pw-reset-exec"
    output_path = "/tmp/pw-reset-exec.zip"
}

resource "aws_lambda_function" "pw_reset_exec" {
    filename         = "/tmp/pw-reset-exec.zip"
    function_name    = "pw-reset-exec"
    role             = aws_iam_role.pw_reset.arn
    handler          = "lambda_function.lambda_handler"
    runtime          = "python3.12"
    memory_size      = 128
    timeout          = 30
    source_code_hash = data.archive_file.pw_reset_exec.output_base64sha256
    environment {
        variables = {
            "TZ" = "Asia/Tokyo"
            "SLACK_WEBHOOK_URL" = var.slack_webhook_url
        }
    }
}

resource "aws_lambda_permission" "pw_reset_exec" {
    function_name   = aws_lambda_function.pw_reset_exec.function_name
    principal       = "lambda.amazonaws.com"
    action          = "lambda:InvokeFunction"
    source_arn      = aws_lambda_function.pw_reset.arn
}

resource "aws_cloudwatch_log_group" "pw_reset_exec" {
  name              = "/aws/lambda/pw-reset-exec"
  retention_in_days = 30
}

resource "aws_lambda_function_event_invoke_config" "pw_reset_exec" {
  function_name                = aws_lambda_function.pw_reset_exec.function_name
  maximum_event_age_in_seconds = 60
  maximum_retry_attempts       = 0
}

data "archive_file" "slack_workflow" {
    type = "zip"
    source_dir  = "${path.module}/scripts/slack-workflow"
    output_path = "/tmp/slack-workflow.zip"
}

resource "aws_lambda_function" "slack_workflow" {
    filename         = "/tmp/slack-workflow.zip"
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
            "VALID_DOMAINS" = var.valid_domains
        }
    }
}

resource "aws_lambda_permission" "slack_workflow" {
    function_name   = aws_lambda_function.slack_workflow.function_name
    principal       = "apigateway.amazonaws.com"
    action          = "lambda:InvokeFunction"
    source_arn      = "${aws_apigatewayv2_api.pw_reset.execution_arn}/*/*"
}

resource "aws_cloudwatch_log_group" "slack_workflow" {
    name              = "/aws/lambda/slack-workflow"
    retention_in_days = 30
}

resource "aws_lambda_function_event_invoke_config" "slack_workflow" {
  function_name                = aws_lambda_function.slack_workflow.function_name
  maximum_event_age_in_seconds = 60
  maximum_retry_attempts       = 0
}

data "archive_file" "close_apigw" {
    type = "zip"
    source_dir  = "${path.module}/scripts/close-apigw"
    output_path = "/tmp/close-apigw.zip"
}

resource "aws_lambda_function" "close_apigw" {
    filename         = "/tmp/close-apigw.zip"
    function_name    = "close-apigw"
    role             = aws_iam_role.close_apigw.arn
    handler          = "lambda_function.lambda_handler"
    runtime          = "python3.12"
    memory_size      = 128
    timeout          = 30
    source_code_hash = data.archive_file.close_apigw.output_base64sha256
    environment {
        variables = {
            "TZ" = "Asia/Tokyo"
            "SLACK_WEBHOOK_URL" = var.slack_webhook_url
            "API_ID" = aws_apigatewayv2_api.pw_reset.id
        }
    }
}

resource "aws_lambda_permission" "close_apigw" {
    function_name   = aws_lambda_function.close_apigw.function_name
    principal       = "lambda.alarms.cloudwatch.amazonaws.com"
    action          = "lambda:InvokeFunction"
    source_arn      = aws_cloudwatch_metric_alarm.pw_reset.arn
}

resource "aws_cloudwatch_log_group" "close_apigw" {
  name              = "/aws/lambda/close-apigw"
  retention_in_days = 30
}

resource "aws_lambda_function_event_invoke_config" "close_apigw" {
  function_name                = aws_lambda_function.close_apigw.function_name
  maximum_event_age_in_seconds = 60
  maximum_retry_attempts       = 0
}
