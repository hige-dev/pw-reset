resource "aws_iam_policy" "pw_reset" {
    name = "pw_reset_policy"
    policy = <<-EOS
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "ManagedByTerraform",
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "iam:UpdateLoginProfile",
                    "iam:CreateLoginProfile",
                    "iam:GetLoginProfile",
                    "iam:GetUser"
                ],
                "Resource": [
                    "arn:aws:iam::${var.account_id}:user/*",
                    "arn:aws:logs:*:${var.account_id}:log-group:${aws_cloudwatch_log_group.pw_reset.name}",
                    "arn:aws:logs:*:${var.account_id}:log-group:${aws_cloudwatch_log_group.pw_reset.name}:log-stream:*"
                ]
            }
        ]
    }
    EOS
}

resource "aws_iam_role" "pw_reset" {
    path = "/"
    # name = "pw_reset_role"
    name = "pw_reset_role"
    assume_role_policy = <<-EOS
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    EOS
    max_session_duration = 3600
    tags = {}
}

resource "aws_iam_role_policy_attachment" "pw_reset" {
    role = aws_iam_role.pw_reset.name
    policy_arn = aws_iam_policy.pw_reset.arn
}

resource "aws_iam_policy" "parameter_store_for_pw_reset" {
    name = "parameter_store_for_pw-reset"
    policy = <<-EOS
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "VisualEditor0",
                "Effect": "Allow",
                "Action": [
                    "ssm:PutParameter",
                    "ssm:DeleteParameter",
                    "ssm:GetParameter"
                ],
                "Resource": "arn:aws:ssm:${var.region}:${var.account_id}:parameter/PW_RESET_TOKEN_FOR_LAMBDA*"
            }
        ]
    }
    EOS
}

resource "aws_iam_role_policy_attachment" "parameter_store_for_pw_reset" {
    role = aws_iam_role.pw_reset.name
    policy_arn = aws_iam_policy.parameter_store_for_pw_reset.arn
}

resource "aws_iam_policy" "slack_workflow" {
    name = "slack_workflow"
    policy = <<-EOS
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "logs:CreateLogGroup",
                "Resource": "arn:aws:logs:ap-northeast-1:${var.account_id}:log-group:${aws_cloudwatch_log_group.slack_workflow.name}"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": [
                    "arn:aws:logs:ap-northeast-1:${var.account_id}:log-group:${aws_cloudwatch_log_group.slack_workflow.name}:*"
                ]
            }
        ]
    }
    EOS
}

resource "aws_iam_role" "slack_workflow" {
    path = "/"
    name = "slack_workflow"
    assume_role_policy = <<-EOS
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    EOS
    max_session_duration = 3600
    tags = {}
}

resource "aws_iam_role_policy_attachment" "slack_workflow" {
    role = aws_iam_role.slack_workflow.name
    policy_arn = aws_iam_policy.slack_workflow.arn
}

resource "aws_iam_role_policy_attachment" "parameter_store_for_slack_workflow" {
    role = aws_iam_role.slack_workflow.name
    policy_arn = aws_iam_policy.parameter_store_for_pw_reset.arn
}
