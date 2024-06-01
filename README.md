## 概要

![](./flow.drawio.svg)

GoogleフォームにユーザーIDを入力して送信すると、API Gatewayが受け取ってLambdaを実行する<br>
Lambdaでは、対象ユーザーのパスワードをリセットし、一時パスワードを発行する

共通一次パスワード：`"U{ユーザー名}_{date +%Y%m%d%H}"`
ex) "Uhoge_2024010113"

### 注意点
- 先頭は大文字の`U`。パスワードに大文字・小文字のルールがある場合の対応
- 過去のパスワードを使いまわしできない場合、デフォルトでは1時間に1回しか更新できない。かも
  - 動的なパスワードを利用者側で把握するための苦肉の策。分まで設定したらシビアかな、と

## 事前準備
1. tfstateを保存するバケットを作成
2. terraform実行用の環境変数を設定

```
cat <<EOS > terraform.tfvars
account_id = {AWSのアカウントID}
lambda_auth_value = "{任意の値。API Gatewayの認証用}"
sns_target = "{アラーム検知時の通知先。メールアドレス}"
# 以下は変えたい場合のみ。デフォルトは900秒に100回API GatewayにリクエストがあればDDoSと判断
# alarm_period = "{デフォルト900秒。アラーム計測間隔}"
# alarm_threshold = "{デフォルト100。API Gatewayリクエスト数のアラーム閾値}"
EOS
```

## terraform実行

```
export AWS_PROFILE={もろもろ作成権限のあるPROFILE}

# 初期設定
terraform init -backend-config="bucket={作成したバケット名}"

# dry run
terraform plan

# execute
terraform apply
```


## Googleフォーム実行前作業
1. terraform実行後、アラート通知先のsns_targetにメールが届くので承認
2. GAS/pw-reset.gsをフォームのスクリプトに設定。フォームの項目名は「ユーザー名」
3. GASの「スクリプト プロパティ」にAPI_ENDPOINTとAUTH_VALUEを設定

```
# API_ENDPOINTには、以下の「api_endpoint」を入力
terraform state show aws_apigatewayv2_api.pw_reset

# ex)
# resource "aws_apigatewayv2_api" "pw_reset" {
#     api_endpoint                 = {ここの値}
#     api_key_selection_expression = ...
#     arn                          = ...
#     description                  = ...
#     disable_execute_api_endpoint = ...
#     execution_arn                = ...
#     id                           = ...
#     name                         = ...
#     protocol_type                = ...
#     route_selection_expression   = ...
#     tags                         = ...
#     tags_all                     = ...
#     version                      = ...
# }
