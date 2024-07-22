variable "account_id" {}
variable "region" { default = "ap-northeast-1" }
variable "lambda_auth_value" {}
variable "sns_target" {}
variable "alarm_period" { default = 900 }
variable "alarm_threshold" { default = 100 }
variable "slack_webhook_url" { description = "管理者向けの承認投稿用" }
variable "slack_webhook_for_user_url" { description = "完了後のユーザー通知用" }
variable "valid_domains" { description = "複数ある場合もカンマ区切りの文字列(配列にしない)" }
