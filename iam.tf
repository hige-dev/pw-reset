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
