resource "aws_sns_topic" "pw_reset" {
    display_name = ""
    name         = "API_GW_DDoS_Alarm"
}

resource "aws_sns_topic_policy" "pw_reset" {
    policy = <<-EOS
    {
        "Version": "2008-10-17",
        "Id": "__default_policy_ID",
        "Statement": [
            {
                "Sid": "__default_statement_ID",
                "Effect": "Allow",
                "Principal": {
                    "AWS": "*"
                },
                "Action": [
                    "SNS:GetTopicAttributes",
                    "SNS:SetTopicAttributes",
                    "SNS:AddPermission",
                    "SNS:RemovePermission",
                    "SNS:DeleteTopic",
                    "SNS:Subscribe",
                    "SNS:ListSubscriptionsByTopic",
                    "SNS:Publish"
                ],
                "Resource": "${aws_sns_topic.pw_reset.arn}",
                "Condition": {
                    "StringEquals": {
                        "AWS:SourceOwner": "${var.account_id}"
                    }
                }
            }
        ]
    }
    EOS
    arn        = aws_sns_topic.pw_reset.arn
    depends_on = [aws_sns_topic.pw_reset]
}

resource "aws_sns_topic_subscription" "pw_reset" {
    topic_arn                       = aws_sns_topic.pw_reset.arn
    endpoint                        = var.sns_target
    protocol                        = "email"
    confirmation_timeout_in_minutes = 1
    endpoint_auto_confirms          = false
    depends_on                      = [aws_sns_topic.pw_reset]
}
