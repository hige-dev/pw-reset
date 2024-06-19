import json
import base64
import boto3
from urllib.parse import parse_qs
from datetime import datetime, timedelta, timezone
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    # Slackからのリクエストデータをパース
    body = json.loads(
            parse_qs(base64.b64decode(event["body"]).decode("utf-8"))["payload"][0]
    )
    # 承認または拒否のアクションを取得
    result = json.loads(body['actions'][0]['value'])
    print('body:', body)
    if result.get('action') == 'approve':
        params = result.get('params')
        KEY = check_key("PW_RESET_TOKEN_FOR_LAMBDA", params.get('user'))
        ssm = SsmParameter()
        token = ssm.get_parameter(KEY)
        # イベントとコンテキストの内容を出力
        if params.get('token') == token:
            resp = create_login_profile(params.get('user'))
            ssm.delete_parameter(KEY)
            return resp
        else:
            ssm.delete_parameter(KEY)
            return {
                'statuscode': 200,
                'body': '不正なトークンです'
            }
    else:
        # 拒否の場合
        ssm = SsmParameter()
        KEY = "PW_RESET_TOKEN_FOR_LAMBDA"
        ssm.delete_parameter(KEY)
        return {
            'statusCode': 200,
            'body': 'リクエストが拒否されました'
        }


def check_key(key, user):
    JST = timezone(timedelta(hours=+9), 'JST')
    now = datetime.now(JST)
    now_ymd = now.strftime('%Y%m%d')
    new_key = f'{key}-{now_ymd}-{user}'
    return new_key


def create_login_profile(user):
    JST = timezone(timedelta(hours=+9), 'JST')
    now = datetime.now(JST)
    now_ymd_h = now.strftime('%Y%m%d%H')
    iam_client = boto3.client('iam')
    try:
        iam_client.get_user(UserName=user)
    except ClientError:
        print(f'[ERROR] user: {user} is not exists.')
        return {
            'statusCode': 200,
            'body': 'ユーザーが見つかりませんでした'
        }
    try:
        iam_client.update_login_profile(
            UserName=user,
            Password=f'U{user}_{now_ymd_h}',
            PasswordResetRequired=True
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            iam_client.create_login_profile(
                UserName=user,
                Password=f'U{user}_{now_ymd_h}',
                PasswordResetRequired=True
            )
        else:
            print(e.response)
            return {
                'statusCode': 200,
                'body': 'エラーが発生しました。/aws/lambda/pw-resetのログを確認してください'
            }


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
