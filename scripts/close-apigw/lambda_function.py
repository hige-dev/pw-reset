import boto3
import os
import urllib.request
import json


def lambda_handler(event, context):
    api_id = os.environ['API_ID']
    client = boto3.client('apigatewayv2')
    client.update_api(
        ApiId=api_id,
        DisableExecuteApiEndpoint=True
    )
    post_slack('異常なアクセスがあったため、API Gatewayのエンドポイントを閉じました')


def post_slack(message):
    message = {
        'text': message
    }
    webhook_url = os.environ['SLACK_WEBHOOK_URL']
    request_post = urllib.request.Request(
        webhook_url,
        data=json.dumps(message).encode(),
        headers={'content-type': 'application/json'}
    )
    with urllib.request.urlopen(request_post) as resp:
        resp.read().decode()
