import json
import boto3
from os import getenv
import re


def template(event, context):
    query_parameters = event.get("queryStringParameters") or {}
    headers = event.get("headers") or {}

    body = ""

    return {
        "statusCode": 200,
        "body": json.dumps(body)
    }
