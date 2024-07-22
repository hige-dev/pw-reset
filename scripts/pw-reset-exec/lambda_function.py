import boto3
import json
import os
import urllib.request
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    print(event)
    params = event.get('params')
    user = params.get('user')
    key = f'/PW_RESET_TOKEN_FOR_LAMBDA/{user}'
    if is_valid_token(params.get('token_for_pw_reset'), key):
        create_login_profile(params)
    else:
        message = f'[ERROR] 不正なtokenです(token: `{params.get("gform_token")}`)'
        post_slack(message)
    delete_parameter(key)


def create_login_profile(params):
    user = params.get('user')
    token = params.get('gform_token')
    password = params.get('tmp_password')
    iam_client = boto3.client('iam')
    try:
        iam_client.get_user(UserName=user)
    except ClientError:
        print(f'[ERROR] user: {user} is not exists.')
        message = f'[ERROR] ユーザー: {user} が見つかりませんでした(token: `{token}`)'
        post_slack(message)
        return
    try:
        iam_client.update_login_profile(
            UserName=user,
            Password=password,
            PasswordResetRequired=True
        )
        message = f'[INFO] {user}のパスワードリセットが完了しました。メールに送信されたパスワードでログインしてください'
        for_admin = False
        post_slack(message, for_admin)
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            iam_client.create_login_profile(
                UserName=user,
                Password=password,
                PasswordResetRequired=True
            )
            message = f'[INFO] {user}のパスワードリセットが完了しました。メールに送信されたパスワードでログインしてください'
            for_admin = False
            post_slack(message, for_admin)
        else:
            print(e.response)
            message = f'[ERROR] {e.response['Error']['Code']} が発生しました。' \
                      f'/aws/lambda/pw-resetのログを確認してください(token: `{token}`)'
            post_slack(message)


def post_slack(message, for_admin=True):
    message = {
        'text': message
    }
    webhook_url = os.environ['SLACK_WEBHOOK_URL'] if for_admin else os.environ['SLACK_WEBHOOK_FOR_USER_URL']
    request_post = urllib.request.Request(
        webhook_url,
        data=json.dumps(message).encode(),
        headers={'content-type': 'application/json'}
    )
    with urllib.request.urlopen(request_post) as resp:
        resp.read().decode()


def delete_parameter(key):
    ssm = SsmParameter()
    ssm.delete_parameter(key)


def is_valid_token(incoming_token, key):
    ssm = SsmParameter()
    registered_token = ssm.get_parameter(key)
    check_token = (incoming_token == registered_token)
    print(f'[INFO] incoming: {incoming_token}')
    print(f'[INFO] registerd: {registered_token}')
    print(f'[INFO] check token result: {check_token}')
    return check_token


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
