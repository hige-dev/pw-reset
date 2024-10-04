## 概要

![](./flow.drawio.svg)

GoogleフォームにユーザーIDを入力して送信すると、API Gatewayが受け取ってLambdaを実行する<br>
Lambdaでは、対象ユーザーのパスワードをリセットする

## 事前準備
1. tfstateを保存するバケットを作成
2. slackのwebhook作成
3. terraform実行用の環境変数を設定

```
cat <<EOS > terraform.tfvars
account_id = {AWSのアカウントID}
lambda_auth_value = "{任意の値。API Gatewayの認証用}"
sns_target = "{アラーム検知時の通知先。メールアドレス}"
slack_webhook_url = "{パスワード変更可否を送る管理者向けチャンネルwebhook}"
slack_webhook_for_user_url = "{パスワード完了を通知する、依頼者が所属するチャンネルwebhook}"
valid_domains = "{許可するメールドメイン。外部からのリクエスト拒否用}"
# 以下は変えたい場合のみ。デフォルトは900秒に100回API GatewayにリクエストがあればDDoSと判断
# alarm_period = "{デフォルト900秒。アラーム計測間隔}"
# alarm_threshold = "{デフォルト100。API Gatewayリクエスト数のアラーム閾値}"
EOS
```

## slack webhook設定
1. 「Incoming Webhooks」で、以下の2つのwebhookを作成する
  - パスワードリセットの承認可否をチャンネルに投稿するためのwebhook
  - パスワードリセットが完了したことを依頼者に通知するためのwebhook
2. 「Interactivity & Shortcuts」で、承認ボタンが押された際にリクエストを投げるAPI GWのendpointを設定する
  - ex) Request URL: https://{api_id}.execute-api.ap-northeast-1.amazonaws.com/pw-reset

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
2. scripts/GAS以下のスクリプトを、Googleフォームのスクリプトに設定。
  - フォームの項目名は「ユーザー名」
3. GASの「スクリプト プロパティ」に以下を設定
  - API_ENDPOINT: 以下参照
  - AUTH_VALUE: Lambda認証用。slack-workflowの環境変数で設定
  - ADMIN_EMAILs: 管理者に送信するメール(通知A用)

```
# API_ENDPOINTには、以下の「api_endpoint」を入力

$ terraform state show aws_apigatewayv2_api.pw_reset | grep '^\s*api_endpoint'
    api_endpoint                 = "https://{api_id}.execute-api.ap-northeast-1.amazonaws.com"
```

## シーケンス図
```mermaid
sequenceDiagram
  actor line_2 as 依頼者
  participant line_1 as Google Form
  participant line_3 as API Gateway
  participant line_5 as Lambda
  participant line_4 as S3署名付URL
  participant line_6 as Slack
  actor line_7 as 管理者
  participant line_11 as Parameter Store
  participant line_10 as IAM
  line_2 ->> line_1: リセット対象ID入力
  line_1 ->> line_3: POST /gen-url
  line_3 ->> line_5: Lambda認証
  line_5 ->> line_3: response
  line_3 ->> line_5: URL発行依頼
  line_5 ->> line_4: URL発行
  line_4 ->> line_3: URL返却
  line_3 ->> line_1: URL返却
  line_1 ->> line_2: URLメール送信
  line_1 ->> line_7: 通知A<br>（依頼者email, リセット対象ID, ランダム文字列）
  line_2 ->> line_4: URLクリック・フォーム送信
  line_4 ->> line_2: htmlフォーム返却
  line_2 ->> line_3: フォーム送信<br>POST /slack-workflow
  line_3 ->> line_5: slack-workflow実行
  line_5 ->> line_11: token発行・保存
  line_5 ->> line_6: 承認可否投稿
  line_6 ->> line_7: 通知B
  line_7 ->> line_6: 通知Aと内容が同じことを確認し<br>承認 or 否認
  line_6 ->> line_3: POST /pw-reset
  line_3 ->> line_5: pw-reset実行
  line_5 ->> line_5: 承認チェック
  line_5 ->> line_11: token検証
  line_5 ->> line_10: パスワードリセット
  line_5 ->> line_11: token削除
  line_5 ->> line_6: 処理完了通知
  line_6 ->> line_2: 通知
  line_2 ->> line_10: 一時パスワードでログインしパスワード変更
```
