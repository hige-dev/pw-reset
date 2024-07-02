import json
import base64
import boto3
from urllib.parse import parse_qs
from datetime import datetime, timedelta, timezone
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    try:
        body = parse_body(event)
        print(f'body: {body}')
        print(f'context: {context}')

        params = body.get('params')
        user = params.get('user')
        if body.get('action') == 'approve':
            if is_valid_token(params.get('token'), user):
                create_login_profile(user)
                delete_parameter(user)
            else:
                raise Exception('invalid token')
    except Exception as e:
        delete_parameter(user)
        raise e


def parse_body(event):
    body = json.loads(
            parse_qs(base64.b64decode(event["body"]).decode("utf-8"))["payload"][0]
    )
    # 承認または拒否のアクションを取得
    return json.loads(body['actions'][0]['value'])


def is_valid_token(response_token, user):
    KEY = generate_key("PW_RESET_TOKEN_FOR_LAMBDA", user)
    ssm = SsmParameter()
    registered_token = ssm.get_parameter(KEY)
    check_token = (response_token == registered_token)
    return check_token


def create_login_profile(user):
    for_passwd = True
    now_ymd_h = now_str(for_passwd)

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


def delete_parameter(user):
    ssm = SsmParameter()
    KEY = generate_key("PW_RESET_TOKEN_FOR_LAMBDA", user)
    ssm.delete_parameter(KEY)


def now_str(for_passwd=False):
    JST = timezone(timedelta(hours=+9), 'JST')
    now = datetime.now(JST)
    if for_passwd:
        # 一時パスワード用。1時間に1回は更新できるようにする
        now_string = now.strftime('%Y%m%d%H')
    else:
        # ParameterStore用。フォーム送信と承認で時間まで揃えるのは難しそうなので、同日なら許容
        now_string = now.strftime('%Y%m%d')
    return now_string


def generate_key(key, user):
    now_ymd = now_str()
    new_key = f'{key}-{now_ymd}-{user}'
    return new_key


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
