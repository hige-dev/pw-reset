import json
import boto3
import os
import base64
from datetime import datetime, timedelta, timezone
from botocore.exceptions import ClientError


def create_login_profile(user):
    JST = timezone(timedelta(hours=+9), 'JST')
    now = datetime.now(JST)
    now_ymd_h = now.strftime('%Y%m%d%H')
    iam_client = boto3.client('iam')
    print(now_ymd_h)
    try:
        iam_client.get_user(UserName=user)
    except ClientError as e:
        print(f'[ERROR] user: {user} is not exists.')
        raise e

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
    params = json.loads(strBody)
    print('param:', params)
    create_login_profile(params.get('user'))

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
