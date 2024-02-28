import boto3
import re
from os import getenv
from ast import literal_eval
from time import time
from uuid import uuid4


def template(event, context):
    name = ""
    <start-time>
    <start-span>
    print("starting")

    sqs = boto3.client('sqs')
    queue_name, regex = getenv('QUEUE_NAME'), getenv('REGEX')
    queue_url = getenv("SQS_DO_NOT_USE") if regex == "true" else getenv(f"SQS_{queue_name}")

    record = event.get("Records")[0]
    message = literal_eval(record.get('body'))
    print(f"Message from queue: {message}")
    parent_span = message.get('span') or {}
    receipt_handle = record.get('receiptHandle')

    if span is not None:
        span["span_depth"] = (parent_span.get('span_depth') or 0) + 1
        span["parent_span_id"] = parent_span.get('span_id')
        span["parent_name"] = parent_span.get('name')

    body = ""

    # Delete received message from queue
    print('Deleting message...')
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle,
    )
    print('Message deleted.')
    <end-time>

    if span is not None:
        <end-span>
        print(f"span: {span}")
