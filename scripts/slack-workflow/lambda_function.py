import os
import base64
import json
import urllib.request
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta, timezone
import authorization


def lambda_handler(event, context):
    try:
        api = authorization.ApiGatewayV2Authorization(event)
        auth = api.authorizer()
        if auth:
            return auth

        ssm = SsmParameter()

        webhook_url = os.environ['SLACK_WEBHOOK_URL']

        strBody = base64.b64decode(event.get('body')).decode()
        params = json.loads(strBody)

        # ex) KEY: PW_RESET_TOKEN_FOR_LAMBDA-20240101-{username}
        KEY = make_key_unique("PW_RESET_TOKEN_FOR_LAMBDA", params.get('user'))
        params['token'] = ssm.save_token_to_parameter_store(KEY)
        print(params)
        txt = 'パスワードリセット依頼が届きました。承認しますか？\n'\
              '```\n'\
              f'依頼者: {params.get("email")}\n'\
              f'リセット対象ユーザー名: {params.get("user")}\n'\
              '```'
        message = {
            "text": txt,
            "attachments": [
                {
                    "text": "承認または拒否を選択してください。\n※処理時間の関係上、「何らかのエラーが発生しました。もう一度お試しください。」と表示されますが問題ありません",
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
                                "params": ""
                            })
                        }
                    ]
                }
            ]
        }
        request_post = urllib.request.Request(
            webhook_url,
            data=json.dumps(message).encode(),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(request_post) as resp:
            body = resp.read().decode()
        print('slack response: ', body)
    except ClientError as e:
        print('あばばば')
        raise e


def make_key_unique(key, user):
    JST = timezone(timedelta(hours=+9), 'JST')
    now = datetime.now(JST)
    now_ymd = now.strftime('%Y%m%d')
    new_key = f'{key}-{now_ymd}-{user}'
    return new_key


def generate_secure_password(length=20):
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
    special_chars = '!#$%&()*+,-./:;=?@^_`{|}~'
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


class SsmParameter:
    def __init__(self):
        self.client = boto3.client('ssm')

    def get_parameter(self, param_key):
        response = self.client.get_parameter(
            Name=param_key,
            WithDecryption=True
        )
        return response['Parameter']['Value']

    def delete_parameter(self, param_key):
        self.client.delete_parameter(Name=param_key)

    def save_token_to_parameter_store(self, param_key):
        token = generate_secure_password()
        self.client.put_parameter(
            Name=param_key,
            Value=token,
            Type='SecureString',
            Overwrite=False,
        )
        return token
