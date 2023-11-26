import boto3
from datetime import datetime, timezone, timedelta
from os import getenv
import re


def template(event, context):
    sqs = boto3.client('sqs')
    queue_env_name = ""
    queue_url = getenv(queue_env_name)

    query_string_parameters = event.get("queryStringParameters") or {}
    headers = event.get("headers") or {}

    body = ""

    queue_name = queue_env_name[queue_env_name.find("_") + 1:].split()[0]
    timezone_offset = 2.0
    time = str(datetime.now(timezone(timedelta(hours=timezone_offset))))
    dedupid = re.sub(pattern=r'\W+', repl='', string=time)

    response = sqs.send_message(QueueUrl=queue_url, MessageBody=body, MessageGroupId=queue_name,
                                MessageDeduplicationId=dedupid)
    output = f'Publish response for body: {body} in group {queue_name} is: {response}'
    return {
        'statusCode': 200,
        'body': output
    }