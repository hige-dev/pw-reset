import os
import base64
import json
import urllib.request
import boto3
import authorization


def lambda_handler(event, context):
    api = authorization.ApiGatewayV2Authorization(event)
    auth = api.authorizer()
    if auth:
        return auth

    # GoogleFormからデータを取り出し
    strBody = base64.b64decode(event.get('body')).decode()
    params = json.loads(strBody)

    user = params.get('user')
    KEY = f'/PW_RESET_TOKEN_FOR_LAMBDA/{user}'
    ssm = SsmParameter()
    email = params.get('email')
    try:
        check_mail_domain(email)
    except Exception:
        message = f'{email}は許可されたメールドメインではありません'
        post_slack(message)
        ssm.delete_parameter(user)
        return

    # tokenをParameterStoreに保存
    # ex) KEY: /PW_RESET_TOKEN_FOR_LAMBDA/{username}/20240101
    params['token_for_pw_reset'] = ssm.save_token_to_parameter_store(KEY)
    print(params)

    # slackに承認可否を投稿
    message = create_post_message(params)
    post_slack(message)


def post_slack(message):
    webhook_url = os.environ['SLACK_WEBHOOK_URL']
    request_post = urllib.request.Request(
        webhook_url,
        data=json.dumps(message).encode(),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(request_post) as resp:
        resp.read().decode()


def check_mail_domain(email):
    valid_domains = os.getenv('VALID_DOMAINS')
    if email.split('@')[-1] not in valid_domains:
        raise Exception('invalid email')


def generate_token_for_pw_reset(length=20):
    import string
    import random
    import secrets
    # パスワードの最低要件を定義
    if length < 8:
        raise ValueError("Password length should be at least 8 characters.")
    # アルファベット、数字、特殊文字の定義
    alphabet_lower = string.ascii_lowercase
    alphabet_upper = string.ascii_uppercase
    digits = string.digits
    special_chars = '!#$%*+,-./:;=?@^_|~'
    # 全てのキャラクターセットを一つにまとめる
    all_chars = alphabet_lower + alphabet_upper + digits + special_chars
    # 必ず含めるべき文字をリスト化
    password = [
        secrets.choice(alphabet_lower),
        secrets.choice(alphabet_upper),
        secrets.choice(digits),
        secrets.choice(special_chars),
    ]
    # 残りの文字を追加
    password += [secrets.choice(all_chars) for _ in range(length - 4)]
    # パスワードの文字をランダムにシャッフル
    random.shuffle(password)
    # リストを文字列に変換して返す
    return ''.join(password)


def create_post_message(params):
    txt = 'パスワードリセット依頼が届きました。承認しますか？\n'\
          '```\n'\
          f'依頼者: {params.get("email")}\n'\
          f'リセット対象ユーザー名: {params.get("user")}\n'\
          f'確認用token: {params.get("gform_token")}\n\n'\
          '※ 事前にメールアドレスに送られたtokenと一致することを必ず確認してください'\
          '```'
    return {
        "text": txt,
        "attachments": [
            {
                "text": "承認または拒否を選択してください",
                "fallback": "You are unable to choose",
                "callback_id": "approval_request",
                "color": "#3AA3E3",
                "attachment_type": "default",
                "actions": [
                    {
                        "name": "approve",
                        "text": "承認",
                        "type": "button",
                        "value": json.dumps({
                            "action": "approve",
                            "params": params
                        })
                    },
                    {
                        "name": "reject",
                        "text": "拒否",
                        "type": "button",
                        "value": json.dumps({
                            "action": "reject",
                            "params": params
                        })
                    }
                ]
            }
        ]
    }


class SsmParameter:
    def __init__(self):
        self.client = boto3.client('ssm')

    def save_token_to_parameter_store(self, param_key):
        token = generate_token_for_pw_reset()
        self.client.put_parameter(
            Name=param_key,
            Value=token,
            Type='SecureString',
            Overwrite=True,
        )
        return token
