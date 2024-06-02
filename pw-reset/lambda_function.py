import json
import boto3
import os
import base64
from botocore.exceptions import ClientError

PASSWORD_LENGTH = 14


def create_login_profile(user_data):
    def _get_random_password_string(length):
        import secrets
        import string
        pass_chars = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(pass_chars) for _ in range(length))
        return password

    def _send_email(userdata, password):
        ses_client = boto3.client('ses')
        sender_email = 'password_reset@example.com'
        recipient_email = userdata['email']
        subject = 'パスワードリセットが完了しました'
        body_text = '新しいパスワードは以下になります\n'\
                    f'username: {userdata["user"]}\n'\
                    f'password: {password}\n'\
                    '不明点はお問い合わせください'
        try:
            ses_client.send_email(
                Source=recipient_email,
                Destination={
                    'ToAddresses': [sender_email]
                },
                Message={
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': body_text,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )
        except ClientError as e:
            print('[ERROR] send mail failed.')
            raise e

    password = _get_random_password_string(PASSWORD_LENGTH)
    user = user_data.get('user')
    email = user_data.get('email')

    if (not user) or (not email):
        print('[ERROR] username or email is empty.')
        raise

    try:
        iam_client = boto3.client('iam')
        iam_client.get_user(UserName=user)
    except ClientError as e:
        print(f'[ERROR] user: {user} is not exists.')
        raise e

    try:
        iam_client.update_login_profile(
            UserName=user,
            Password=password,
            PasswordResetRequired=True
        )
        _send_email(user_data, password)
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            iam_client.create_login_profile(
                UserName=user,
                Password=password,
                PasswordResetRequired=True
            )
            _send_email(user_data, password)
        else:
            print(e.response)
            raise e


def lambda_handler(event, context):
    api = ApiGatewayV2Authorization(event)
    auth = api.authorizer()
    if auth:
        return auth

    # イベントとコンテキストの内容を出力
    print(f'event: {event}')
    print(f'context: {context}')

    strBody = base64.b64decode(event.get('body')).decode()
    param = json.loads(strBody)
    print('param:', param)
    create_login_profile(param)

    return {
        'statusCode': 200,
        'body': 'login profile update finished'
    }


# https://blog.father.gedow.net/2021/01/21/aws-api-gateway-http-authorizer/
class ApiGatewayV2Authorization():

    event = None

    def __init__(self, event=None):
        if event is not None:
            self.setEvent(event)

    def setEvent(self, event):
        if self.event is not None:
            return
        self.event = event

    def authorizer(self):
        AUTH_KEY   = os.environ['AUTH_KEY']   if os.environ.get('AUTH_KEY')   else "Authorization"
        AUTH_VALUE = os.environ['AUTH_VALUE'] if os.environ.get('AUTH_VALUE') else None

        auth_type = self.event.get("type")
        if auth_type != "REQUEST":
            return None

        header_key   = AUTH_KEY.lower()
        header_value = self.event["headers"].get(header_key)
        if AUTH_VALUE is None or header_value is None:
            return self.responseUnauthorized()

        if AUTH_VALUE != header_value:
            return self.responseUnauthorized()

        return self.responseAuthorized()

    def responseAuthorized(self):
        res = {
            "isAuthorized": True,
            "context": {},
        }
        return res

    def responseUnauthorized(self):
        res = {
            "isAuthorized": False,
            "context": {},
        }
        return res
