import boto3
import re
from os import getenv


def template(event, context):
    print("starting")
    sqs = boto3.client('sqs')
    queue_name = getenv('QUEUE_NAME')
    queue_url = getenv(f"SQS_{queue_name}")

    record = event.get("Records")[0]
    message = record.get('body')
    receipt_handle = record.get('receiptHandle')

    body = ""

    # Delete received message from queue
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle,
    )
    print('Received and deleted message: %s' % record)
    print(f"body: {body}")
