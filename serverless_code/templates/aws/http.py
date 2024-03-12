import json
import boto3
from os import getenv
import re
from time import time
from uuid import uuid4
import resource


def template(event, context):
    name = ""
    <start-time>
    <start-span>
    query_parameters, headers = event.get("queryStringParameters") or {}, event.get("headers") or {}

    body = ""

    <end-time>
    <end-span>

    return {
        "statusCode": 200,
        "body": json.dumps({"body": body,})
    }
