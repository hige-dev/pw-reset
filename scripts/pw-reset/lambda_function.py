import json
import base64
import boto3
from urllib.parse import parse_qs
from datetime import datetime, timedelta, timezone
import asyncio


def lambda_handler(event, context):
    try:
        body = parse_body(event)
        print(f'body: {body}')
        print(f'context: {context}')

        params = body.get('params')
        if body.get('action') == 'approve':
            asyncio.run(invoke_pw_reset_exec(params))
            message = create_message(params)
            return {
                'statusCode': 200,
                'body': message
            }
        else:
            raise Exception('rejected')
    except Exception:
        message = create_message(params, False)
        return {
            'statusCode': 200,
            'body': message
        }


def create_message(params, is_approved=True):
    result = "承認" if is_approved else "却下"
    txt = 'パスワードリセット依頼が届きました。承認しますか？\n'\
        '```\n'\
        f'依頼者: {params.get("email")}\n'\
        f'リセット対象ユーザー名: {params.get("user")}\n'\
        f'確認用token: {params.get("gform_token")}\n\n'\
        '※ 事前にメールアドレスに送られたtokenと一致することを必ず確認してください'\
        '```\n'\
        '↓\n'\
        f'<@{params.get('button_pusher')}>により、{params.get('user')}のパスワードリセットが{result}されました'
    return txt


def parse_body(event):
    print('parse body')
    body = json.loads(
        parse_qs(base64.b64decode(event["body"]).decode("utf-8"))["payload"][0]
    )
    result = json.loads(body['actions'][0]['value'])
    result['params']['button_pusher'] = body['user']['id']
    return result


async def invoke_pw_reset_exec(params):
    print('invoke reset exec')
    asyncio.create_task(create_login_profile(params))
    print('asd')


async def create_login_profile(params):
    print('create login profile')
    client = boto3.client('lambda')
    print('after init boto3')
    data = json.dumps({"params": params})
    client.invoke(
        FunctionName='pw-reset-exec',
        InvocationType='Event',
        Payload=data
    )


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
    new_key = f'/{key}/{user}/{now_ymd}'
    return new_key
