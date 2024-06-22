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
slack_webhook_url = "{パスワード変更可否を送る管理者向けチャンネル}"
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

$ terraform state show aws_apigatewayv2_api.pw_reset | grep '^\s*api_endpoint'
    api_endpoint                 = "https://{api_id}.execute-api.ap-northeast-1.amazonaws.com"
```

## [WIP] slack webhook設定
パスワードリセットの承認可否をチャンネルに投稿するためのwebhookを作る

ボタンが押された際にリクエストを投げるAPI GWのendpointの設定も必要

## シーケンス図
```mermaid
sequenceDiagram
  autonumber
  actor line_2 as 依頼者
  participant line_1 as form
  participant line_3 as API Gateway
  participant line_4 as S3署名付URL
  participant line_5 as Lambda
  participant line_6 as Slack
  actor line_7 as admin
  participant line_10 as IAM
  participant line_11 as Parameter Store
  line_2 ->> line_1: 入力
  line_1 ->> line_2: URLをメールで送信
  line_1 ->> line_6: CC: Slack
  line_6 ->> line_7: 通知
  line_2 ->> line_3: GET /gen-url
  line_3 ->> line_4: URL発行リクエスト
  line_4 ->> line_2: URL返す
  line_2 ->> line_4: リダイレクト
  line_2 ->> line_4: フォーム送信
  line_4 ->> line_3: POST /slack-workflow
  line_3 ->> line_5: slack-workflow実行
  line_5 ->> line_11: token保存
  line_5 ->> line_6: 承認可否投稿
  line_6 ->> line_7: 通知
  line_7 ->> line_6: 承認 or 否認
  line_6 ->> line_3: POST /pw-reset
  line_3 ->> line_5: pw-reset実行
  line_5 ->> line_11: token検証
  line_5 ->> line_10: 承認の場合のみ<br>パスワードリセット
  line_5 ->> line_11: token削除
  line_2 ->> line_10: 固定一時パスワードでログインしパスワード変更
```
