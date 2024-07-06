variable "account_id" {}
variable "region" { default = "ap-northeast-1" }
variable "lambda_auth_value" {}
variable "sns_target" {}
variable "alarm_period" { default = 900 }
variable "alarm_threshold" { default = 100 }
variable "slack_webhook_url" {}
variable "valid_domains" { description = "複数ある場合もカンマ区切りの文字列(配列にしない)" }
