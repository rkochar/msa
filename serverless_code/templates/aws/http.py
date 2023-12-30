import json
import boto3
from os import getenv
import re
from time import time


def template(event, context):
    start_time = time()
    query_parameters = event.get("queryStringParameters") or {}
    headers = event.get("headers") or {}

    body = ""

    return {
        "statusCode": 200,
        "body": json.dumps({"body": body, "execution_time": str(time() - start_time)})
    }
