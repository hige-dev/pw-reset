resource "aws_cloudwatch_metric_alarm" "pw_reset" {
    alarm_name          = "API_GW_DDoS_Alarm"
    alarm_description   = "API Gateway received ${var.alarm_threshold} requests in ${var.alarm_period} seconds, possible DDoS."
    actions_enabled     = true
    alarm_actions       = [
                              aws_sns_topic.pw_reset.arn
                          ]
    metric_name         = "Count"
    namespace           = "AWS/ApiGateway"
    statistic           = "Sum"
    dimensions          = {}
    period              = var.alarm_period
    evaluation_periods  = 1
    datapoints_to_alarm = 1
    threshold           = var.alarm_threshold
    comparison_operator = "GreaterThanOrEqualToThreshold"
    treat_missing_data  = "missing"
    depends_on          = [aws_sns_topic.pw_reset]
}
